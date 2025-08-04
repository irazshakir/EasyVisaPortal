"""
Main chat service that orchestrates FSM, OpenAI, and session management
"""
from typing import Dict, Any, Optional
from loguru import logger

from app.services.fsm_service import fsm_service
from app.services.openai_service import OpenAIService
from app.services.session_service import SessionService
from app.models.chat import ChatResponse


class ChatService:
    """Main chat service for bot interactions"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.session_service = SessionService()
    
    async def process_message(
        self,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Process user message and generate response"""
        try:
            # Get current FSM state
            state_info = await fsm_service.get_current_state(session_id)
            current_state = state_info['current_state']
            
            # Analyze user intent
            intent_analysis = await self.openai_service.analyze_intent(message)
            
            # Store message in session history
            await self.session_service.add_message(session_id, "user", message)
            
            # Generate response based on current state and intent
            response_message = await self._generate_state_response(
                session_id, current_state, message, intent_analysis, context
            )
            
            # Store bot response in session history
            await self.session_service.add_message(session_id, "assistant", response_message)
            
            # Update session activity
            await self.session_service.update_activity(session_id)
            
            return ChatResponse(
                session_id=session_id,
                message=response_message,
                state=current_state,
                metadata={
                    "intent": intent_analysis,
                    "context": state_info['context']
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                session_id=session_id,
                message="I apologize, but I encountered an error. Please try again.",
                state="error",
                metadata={"error": str(e)}
            )
    
    async def _generate_state_response(
        self,
        session_id: str,
        current_state: str,
        user_message: str,
        intent_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate response based on current state"""
        
        # Get conversation history
        history = await self.session_service.get_chat_history(session_id)
        messages = [{"role": msg.role, "content": msg.content} for msg in history[-5:]]  # Last 5 messages
        
        # State-specific system prompts
        system_prompts = {
            "greeting": """You are a helpful visa application assistant. Welcome the user warmly and ask how you can help them with their visa application process.""",
            
            "collecting_info": """You are collecting basic information for visa application. Ask for:
            - Full name
            - Nationality
            - Purpose of travel
            - Destination country
            - Travel dates
            Be friendly and professional.""",
            
            "visa_type_selection": """Help the user select the appropriate visa type based on their information. 
            Common types: Tourist, Business, Student, Work, Transit.
            Explain requirements for each type briefly.""",
            
            "document_upload": """Guide the user through document upload process. 
            Explain what documents are required and how to upload them.
            Common documents: Passport, Photos, Financial statements, Travel itinerary.""",
            
            "application_review": """Review the application with the user. 
            Summarize the information collected and ask for confirmation.
            Mention any missing documents or information.""",
            
            "payment": """Guide the user through payment process.
            Explain the fees and payment methods available.
            Be clear about what the payment covers.""",
            
            "confirmation": """Confirm the application submission.
            Provide next steps and timeline.
            Thank the user for using the service.""",
            
            "help": """Provide helpful information about the visa application process.
            Answer common questions and guide users back to the main flow.""",
            
            "error": """Apologize for the error and help the user get back on track.
            Offer to restart the process or provide help."""
        }
        
        system_prompt = system_prompts.get(current_state, system_prompts["greeting"])
        
        # Add state context to system prompt
        state_context = await fsm_service.get_current_state(session_id)
        if state_context['context']:
            context_info = f"Current context: {state_context['context']}"
            system_prompt += f"\n\n{context_info}"
        
        # Generate response using OpenAI
        response = await self.openai_service.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            context=context
        )
        
        # Handle state transitions based on intent
        await self._handle_state_transition(session_id, current_state, intent_analysis, user_message)
        
        return response
    
    async def _handle_state_transition(
        self,
        session_id: str,
        current_state: str,
        intent_analysis: Dict[str, Any],
        user_message: str
    ):
        """Handle state transitions based on intent and current state"""
        
        intent = intent_analysis.get("intent", "unknown")
        confidence = intent_analysis.get("confidence", 0.0)
        
        # Only transition if confidence is high enough
        if confidence < 0.7:
            return
        
        # State-specific transition logic
        if current_state == "greeting":
            if intent in ["visa_info", "document_upload", "application_status"]:
                await fsm_service.transition(session_id, "start")
        
        elif current_state == "collecting_info":
            # Check if we have enough information
            state_info = await fsm_service.get_current_state(session_id)
            context = state_info['context']
            
            required_fields = ["full_name", "nationality", "purpose", "destination", "travel_dates"]
            if all(field in context for field in required_fields):
                await fsm_service.transition(session_id, "info_complete")
        
        elif current_state == "visa_type_selection":
            if "visa_type" in intent_analysis.get("entities", {}):
                visa_type = intent_analysis["entities"]["visa_type"]
                await fsm_service.transition(session_id, "type_selected", visa_type=visa_type)
        
        elif current_state == "document_upload":
            if intent == "document_upload":
                await fsm_service.transition(session_id, "documents_uploaded")
        
        elif current_state == "application_review":
            if "confirm" in user_message.lower() or "yes" in user_message.lower():
                await fsm_service.transition(session_id, "review_approved")
            elif "no" in user_message.lower() or "change" in user_message.lower():
                await fsm_service.transition(session_id, "review_rejected")
        
        elif current_state == "payment":
            if "payment_complete" in user_message.lower() or "paid" in user_message.lower():
                await fsm_service.transition(session_id, "payment_complete")
        
        # Handle help requests from any state
        if intent == "help":
            await fsm_service.transition(session_id, "help_request")
        
        # Handle restart requests
        if intent == "goodbye" or "restart" in user_message.lower():
            await fsm_service.transition(session_id, "restart") 
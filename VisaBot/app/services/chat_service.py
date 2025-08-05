"""
Chat service for visa evaluation bot - integrates FSM, OpenAI, and session services
"""
from typing import Dict, Any, Optional
from loguru import logger

from app.services.fsm_service import fsm_service, FSMStates
from app.services.openai_service import openai_service
from app.services.session_service import session_service
from app.models.chat import ChatRequest, ChatResponse


class ChatService:
    """Main chat service for visa evaluation bot"""
    
    def __init__(self):
        self.openai_service = openai_service
    
    async def process_chat_message(self, chat_request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return appropriate response
        This is the main entry point for the visa evaluation bot
        """
        try:
            # Get or create session
            session_id, session_data = await session_service.get_or_create_session(chat_request.session_id)
            
            # Get current FSM state from FSM service (single source of truth)
            fsm_state_info = await fsm_service.get_current_state(session_id)
            current_state = FSMStates(fsm_state_info["current_state"])
            logger.info(f"Chat service - Session {session_id} - Current state: {current_state.value}")
            logger.info(f"Chat service - FSM state info: {fsm_state_info}")
            logger.info(f"Chat service - FSM answers: {fsm_state_info.get('answers', {})}")
            
            # Check if this is the very first message in the conversation
            chat_history = await session_service.get_chat_history(session_id)
            is_first_message = len(chat_history) == 0
            
            # If this is the first message, send the initial question
            if is_first_message:
                # Get the initial question from FSM
                fsm = await fsm_service.get_fsm(session_id)
                initial_question = fsm.get_current_question()
                
                # Add assistant message to history
                await session_service.add_message(session_id, "assistant", initial_question)
                
                return ChatResponse(
                    session_id=session_id,
                    message=initial_question,
                    state=current_state.value,
                    metadata={"is_initial": True}
                )
            
            # Add user message to history
            await session_service.add_message(session_id, "user", chat_request.message)
            
            # Process the message based on current state
            if current_state == FSMStates.COMPLETE:
                # Session is complete, offer to restart
                response_message = "Your visa evaluation is complete. Would you like to start a new evaluation?"
                await session_service.add_message(session_id, "assistant", response_message)
                
                return ChatResponse(
                    session_id=session_id,
                    message=response_message,
                    state=current_state.value,
                    metadata={"is_complete": True}
                )
            
            # Parse user input using OpenAI
            parsed_input = await self.openai_service.parse_user_input(current_state, chat_request.message)
            
            # Process with FSM
            logger.info(f"Processing user input for session {session_id} in state {current_state.value}")
            fsm_result = await fsm_service.process_user_input(session_id, chat_request.message)
            logger.info(f"FSM result: {fsm_result}")
            
            # Update session with new state and parsed data
            next_state = FSMStates(fsm_result["current_state"])
            logger.info(f"Chat service - Moving to next state: {next_state.value}")
            
            # Update session service to keep it in sync with FSM
            await session_service.update_session(session_id, next_state, fsm_result["answers"])
            
            # Use FSM question/response - DO NOT generate with OpenAI
            response_message = fsm_result["question"]
            logger.info(f"Using FSM response: {response_message}")
            
            # Add assistant message to history
            await session_service.add_message(session_id, "assistant", response_message)
            
            return ChatResponse(
                session_id=session_id,
                message=response_message,
                state=next_state.value,
                metadata={
                    "parsed_input": parsed_input,
                    "is_complete": fsm_result["is_complete"],
                    "answers": fsm_result["answers"]
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            
            # Return error response
            error_message = "I apologize, but I encountered an error processing your request. Please try again."
            
            if chat_request.session_id:
                await session_service.add_message(chat_request.session_id, "assistant", error_message)
            
            return ChatResponse(
                session_id=chat_request.session_id or "error",
                message=error_message,
                state="error",
                metadata={"error": str(e)}
            )
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status and progress"""
        try:
            session_data = await session_service.get_session(session_id)
            if not session_data:
                return {"error": "Session not found"}
            
            current_state = session_service.get_session_state(session_id)
            answers = session_service.get_session_answers(session_id)
            
            # Calculate progress
            state_order = [
                FSMStates.ASK_PROFESSION,
                FSMStates.ASK_TAX_INFO,
                FSMStates.ASK_BALANCE,
                FSMStates.ASK_TRAVEL,
                FSMStates.EVALUATION,
                FSMStates.COMPLETE
            ]
            
            try:
                progress = (state_order.index(current_state) + 1) / len(state_order) * 100
            except ValueError:
                progress = 0
            
            return {
                "session_id": session_id,
                "current_state": current_state.value if current_state else "unknown",
                "progress": progress,
                "answers": answers,
                "is_complete": current_state == FSMStates.COMPLETE,
                "last_activity": session_data["last_activity"]
            }
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {"error": str(e)}
    
    async def reset_session(self, session_id: str) -> Dict[str, Any]:
        """Reset a session to start over"""
        try:
            await session_service.reset_session(session_id)
            await fsm_service.reset_session(session_id)
            
            return {
                "session_id": session_id,
                "message": "Session reset successfully. You can start a new visa evaluation.",
                "state": FSMStates.ASK_PROFESSION.value
            }
            
        except Exception as e:
            logger.error(f"Error resetting session: {e}")
            return {"error": str(e)}
    
    async def get_evaluation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get evaluation summary for completed sessions"""
        try:
            session_data = await session_service.get_session(session_id)
            if not session_data:
                return {"error": "Session not found"}
            
            current_state = session_service.get_session_state(session_id)
            if current_state != FSMStates.COMPLETE:
                return {"error": "Evaluation not complete"}
            
            answers = session_service.get_session_answers(session_id)
            evaluation = answers.get("evaluation", {})
            
            return {
                "session_id": session_id,
                "evaluation": evaluation,
                "answers": answers,
                "summary": {
                    "eligible": evaluation.get("eligible", False),
                    "score": evaluation.get("score", 0),
                    "confidence": evaluation.get("confidence", 0),
                    "recommendations": evaluation.get("recommendations", []),
                    "risk_factors": evaluation.get("risk_factors", []),
                    "next_steps": evaluation.get("next_steps", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting evaluation summary: {e}")
            return {"error": str(e)}
    
    async def list_active_sessions(self) -> Dict[str, Any]:
        """List all active sessions"""
        try:
            sessions = await session_service.list_sessions()
            return {
                "sessions": sessions,
                "count": len(sessions)
            }
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return {"error": str(e)}


# Global chat service instance
chat_service = ChatService() 
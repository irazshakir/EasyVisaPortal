"""
OpenAI service for LLM interactions
"""
import tiktoken
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings


class OpenAIService:
    """OpenAI service for LLM interactions"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        self.encoding = tiktoken.encoding_for_model(self.model)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def truncate_messages(self, messages: List[Dict[str, str]], max_tokens: int = None) -> List[Dict[str, str]]:
        """Truncate messages to fit within token limit"""
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        total_tokens = 0
        truncated_messages = []
        
        # Start from the most recent messages
        for message in reversed(messages):
            message_tokens = self.count_tokens(message["content"])
            if total_tokens + message_tokens <= max_tokens:
                truncated_messages.insert(0, message)
                total_tokens += message_tokens
            else:
                break
        
        return truncated_messages
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        """Generate response using OpenAI API"""
        try:
            # Prepare messages
            api_messages = []
            
            # Add system prompt if provided
            if system_prompt:
                api_messages.append({"role": "system", "content": system_prompt})
            
            # Add context if provided
            if context:
                context_message = f"Context: {str(context)}"
                api_messages.append({"role": "system", "content": context_message})
            
            # Add conversation messages
            api_messages.extend(messages)
            
            # Truncate messages if needed
            api_messages = self.truncate_messages(api_messages)
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent from message"""
        system_prompt = """
        Analyze the user's intent and extract relevant information for visa application.
        Return a JSON object with the following structure:
        {
            "intent": "greeting|visa_info|document_upload|application_status|help|goodbye",
            "confidence": 0.0-1.0,
            "entities": {
                "visa_type": "tourist|business|student|work|other",
                "country": "destination country",
                "urgency": "low|medium|high"
            },
            "requires_action": true|false,
            "next_state": "suggested_next_state"
        }
        """
        
        try:
            response = await self.generate_response(
                messages=[{"role": "user", "content": message}],
                system_prompt=system_prompt
            )
            
            # Parse JSON response
            import json
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
                "requires_action": False,
                "next_state": "greeting"
            }
    
    async def parse_user_input(self, state: str, user_input: str) -> Dict[str, Any]:
        """Parse user input based on current state"""
        try:
            # For now, return a simple parsed structure
            # In a real implementation, this would use more sophisticated NLP
            return {
                "raw_input": user_input,
                "parsed_data": user_input.lower(),
                "confidence": 0.8,
                "state": state
            }
        except Exception as e:
            logger.error(f"Error parsing user input: {e}")
            return {
                "raw_input": user_input,
                "parsed_data": user_input,
                "confidence": 0.5,
                "state": state
            }
    
    async def generate_response_for_state(
        self, 
        state: str, 
        user_input: str, 
        context: Dict[str, Any] = None
    ) -> str:
        """Generate contextual response for specific state"""
        try:
            # Define state-specific prompts
            state_prompts = {
                "ask_profession": "You are a visa assistant. Ask the user about their profession in a friendly way.",
                "ask_tax_info": "You are a visa assistant. Ask the user about their tax filing status and income.",
                "ask_balance": "You are a visa assistant. Ask the user about their ability to maintain a closing balance.",
                "ask_travel": "You are a visa assistant. Ask the user about their travel history.",
                "evaluation": "You are a visa assistant. Provide a professional evaluation response.",
                "complete": "You are a visa assistant. Thank the user and provide next steps."
            }
            
            system_prompt = state_prompts.get(state, "You are a helpful visa assistant.")
            
            # Add context to the prompt
            if context:
                context_str = f"Context: {str(context)}"
                system_prompt += f"\n\n{context_str}"
            
            response = await self.generate_response(
                messages=[{"role": "user", "content": user_input}],
                system_prompt=system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response for state: {e}")
            # Fallback responses
            fallback_responses = {
                "ask_profession": "Could you please tell me about your profession? Are you a business person or job holder?",
                "ask_tax_info": "Are you a tax filer? If yes, what was your annual income in the last tax return?",
                "ask_balance": "Can you manage a closing balance of 2 million PKR?",
                "ask_travel": "What is your previous travel history in the last 5 years?",
                "evaluation": "Thank you for providing your information. I'm processing your visa evaluation.",
                "complete": "Thank you for using our visa evaluation service!"
            }
            
            return fallback_responses.get(state, "Thank you for your response. Please continue with the visa evaluation process.")


# Global OpenAI service instance
openai_service = OpenAIService() 
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
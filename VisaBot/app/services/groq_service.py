"""
Groq service for LLM interactions
"""
import tiktoken
from typing import List, Dict, Any, Optional
from groq import AsyncGroq
from loguru import logger

from app.core.config import settings


class GroqService:
    """Groq service for LLM interactions"""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.default_model = settings.GROQ_DEFAULT_MODEL
        self.evaluation_model = settings.GROQ_EVALUATION_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.temperature = settings.GROQ_TEMPERATURE
        # Use tiktoken for token counting (works with Groq models)
        self.encoding = tiktoken.encoding_for_model("gpt-4")  # Fallback encoding
    
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
        context: Dict[str, Any] = None,
        use_evaluation_model: bool = False
    ) -> str:
        """Generate response using Groq API"""
        try:
            # Choose model based on use case
            model = self.evaluation_model if use_evaluation_model else self.default_model
            
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
                model=model,
                messages=api_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
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
        """Enhanced parsing of user input to extract structured information"""
        try:
            # Create a comprehensive system prompt for information extraction
            system_prompt = """
            You are an AI assistant that extracts structured information from visa-related conversations.
            
            Extract ALL relevant information from the user's message and return it in JSON format.
            Look for information about:
            
            1. **Country**: Target country for visa application (e.g., France, Germany, USA, Canada, etc.)
            2. **Profession**: Employment status (business person, job holder, employed, unemployed, student, etc.)
            3. **Business Type**: If business person, extract business type (sole proprietor, private limited company, etc.)
            4. **Salary**: If job holder, extract salary amount
            5. **Salary Mode**: If job holder, extract how salary is received (bank transfer, cash, etc.)
            6. **Tax Information**: Tax filing status and income amounts
            7. **Financial Capacity**: Bank balance, savings, financial ability (especially 2M PKR requirement)
            8. **Travel History**: Previous travel experience, countries visited, etc.
            
            Return a JSON object with this structure:
            {
                "extracted_info": {
                    "country": {"value": "country_name", "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "profession": {"value": "profession_type", "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "business_type": {"value": "business_type", "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "salary": {"value": "salary_amount", "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "salary_mode": {"value": "salary_mode", "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "tax_filer": {"value": true/false/null, "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "annual_income": {"value": number/null, "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "closing_balance": {"value": number/null, "confidence": 0.0-1.0, "source": "explicit/implicit"},
                    "travel_history": {"value": "description", "confidence": 0.0-1.0, "source": "explicit/implicit"}
                },
                "overall_confidence": 0.0-1.0,
                "questions_answered": ["country", "profession", "business_type", "salary", "salary_mode", "tax_info", "balance", "travel"],
                "raw_input": "original_user_input"
            }
            
            Rules:
            - Set confidence to 0.0 if information is not mentioned
            - Set confidence to 0.5-0.7 if information is implied
            - Set confidence to 0.8-1.0 if information is explicitly stated
            - For numbers, extract the actual value (e.g., "2 million" -> 2000000)
            - For countries, use standard names (e.g., "USA" -> "United States")
            - For business types, identify: "sole proprietor", "private limited company", etc.
            - For salary modes, identify: "bank transfer", "cash", etc.
            - IMPORTANT: Distinguish between target country and travel history countries:
              * Target country: The country they want to apply visa for (usually mentioned first or in context of "apply for", "visa for", etc.)
              * Travel history: Countries they have visited in the past (usually mentioned in context of "visited", "been to", "traveled to", etc.)
            - For travel history, handle both positive and negative responses:
              * Positive: "Dubai, Sri Lanka, Saudi Arabia" -> ["Dubai", "Sri Lanka", "Saudi Arabia"]
              * Negative: "no travel", "none", "never traveled" -> []
            - Only include questions_answered for information that is clearly provided
            """
            
            # Get structured response from Groq
            response = await self.generate_response(
                messages=[{"role": "user", "content": user_input}],
                system_prompt=system_prompt
            )
            
            # Parse the JSON response
            import json
            try:
                parsed_data = json.loads(response)
                logger.info(f"Parsed user input: {parsed_data}")
                return parsed_data
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {response}")
                # Fallback to basic parsing
                return self._fallback_parse(user_input, state)
                
        except Exception as e:
            logger.error(f"Error in enhanced parsing: {e}")
            return self._fallback_parse(user_input, state)

    def _fallback_parse(self, user_input: str, state: str) -> Dict[str, Any]:
        """Fallback parsing when Groq parsing fails"""
        input_lower = user_input.lower()
        
        # Basic keyword-based extraction
        extracted_info = {
            "country": {"value": None, "confidence": 0.0, "source": "none"},
            "profession": {"value": None, "confidence": 0.0, "source": "none"},
            "business_type": {"value": None, "confidence": 0.0, "source": "none"},
            "salary": {"value": None, "confidence": 0.0, "source": "none"},
            "salary_mode": {"value": None, "confidence": 0.0, "source": "none"},
            "tax_filer": {"value": None, "confidence": 0.0, "source": "none"},
            "annual_income": {"value": None, "confidence": 0.0, "source": "none"},
            "closing_balance": {"value": None, "confidence": 0.0, "source": "none"},
            "travel_history": {"value": None, "confidence": 0.0, "source": "none"}
        }
        
        questions_answered = []
        
        # Basic country detection - distinguish between target country and travel history
        countries = {
            "france", "germany", "italy", "spain", "netherlands", "belgium", "austria", 
            "switzerland", "denmark", "norway", "sweden", "finland", "poland", "czech", 
            "hungary", "slovakia", "slovenia", "croatia", "greece", "portugal", "ireland",
            "usa", "united states", "america", "canada", "uk", "united kingdom", 
            "australia", "new zealand"
        }
        
        # Check for target country (usually mentioned in context of visa application)
        target_country_keywords = ["apply", "visa", "want", "interested", "planning", "going"]
        for country in countries:
            if country in input_lower:
                # Check if this is likely a target country (not travel history)
                is_target_country = any(keyword in input_lower for keyword in target_country_keywords)
                if is_target_country:
                    extracted_info["country"] = {
                        "value": country.title(),
                        "confidence": 0.8,
                        "source": "explicit"
                    }
                    questions_answered.append("country")
                    break
        
        # Basic profession detection
        if any(word in input_lower for word in ["business", "owner", "entrepreneur"]):
            extracted_info["profession"] = {
                "value": "business person",
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("profession")
        elif any(word in input_lower for word in ["job", "employed", "employee", "worker"]):
            extracted_info["profession"] = {
                "value": "job holder",
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("profession")
        
        # Basic business type detection
        if any(word in input_lower for word in ["sole", "proprietor", "individual"]):
            extracted_info["business_type"] = {
                "value": "sole proprietor",
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("business_type")
        elif any(word in input_lower for word in ["private", "limited", "pvt", "company"]):
            extracted_info["business_type"] = {
                "value": "private limited company",
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("business_type")
        
        # Basic salary mode detection
        if any(word in input_lower for word in ["bank", "account", "transfer", "deposit"]):
            extracted_info["salary_mode"] = {
                "value": "bank transfer",
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("salary_mode")
        elif any(word in input_lower for word in ["cash", "hand"]):
            extracted_info["salary_mode"] = {
                "value": "cash",
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("salary_mode")
        
        # Basic financial detection
        if "2 million" in input_lower or "2m" in input_lower or "2000000" in input_lower:
            extracted_info["closing_balance"] = {
                "value": 2000000,
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("balance")
        
        # Basic travel history detection
        travel_history_keywords = ["visited", "been to", "traveled to", "went to", "travel history", "previous travel", "last 5 years"]
        negative_travel_keywords = ["no", "none", "never", "no history", "no travel", "no travel history", "never traveled", "no international travel"]
        
        if any(phrase in input_lower for phrase in negative_travel_keywords):
            extracted_info["travel_history"] = {
                "value": [],
                "confidence": 0.8,
                "source": "explicit"
            }
            questions_answered.append("travel")
        elif any(phrase in input_lower for phrase in travel_history_keywords):
            # Try to extract countries from travel history
            travel_countries = []
            country_keywords = [
                "dubai", "uae", "saudi arabia", "saudia", "sri lanka", "srilanka", 
                "thailand", "malaysia", "singapore", "turkey", "qatar", "kuwait", 
                "oman", "bahrain", "jordan", "lebanon", "egypt", "morocco", "tunisia",
                "china", "japan", "south korea", "india", "pakistan", "bangladesh",
                "nepal", "bhutan", "maldives", "afghanistan", "iran", "iraq", "syria",
                "usa", "united states", "america", "canada", "uk", "united kingdom",
                "australia", "new zealand", "france", "germany", "italy", "spain",
                "netherlands", "belgium", "austria", "switzerland", "denmark", "norway",
                "sweden", "finland", "poland", "czech", "hungary", "slovakia", "slovenia",
                "croatia", "greece", "portugal", "ireland"
            ]
            
            for country in country_keywords:
                if country in input_lower:
                    travel_countries.append(country.title())
            
            if travel_countries:
                extracted_info["travel_history"] = {
                    "value": travel_countries,
                    "confidence": 0.8,
                    "source": "explicit"
                }
                questions_answered.append("travel")
        
        return {
            "extracted_info": extracted_info,
            "overall_confidence": 0.6,
            "questions_answered": questions_answered,
            "raw_input": user_input
        }

    async def extract_visa_information(self, user_input: str) -> Dict[str, Any]:
        """
        Extract all relevant visa information from user input
        This is a wrapper around parse_user_input for easier integration
        """
        return await self.parse_user_input("any", user_input)
    
    async def generate_response_for_state(
        self, 
        state: str, 
        user_input: str, 
        context: Dict[str, Any] = None,
        use_evaluation_model: bool = False
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
                system_prompt=system_prompt,
                use_evaluation_model=use_evaluation_model
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

    async def generate_final_evaluation(self, user_data: Dict[str, Any]) -> str:
        """Generate final visa evaluation using the evaluation model"""
        try:
            system_prompt = """
            You are an expert visa evaluation assistant. Based on the provided user information, 
            provide a comprehensive visa evaluation with the following structure:
            
            1. **Overall Assessment**: Brief summary of eligibility
            2. **Strengths**: Positive factors supporting the application
            3. **Concerns**: Potential issues or areas of concern
            4. **Recommendations**: Specific advice for improving the application
            5. **Next Steps**: Clear guidance on what to do next
            
            Be professional, objective, and constructive in your evaluation.
            """
            
            user_info_str = f"User Information: {str(user_data)}"
            
            response = await self.generate_response(
                messages=[{"role": "user", "content": user_info_str}],
                system_prompt=system_prompt,
                use_evaluation_model=True  # Use the evaluation model for final assessments
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating final evaluation: {e}")
            return "I apologize, but I'm unable to generate a complete evaluation at this time. Please try again later."


# Global Groq service instance
groq_service = GroqService() 
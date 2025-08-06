"""
RAG (Retrieval Augmented Generation) service for visa evaluation bot
Handles off-track questions and complex evaluation scenarios
"""
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from app.services.openai_service import openai_service
from app.core.config import settings


@dataclass
class FAQEntry:
    """FAQ entry structure"""
    question: str
    answer: str
    category: str
    keywords: List[str]
    confidence: float = 1.0


@dataclass
class RAGResponse:
    """RAG response structure"""
    answer: str
    confidence: float
    source: str
    should_return_to_fsm: bool
    transition_message: str = ""
    context_for_fsm: Dict[str, Any] = None


class RAGService:
    """RAG service for handling off-track questions and complex evaluations"""
    
    def __init__(self):
        self.openai_service = openai_service
        self.faq_database = self._initialize_faq_database()
        self.evaluation_rules = self._initialize_evaluation_rules()
        
    def _initialize_faq_database(self) -> List[FAQEntry]:
        """Initialize FAQ database with visa-related information"""
        return [
            # Country-specific information
            FAQEntry(
                question="Which Schengen country has the highest visa approval rate?",
                answer="Germany typically has the highest approval rate for Schengen visas, followed by France and Italy. However, approval rates vary based on individual circumstances, documentation quality, and the specific embassy's current policies.",
                category="country_selection",
                keywords=["best country", "highest approval", "success rate", "which country", "approval rate", "good country"]
            ),
            FAQEntry(
                question="What are the visa fees for Schengen countries?",
                answer="Schengen visa fees are standardized: €90 for adults, €40 for children (6-12 years), and free for children under 6. Some categories like students, researchers, and family members may have reduced or waived fees.",
                category="fees",
                keywords=["cost", "fee", "price", "how much", "visa fee", "application cost"]
            ),
            FAQEntry(
                question="How long does visa processing take?",
                answer="Standard Schengen visa processing takes 15 calendar days, but can extend up to 30 days in some cases. During peak seasons (summer, holidays), processing may take longer. It's recommended to apply at least 3-4 weeks before travel.",
                category="processing_time",
                keywords=["how long", "processing time", "duration", "when", "timeline", "waiting time"]
            ),
            FAQEntry(
                question="What documents are required for Schengen visa?",
                answer="Required documents include: valid passport (3 months validity beyond stay), visa application form, recent photos, travel insurance, flight itinerary, accommodation proof, financial statements, employment letter, and travel purpose documentation.",
                category="documents",
                keywords=["documents", "requirements", "what needed", "papers", "documentation", "checklist"]
            ),
            FAQEntry(
                question="What is the minimum bank balance for Schengen visa?",
                answer="There's no fixed minimum, but generally €50-100 per day of stay is recommended. For a 10-day trip, €500-1000 should be sufficient. The amount varies by country and individual circumstances.",
                category="financial_requirements",
                keywords=["bank balance", "minimum amount", "money required", "financial proof", "bank statement"]
            ),
            FAQEntry(
                question="Can I apply for multiple Schengen visas?",
                answer="Yes, you can apply for multiple Schengen visas. However, you must apply to the country where you'll spend the most time, or the first country you'll enter if staying equal time in multiple countries.",
                category="application_rules",
                keywords=["multiple visas", "several countries", "more than one", "different countries"]
            ),
            FAQEntry(
                question="What if my visa is rejected?",
                answer="If rejected, you can appeal within 30 days. Common reasons include insufficient funds, unclear travel purpose, or incomplete documentation. You can reapply after addressing the issues mentioned in the rejection letter.",
                category="rejection",
                keywords=["rejected", "denied", "refused", "what if", "appeal", "rejection"]
            ),
            FAQEntry(
                question="Do I need travel insurance for Schengen visa?",
                answer="Yes, travel insurance is mandatory for Schengen visas. It must cover at least €30,000 for medical expenses and repatriation, and be valid for the entire duration of your stay in the Schengen area.",
                category="insurance",
                keywords=["travel insurance", "medical insurance", "insurance required", "health coverage"]
            ),
            FAQEntry(
                question="What are the best months to apply for Schengen visa?",
                answer="Apply 3-4 months before travel, avoiding peak seasons (May-August, December). January-March and September-November typically have faster processing times. Avoid applying during major holidays.",
                category="timing",
                keywords=["best time", "when to apply", "timing", "months", "season", "peak time"]
            ),
            FAQEntry(
                question="Can I work on a Schengen tourist visa?",
                answer="No, tourist visas are strictly for tourism, family visits, or business meetings. Working, studying, or conducting business activities requires specific visa types. Violating visa terms can result in future rejections.",
                category="visa_types",
                keywords=["work", "job", "employment", "business", "study", "student"]
            ),
        ]
    
    def _initialize_evaluation_rules(self) -> Dict[str, Any]:
        """Initialize complex evaluation rules for RAG-based assessment"""
        return {
            "high_risk_factors": [
                "no travel history",
                "low income",
                "no tax filing",
                "insufficient bank balance",
                "unclear travel purpose",
                "recent visa rejections"
            ],
            "positive_factors": [
                "extensive travel history",
                "high income",
                "regular tax filing",
                "substantial bank balance",
                "clear travel purpose",
                "previous visa approvals"
            ],
            "country_specific_rules": {
                "germany": {
                    "preferred_professions": ["engineers", "doctors", "business owners"],
                    "financial_requirements": "higher than average",
                    "documentation_standards": "very strict"
                },
                "france": {
                    "preferred_professions": ["tourism", "business", "family visits"],
                    "financial_requirements": "moderate",
                    "documentation_standards": "standard"
                },
                "italy": {
                    "preferred_professions": ["tourism", "business", "cultural visits"],
                    "financial_requirements": "moderate",
                    "documentation_standards": "standard"
                }
            }
        }
    
    async def handle_off_track_question(self, user_input: str, current_fsm_state: str, user_context: Dict[str, Any] = None) -> RAGResponse:
        """
        Handle off-track questions using RAG
        Returns appropriate response and whether to return to FSM
        """
        try:
            # Analyze if this is an off-track question
            is_off_track, question_type = self._classify_question(user_input, current_fsm_state)
            
            if not is_off_track:
                return RAGResponse(
                    answer="",
                    confidence=0.0,
                    source="not_off_track",
                    should_return_to_fsm=True
                )
            
            # Search for relevant FAQ
            best_match = await self._search_faq(user_input, question_type)
            
            if best_match and best_match.confidence > 0.7:
                # Generate contextual response
                response = await self._generate_contextual_response(
                    user_input, best_match, current_fsm_state, user_context
                )
                
                return RAGResponse(
                    answer=response["answer"],
                    confidence=best_match.confidence,
                    source="faq",
                    should_return_to_fsm=response["return_to_fsm"],
                    transition_message=response["transition_message"],
                    context_for_fsm=response.get("context", {})
                )
            
            # If no good FAQ match, use LLM to generate response
            llm_response = await self._generate_llm_response(user_input, current_fsm_state, user_context)
            
            return RAGResponse(
                answer=llm_response["answer"],
                confidence=0.6,
                source="llm",
                should_return_to_fsm=llm_response["return_to_fsm"],
                transition_message=llm_response["transition_message"]
            )
            
        except Exception as e:
            logger.error(f"Error in handle_off_track_question: {e}")
            return RAGResponse(
                answer="I understand your question. Let me help you with that after we complete your evaluation. For now, let's continue with the assessment to provide you with accurate information.",
                confidence=0.5,
                source="fallback",
                should_return_to_fsm=True,
                transition_message="Now, let's continue with your evaluation:"
            )
    
    def _classify_question(self, user_input: str, current_fsm_state: str) -> Tuple[bool, str]:
        """Classify if question is off-track and determine its type"""
        input_lower = user_input.lower().strip()
        
        # FSM state-specific expected responses
        expected_responses = {
            "ask_country": ["country", "nation", "destination", "where"],
            "ask_profession": ["business", "job", "employee", "profession", "work"],
            "ask_business_type": ["sole", "proprietor", "private", "limited", "company"],
            "ask_salary": ["salary", "income", "earnings", "pay", "amount"],
            "ask_salary_mode": ["bank", "transfer", "cash", "payment", "mode"],
            "ask_tax_info": ["tax", "filer", "income", "annual", "return"],
            "ask_balance": ["balance", "bank", "money", "account", "funds"],
            "ask_travel": ["travel", "history", "countries", "visited", "trip"]
        }
        
        # Check if input matches expected response for current state
        if current_fsm_state in expected_responses:
            expected_keywords = expected_responses[current_fsm_state]
            if any(keyword in input_lower for keyword in expected_keywords):
                return False, "on_track"
        
        # Off-track question patterns
        off_track_patterns = {
            "general_info": ["what is", "how does", "can you tell", "explain", "information"],
            "country_selection": ["best country", "which country", "recommend", "suggest", "good country"],
            "fees": ["cost", "fee", "price", "how much", "charge"],
            "timing": ["how long", "when", "time", "duration", "processing"],
            "documents": ["documents", "papers", "requirements", "what needed"],
            "rejection": ["rejected", "denied", "refused", "appeal", "what if"],
            "general_help": ["help", "assist", "guide", "advice", "support"]
        }
        
        for question_type, patterns in off_track_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                return True, question_type
        
        return True, "general"
    
    async def _search_faq(self, user_input: str, question_type: str) -> Optional[FAQEntry]:
        """Search FAQ database for relevant answers"""
        input_lower = user_input.lower().strip()
        best_match = None
        best_score = 0
        
        for faq in self.faq_database:
            # Calculate relevance score
            score = 0
            
            # Keyword matching
            for keyword in faq.keywords:
                if keyword in input_lower:
                    score += 2
            
            # Category matching
            if faq.category == question_type:
                score += 1
            
            # Question similarity
            if any(word in faq.question.lower() for word in input_lower.split()):
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = faq
                best_match.confidence = min(score / 5.0, 1.0)  # Normalize confidence
        
        return best_match if best_score > 1 else None
    
    async def _generate_contextual_response(
        self, 
        user_input: str, 
        faq_match: FAQEntry, 
        current_fsm_state: str, 
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate contextual response that bridges FAQ answer and FSM return"""
        
        # Get current FSM question for context
        fsm_questions = {
            "ask_country": "Which Country visa are you interested to apply?",
            "ask_profession": "Are you a business person or job holder?",
            "ask_business_type": "Are you a sole proprietor or is it a Private Limited company?",
            "ask_salary": "What is your current salary?",
            "ask_salary_mode": "Is your salary transferred to your bank account or do you receive it in cash?",
            "ask_tax_info": "Are you a tax filer? If yes, what was your annual income in the last tax return?",
            "ask_balance": "Can you manage a closing balance of 2 million PKR?",
            "ask_travel": "What is your previous travel history in the last 5 years?"
        }
        
        current_question = fsm_questions.get(current_fsm_state, "")
        
        # Generate transition message
        transition_templates = [
            "Thank you for that information. Now, let's continue with your evaluation:",
            "That's helpful to know. Let's proceed with your assessment:",
            "I understand. Now, let's get back to your evaluation:",
            "Good question! After we complete your evaluation, I can provide more detailed information. For now:",
            "That's a great point. Let's finish your evaluation first, then I can give you specific advice:"
        ]
        
        import random
        transition = random.choice(transition_templates)
        
        # Combine FAQ answer with transition
        full_response = f"{faq_match.answer}\n\n{transition}\n\n{current_question}"
        
        return {
            "answer": full_response,
            "return_to_fsm": True,
            "transition_message": transition,
            "context": {"faq_answered": faq_match.category}
        }
    
    async def _generate_llm_response(
        self, 
        user_input: str, 
        current_fsm_state: str, 
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate LLM response for off-track questions"""
        
        system_prompt = f"""
        You are a visa evaluation assistant. The user has asked an off-track question while in the middle of their visa evaluation.
        
        Current FSM state: {current_fsm_state}
        User context: {user_context or {}}
        
        Provide a helpful, accurate response to their question, then tactfully guide them back to the evaluation.
        Keep your response concise but informative.
        
        Format your response as:
        1. Answer their question
        2. A smooth transition back to the evaluation
        3. The current evaluation question they need to answer
        
        Be professional, helpful, and ensure they understand the importance of completing the evaluation first.
        """
        
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = await self.openai_service.generate_response(messages, system_prompt)
            
            # Extract transition message
            lines = response.split('\n')
            transition_message = ""
            for line in lines:
                if any(phrase in line.lower() for phrase in ["let's continue", "now", "let's proceed", "let's get back"]):
                    transition_message = line.strip()
                    break
            
            return {
                "answer": response,
                "return_to_fsm": True,
                "transition_message": transition_message or "Now, let's continue with your evaluation:"
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return {
                "answer": "I understand your question. Let me help you with that after we complete your evaluation. For now, let's continue with the assessment.",
                "return_to_fsm": True,
                "transition_message": "Now, let's continue with your evaluation:"
            }
    
    async def perform_rag_evaluation(self, user_answers: Dict[str, Any], target_country: str = None) -> Dict[str, Any]:
        """
        Perform RAG-based evaluation for complex decision making
        This supplements the FSM evaluation with more nuanced analysis
        """
        try:
            # Prepare context for LLM evaluation
            evaluation_context = {
                "user_answers": user_answers,
                "target_country": target_country,
                "evaluation_rules": self.evaluation_rules,
                "risk_factors": self._identify_risk_factors(user_answers),
                "positive_factors": self._identify_positive_factors(user_answers)
            }
            
            system_prompt = """
            You are an expert visa evaluation specialist. Analyze the user's profile and provide a comprehensive evaluation.
            
            Consider:
            1. Financial stability (income, tax filing, bank balance)
            2. Travel history and experience
            3. Professional background
            4. Country-specific requirements
            5. Risk factors and positive indicators
            
            Provide:
            1. Overall approval probability (0-100%)
            2. Key strengths
            3. Areas of concern
            4. Specific recommendations
            5. Required documents priority list
            6. Timeline recommendations
            
            Be realistic but encouraging. Focus on actionable advice.
            """
            
            # Create detailed profile description
            profile_description = self._create_profile_description(user_answers, target_country)
            
            messages = [
                {"role": "user", "content": f"Please evaluate this visa application profile:\n\n{profile_description}"}
            ]
            
            rag_evaluation = await self.openai_service.generate_response(messages, system_prompt, evaluation_context)
            
            # Parse the evaluation response
            parsed_evaluation = self._parse_evaluation_response(rag_evaluation)
            
            return {
                "rag_evaluation": rag_evaluation,
                "parsed_evaluation": parsed_evaluation,
                "risk_factors": evaluation_context["risk_factors"],
                "positive_factors": evaluation_context["positive_factors"],
                "recommendations": parsed_evaluation.get("recommendations", []),
                "confidence": parsed_evaluation.get("confidence", 0.7)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG evaluation: {e}")
            return {
                "rag_evaluation": "Unable to perform detailed evaluation at this time.",
                "parsed_evaluation": {},
                "risk_factors": [],
                "positive_factors": [],
                "recommendations": ["Please ensure all required documents are properly prepared."],
                "confidence": 0.5
            }
    
    def _identify_risk_factors(self, answers: Dict[str, Any]) -> List[str]:
        """Identify risk factors from user answers"""
        risk_factors = []
        
        # Financial risks
        salary = answers.get("salary", 0)
        if isinstance(salary, str):
            try:
                salary = int(salary.replace(',', '').replace(' ', ''))
            except:
                salary = 0
        
        if salary < 50000:  # Less than 50k PKR
            risk_factors.append("low_income")
        
        # Tax filing
        tax_info = answers.get("tax_info", "")
        if "no" in str(tax_info).lower():
            risk_factors.append("no_tax_filing")
        
        # Travel history
        travel_history = answers.get("travel_history", [])
        if not travel_history or (isinstance(travel_history, list) and len(travel_history) == 0):
            risk_factors.append("no_travel_history")
        
        # Bank balance
        balance = answers.get("closing_balance", "")
        if "no" in str(balance).lower():
            risk_factors.append("insufficient_balance")
        
        return risk_factors
    
    def _identify_positive_factors(self, answers: Dict[str, Any]) -> List[str]:
        """Identify positive factors from user answers"""
        positive_factors = []
        
        # High income
        salary = answers.get("salary", 0)
        if isinstance(salary, str):
            try:
                salary = int(salary.replace(',', '').replace(' ', ''))
            except:
                salary = 0
        
        if salary > 100000:  # More than 100k PKR
            positive_factors.append("high_income")
        
        # Tax filing
        tax_info = answers.get("tax_info", "")
        if "yes" in str(tax_info).lower():
            positive_factors.append("tax_filer")
        
        # Travel history
        travel_history = answers.get("travel_history", [])
        if travel_history and isinstance(travel_history, list) and len(travel_history) > 0:
            positive_factors.append("travel_history")
        
        # Bank balance
        balance = answers.get("closing_balance", "")
        if "yes" in str(balance).lower():
            positive_factors.append("sufficient_balance")
        
        return positive_factors
    
    def _create_profile_description(self, answers: Dict[str, Any], target_country: str = None) -> str:
        """Create a detailed profile description for evaluation"""
        profile_parts = []
        
        # Basic info
        if target_country:
            profile_parts.append(f"Target Country: {target_country}")
        
        # Profession
        profession = answers.get("profession", "")
        if profession:
            profile_parts.append(f"Profession: {profession}")
        
        # Business type
        business_type = answers.get("business_type", "")
        if business_type:
            profile_parts.append(f"Business Type: {business_type}")
        
        # Salary
        salary = answers.get("salary", "")
        if salary:
            profile_parts.append(f"Salary: {salary}")
        
        # Tax filing
        tax_info = answers.get("tax_info", "")
        if tax_info:
            profile_parts.append(f"Tax Filing: {tax_info}")
        
        # Travel history
        travel_history = answers.get("travel_history", [])
        if travel_history:
            if isinstance(travel_history, list):
                profile_parts.append(f"Travel History: {', '.join(travel_history)}")
            else:
                profile_parts.append(f"Travel History: {travel_history}")
        
        # Bank balance
        balance = answers.get("closing_balance", "")
        if balance:
            profile_parts.append(f"Bank Balance: {balance}")
        
        return "\n".join(profile_parts)
    
    def _parse_evaluation_response(self, evaluation_text: str) -> Dict[str, Any]:
        """Parse the LLM evaluation response into structured data"""
        try:
            # Extract key information using simple parsing
            lines = evaluation_text.split('\n')
            parsed = {
                "approval_probability": 0,
                "strengths": [],
                "concerns": [],
                "recommendations": [],
                "confidence": 0.7
            }
            
            for line in lines:
                line_lower = line.lower()
                
                # Extract approval probability
                if "%" in line and any(word in line_lower for word in ["probability", "chance", "approval"]):
                    try:
                        import re
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            parsed["approval_probability"] = int(numbers[0])
                    except:
                        pass
                
                # Extract strengths
                if any(word in line_lower for word in ["strength", "positive", "good", "strong"]):
                    parsed["strengths"].append(line.strip())
                
                # Extract concerns
                if any(word in line_lower for word in ["concern", "risk", "weakness", "issue"]):
                    parsed["concerns"].append(line.strip())
                
                # Extract recommendations
                if any(word in line_lower for word in ["recommend", "suggest", "advise", "should"]):
                    parsed["recommendations"].append(line.strip())
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing evaluation response: {e}")
            return {
                "approval_probability": 0,
                "strengths": [],
                "concerns": [],
                "recommendations": ["Please ensure all documents are properly prepared."],
                "confidence": 0.5
            }


# Global RAG service instance
rag_service = RAGService() 
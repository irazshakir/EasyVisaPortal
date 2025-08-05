"""
FSM (Finite State Machine) service for visa evaluation bot
"""
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
from loguru import logger

from app.services.redis_service import redis_client


class FSMStates(Enum):
    """FSM States for visa evaluation"""
    GREETING = "greeting"
    ASK_COUNTRY = "ask_country"
    COUNTRY_NOT_SUPPORTED = "country_not_supported"
    ASK_PROFESSION = "ask_profession"
    ASK_BUSINESS_TYPE = "ask_business_type"  # New state for business type
    ASK_SALARY = "ask_salary"  # New state for job holder salary
    ASK_SALARY_MODE = "ask_salary_mode"  # New state for salary transfer mode
    ASK_TAX_INFO = "ask_tax_info"
    ASK_BALANCE = "ask_balance"
    ASK_TRAVEL = "ask_travel"
    EVALUATION = "evaluation"
    COMPLETE = "complete"


class VisaEvaluationFSM:
    """Finite State Machine for Visa Evaluation Bot"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_state = FSMStates.GREETING
        self.answers: Dict[str, Any] = {}
        
        # Questions for each state
        self.questions = {
            FSMStates.GREETING: "Welcome to Easy Visa PK free visa success ratio evaluation. I am here to assist and answer your questions. Which Country visa are you interested to apply?",
            FSMStates.ASK_COUNTRY: "Which Country visa are you interested to apply?",
            FSMStates.COUNTRY_NOT_SUPPORTED: "At the moment we are not providing Visa Success ratio evaluation for this country. We are only assisting in Schengen visas. Would you like to evaluate for a Schengen country instead?",
            FSMStates.ASK_PROFESSION: "Great! I'm going to ask you some questions to evaluate your success ratio. Are you a business person or job holder?",
            FSMStates.ASK_BUSINESS_TYPE: "Are you a sole proprietor or is it a Private Limited company?",
            FSMStates.ASK_SALARY: "What is your current salary?",
            FSMStates.ASK_SALARY_MODE: "Is your salary transferred to your bank account or do you receive it in cash?",
            FSMStates.ASK_TAX_INFO: "Are you a tax filer? If yes, what was your annual income in the last tax return?",
            FSMStates.ASK_BALANCE: "Can you manage a closing balance of 2 million PKR?",
            FSMStates.ASK_TRAVEL: "What is your previous travel history in the last 5 years?"
        }
        
        # Supported countries (Schengen/Europe)
        self.supported_countries = {
            "europe", "schengen", "france", "italy", "spain", "ireland", "portugal", 
            "germany", "belgium", "netherlands", "holland", "poland", "bulgaria", 
            "norway", "denmark", "greece", "hungary", "austria", "switzerland", 
            "luxembourg", "slovenia", "slovakia", "czech republic", "czech", 
            "estonia", "latvia", "lithuania", "malta", "iceland", "liechtenstein",
            "finland", "sweden", "croatia", "romania", "cyprus"
        }
        
        # Non-supported countries
        self.non_supported_countries = {
            "usa", "united states", "america", "canada", "uk", "united kingdom", 
            "britain", "england", "australia", "new zealand", "japan", "singapore", 
            "malaysia", "thailand", "china", "india", "pakistan", "bangladesh", 
            "sri lanka", "nepal", "bhutan", "maldives", "afghanistan", "iran", 
            "iraq", "syria", "lebanon", "jordan", "israel", "palestine", "egypt", 
            "libya", "tunisia", "algeria", "morocco", "mauritania", "mali", 
            "niger", "chad", "sudan", "south sudan", "ethiopia", "eritrea", 
            "djibouti", "somalia", "kenya", "uganda", "tanzania", "rwanda", 
            "burundi", "central african republic", "cameroon", "nigeria", 
            "benin", "togo", "ghana", "cote d'ivoire", "ivory coast", 
            "liberia", "sierra leone", "guinea", "guinea-bissau", "senegal", 
            "gambia", "cape verde", "sao tome and principe", "equatorial guinea", 
            "gabon", "congo", "congo brazzaville", "congo kinshasa", "democratic republic of congo", 
            "angola", "zambia", "zimbabwe", "botswana", "namibia", "south africa", 
            "lesotho", "eswatini", "swaziland", "mozambique", "madagascar", 
            "comoros", "seychelles", "mauritius", "reunion", "mayotte"
        }
    
    def get_current_question(self) -> str:
        """Get the current question for the user"""
        return self.questions.get(self.current_state, "")
    
    def _is_supported_country(self, user_input: str) -> bool:
        """Check if the user input indicates a supported country"""
        input_lower = user_input.lower().strip()
        
        # Handle case where input might be a list
        if isinstance(input_lower, list):
            input_lower = input_lower[0].lower().strip() if input_lower else ""
        
        # Check for supported countries
        for country in self.supported_countries:
            if country in input_lower:
                return True
        
        return False
    
    def _is_non_supported_country(self, user_input: str) -> bool:
        """Check if the user input indicates a non-supported country"""
        input_lower = user_input.lower().strip()
        
        # Handle case where input might be a list
        if isinstance(input_lower, list):
            input_lower = input_lower[0].lower().strip() if input_lower else ""
        
        # Check for non-supported countries
        for country in self.non_supported_countries:
            if country in input_lower:
                return True
        
        return False
    
    def _store_extracted_info(self, extracted_info: Dict[str, Any]) -> List[str]:
        """
        Store extracted information and return list of questions that were answered
        """
        questions_answered = []
        
        # Store country information - only if not already stored
        country_info = extracted_info.get("country", {})
        if country_info.get("value") and country_info.get("confidence", 0) >= 0.7:
            # Only store country if it's not already stored (to avoid overwriting original selection)
            if not self.answers.get("selected_country"):
                country_value = country_info["value"]
                # Handle case where country is a list (from travel history)
                if isinstance(country_value, list):
                    country_value = country_value[0] if country_value else None
                
                if country_value:
                    self.answers["selected_country"] = country_value
                    questions_answered.append("country")
                    logger.info(f"Stored country: {country_value}")
        
        # Store profession information
        profession_info = extracted_info.get("profession", {})
        if profession_info.get("value") and profession_info.get("confidence", 0) >= 0.7:
            self.answers["profession"] = profession_info["value"]
            questions_answered.append("profession")
            logger.info(f"Stored profession: {profession_info['value']}")
        
        # Store business type information
        business_type_info = extracted_info.get("business_type", {})
        if business_type_info.get("value") and business_type_info.get("confidence", 0) >= 0.7:
            self.answers["business_type"] = business_type_info["value"]
            questions_answered.append("business_type")
            logger.info(f"Stored business type: {business_type_info['value']}")
        
        # Store salary information
        salary_info = extracted_info.get("salary", {})
        if salary_info.get("value") and salary_info.get("confidence", 0) >= 0.7:
            self.answers["salary"] = salary_info["value"]
            questions_answered.append("salary")
            logger.info(f"Stored salary: {salary_info['value']}")
        
        # Store salary mode information
        salary_mode_info = extracted_info.get("salary_mode", {})
        if salary_mode_info.get("value") and salary_mode_info.get("confidence", 0) >= 0.7:
            self.answers["salary_mode"] = salary_mode_info["value"]
            questions_answered.append("salary_mode")
            logger.info(f"Stored salary mode: {salary_mode_info['value']}")
        
        # Store tax information
        tax_info = extracted_info.get("tax_filer", {})
        if tax_info.get("value") is not None and tax_info.get("confidence", 0) >= 0.7:
            self.answers["is_tax_filer"] = tax_info["value"]
            questions_answered.append("tax_info")
            logger.info(f"Stored tax filer status: {tax_info['value']}")
        
        # Store annual income
        income_info = extracted_info.get("annual_income", {})
        if income_info.get("value") and income_info.get("confidence", 0) >= 0.7:
            self.answers["annual_income"] = income_info["value"]
            logger.info(f"Stored annual income: {income_info['value']}")
        
        # Store closing balance
        balance_info = extracted_info.get("closing_balance", {})
        if balance_info.get("value") and balance_info.get("confidence", 0) >= 0.7:
            self.answers["closing_balance"] = balance_info["value"]
            questions_answered.append("balance")
            logger.info(f"Stored closing balance: {balance_info['value']}")
        
        # Store travel history
        travel_info = extracted_info.get("travel_history", {})
        if travel_info.get("value") and travel_info.get("confidence", 0) >= 0.7:
            self.answers["travel_history"] = travel_info["value"]
            questions_answered.append("travel")
            logger.info(f"Stored travel history: {travel_info['value']}")
        
        return questions_answered
    
    def _find_next_unanswered_question(self, answered_questions: List[str]) -> Tuple[FSMStates, str]:
        """
        Find the next unanswered question based on what information is already available
        """
        # Define the question sequence with branching logic
        question_sequence = [
            ("country", FSMStates.ASK_COUNTRY),
            ("profession", FSMStates.ASK_PROFESSION),
            # Business branch
            ("business_type", FSMStates.ASK_BUSINESS_TYPE),
            # Job branch
            ("salary", FSMStates.ASK_SALARY),
            ("salary_mode", FSMStates.ASK_SALARY_MODE),
            # Common questions
            ("tax_info", FSMStates.ASK_TAX_INFO),
            ("balance", FSMStates.ASK_BALANCE),
            ("travel", FSMStates.ASK_TRAVEL)
        ]
        
        # Check what's already stored in answers (not just from current extraction)
        stored_answers = set()
        if self.answers.get("selected_country") or self.answers.get("country"):
            stored_answers.add("country")
        if self.answers.get("profession"):
            stored_answers.add("profession")
        if self.answers.get("business_type"):
            stored_answers.add("business_type")
        if self.answers.get("salary"):
            stored_answers.add("salary")
        if self.answers.get("salary_mode"):
            stored_answers.add("salary_mode")
        if self.answers.get("is_tax_filer") is not None or self.answers.get("tax_response"):
            stored_answers.add("tax_info")
        if self.answers.get("closing_balance") or self.answers.get("balance_response"):
            stored_answers.add("balance")
        if self.answers.get("travel_history") or self.answers.get("travel_response"):
            stored_answers.add("travel")
        
        # Combine answered questions from current extraction and stored answers
        all_answered = set(answered_questions) | stored_answers
        logger.info(f"All answered questions: {all_answered}")
        
        # Determine profession type to decide which branch to follow
        profession = self.answers.get("profession", "").lower()
        is_business = any(word in profession for word in ["business", "owner", "entrepreneur", "proprietor"])
        is_job_holder = any(word in profession for word in ["job", "employed", "employee", "worker", "salary"])
        
        # Find the first unanswered question based on profession type
        for question, state in question_sequence:
            if question not in all_answered:
                # Handle branching logic
                if question == "business_type" and not is_business:
                    # Skip business_type if not a business person
                    continue
                elif question in ["salary", "salary_mode"] and not is_job_holder:
                    # Skip salary questions if not a job holder
                    continue
                elif question == "business_type" and is_business:
                    # If business person, ask business type
                    logger.info(f"Next unanswered question: {question} -> {state.value}")
                    return state, self.questions[state]
                elif question == "salary" and is_job_holder:
                    # If job holder, ask salary
                    logger.info(f"Next unanswered question: {question} -> {state.value}")
                    return state, self.questions[state]
                elif question not in ["business_type", "salary", "salary_mode"]:
                    # For common questions, proceed normally
                    logger.info(f"Next unanswered question: {question} -> {state.value}")
                    return state, self.questions[state]
        
        # If all questions are answered, move to evaluation
        logger.info("All questions answered, moving to evaluation")
        return FSMStates.EVALUATION, "Evaluating your profile..."
    
    def _generate_contextual_response(self, extracted_info: Dict[str, Any], next_question: str) -> str:
        """
        Generate a contextual response that acknowledges provided information
        """
        response_parts = []
        
        # Acknowledge country if provided
        country_info = extracted_info.get("country", {})
        if country_info.get("value") and country_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"Great! I see you're interested in {country_info['value']}.")
        
        # Acknowledge profession if provided
        profession_info = extracted_info.get("profession", {})
        if profession_info.get("value") and profession_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I understand you're a {profession_info['value']}.")
        
        # Acknowledge business type if provided
        business_type_info = extracted_info.get("business_type", {})
        if business_type_info.get("value") and business_type_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I see you're a {business_type_info['value']}.")
        
        # Acknowledge salary if provided
        salary_info = extracted_info.get("salary", {})
        if salary_info.get("value") and salary_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I understand your salary is {salary_info['value']}.")
        
        # Acknowledge salary mode if provided
        salary_mode_info = extracted_info.get("salary_mode", {})
        if salary_mode_info.get("value") and salary_mode_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I see you receive salary via {salary_mode_info['value']}.")
        
        # Acknowledge financial information if provided
        balance_info = extracted_info.get("closing_balance", {})
        if balance_info.get("value") and balance_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I see you can manage the required financial balance.")
        
        # Add the next question
        if response_parts:
            response_parts.append(next_question)
            return " ".join(response_parts)
        else:
            return next_question
    
    def smart_process_input(self, user_input: str, extracted_info: Dict[str, Any]) -> Tuple[FSMStates, str]:
        """
        Smart processing that extracts all information and determines next steps
        """
        logger.info(f"Smart processing input: {user_input}")
        logger.info(f"Extracted info: {extracted_info}")
        logger.info(f"Current answers before processing: {self.answers}")
        
        # Store extracted information
        answered_questions = self._store_extracted_info(extracted_info)
        logger.info(f"Questions answered from extraction: {answered_questions}")
        logger.info(f"Answers after storing extracted info: {self.answers}")
        
        # Check for unsupported countries first - only if we're in the country selection phase
        # Don't check for unsupported countries when we're asking about travel history
        if self.current_state == FSMStates.ASK_COUNTRY:
            country_info = extracted_info.get("country", {})
            if country_info.get("value"):
                country_value = country_info["value"]
                # Handle case where country is a list
                if isinstance(country_value, list):
                    country_value = country_value[0] if country_value else ""
                
                if country_value and self._is_non_supported_country(country_value):
                    self.answers["unsupported_country"] = country_value
                    return FSMStates.COUNTRY_NOT_SUPPORTED, self.questions[FSMStates.COUNTRY_NOT_SUPPORTED]
        
        # Find next unanswered question
        next_state, next_question = self._find_next_unanswered_question(answered_questions)
        logger.info(f"Next state determined: {next_state.value}")
        
        # Generate contextual response
        contextual_response = self._generate_contextual_response(extracted_info, next_question)
        
        return next_state, contextual_response
    
    def get_next_state(self, current_state: FSMStates, user_input: str) -> Tuple[FSMStates, str]:
        """Determine next state based on current state and user input"""
        if current_state == FSMStates.GREETING:
            # After greeting, always ask for country
            return FSMStates.ASK_COUNTRY, self.questions[FSMStates.ASK_COUNTRY]
        
        elif current_state == FSMStates.ASK_COUNTRY:
            # Check if user mentioned a supported country
            if self._is_supported_country(user_input):
                # Store the selected country
                self.answers["selected_country"] = user_input
                return FSMStates.ASK_PROFESSION, self.questions[FSMStates.ASK_PROFESSION]
            elif self._is_non_supported_country(user_input):
                # Store the unsupported country and inform user
                self.answers["unsupported_country"] = user_input
                return FSMStates.COUNTRY_NOT_SUPPORTED, self.questions[FSMStates.COUNTRY_NOT_SUPPORTED]
            else:
                # Unclear response, ask again
                return FSMStates.ASK_COUNTRY, "I didn't understand. Please specify which country visa you're interested in (e.g., France, Germany, USA, Canada, etc.)."
        
        elif current_state == FSMStates.COUNTRY_NOT_SUPPORTED:
            # Check if user wants to try a Schengen country
            input_lower = user_input.lower().strip()
            if any(word in input_lower for word in ["yes", "sure", "okay", "ok", "alright", "schengen", "europe"]):
                return FSMStates.ASK_COUNTRY, "Great! Which Schengen country would you like to evaluate for? (e.g., France, Germany, Italy, Spain, etc.)"
            else:
                return FSMStates.COMPLETE, "Thank you for your interest. We currently only provide visa evaluation services for Schengen countries. Feel free to contact us again when you're interested in a Schengen visa."
        
        elif current_state == FSMStates.ASK_PROFESSION:
            # Determine profession type and branch accordingly
            input_lower = user_input.lower().strip()
            if any(word in input_lower for word in ["business", "owner", "entrepreneur", "proprietor"]):
                self.answers["profession"] = "business person"
                return FSMStates.ASK_BUSINESS_TYPE, self.questions[FSMStates.ASK_BUSINESS_TYPE]
            elif any(word in input_lower for word in ["job", "employed", "employee", "worker", "salary"]):
                self.answers["profession"] = "job holder"
                return FSMStates.ASK_SALARY, self.questions[FSMStates.ASK_SALARY]
            else:
                # Unclear response, ask again
                return FSMStates.ASK_PROFESSION, "I didn't understand. Please specify if you are a business person or job holder."
        
        elif current_state == FSMStates.ASK_BUSINESS_TYPE:
            # Store business type and move to tax info
            input_lower = user_input.lower().strip()
            if any(word in input_lower for word in ["sole", "proprietor", "individual"]):
                self.answers["business_type"] = "sole proprietor"
            elif any(word in input_lower for word in ["private", "limited", "pvt", "company", "corporate"]):
                self.answers["business_type"] = "private limited company"
            else:
                self.answers["business_type"] = user_input
            
            return FSMStates.ASK_TAX_INFO, self.questions[FSMStates.ASK_TAX_INFO]
        
        elif current_state == FSMStates.ASK_SALARY:
            # Store salary and move to salary mode
            self.answers["salary"] = user_input
            return FSMStates.ASK_SALARY_MODE, self.questions[FSMStates.ASK_SALARY_MODE]
        
        elif current_state == FSMStates.ASK_SALARY_MODE:
            # Store salary mode and move to tax info
            input_lower = user_input.lower().strip()
            if any(word in input_lower for word in ["bank", "account", "transfer", "deposit"]):
                self.answers["salary_mode"] = "bank transfer"
            elif any(word in input_lower for word in ["cash", "hand"]):
                self.answers["salary_mode"] = "cash"
            else:
                self.answers["salary_mode"] = user_input
            
            return FSMStates.ASK_TAX_INFO, self.questions[FSMStates.ASK_TAX_INFO]
        
        elif current_state == FSMStates.ASK_TAX_INFO:
            return FSMStates.ASK_BALANCE, self.questions[FSMStates.ASK_BALANCE]
        
        elif current_state == FSMStates.ASK_BALANCE:
            return FSMStates.ASK_TRAVEL, self.questions[FSMStates.ASK_TRAVEL]
        
        elif current_state == FSMStates.ASK_TRAVEL:
            return FSMStates.EVALUATION, "Evaluating your profile..."
        
        elif current_state == FSMStates.EVALUATION:
            return FSMStates.COMPLETE, "Thank you for using our visa evaluation service!"
        
        else:
            return FSMStates.COMPLETE, "Evaluation complete."
    
    def evaluate_profile(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate visa application profile based on collected answers
        Returns evaluation report with recommendations
        """
        evaluation = {
            "eligible": False,
            "confidence": 0.0,
            "recommendations": [],
            "risk_factors": [],
            "next_steps": []
        }
        
        score = 0
        max_score = 100
        
        # Check profession (20 points)
        profession = answers.get("profession", "").lower()
        if "business" in profession or "owner" in profession or "entrepreneur" in profession or "proprietor" in profession:
            score += 20
            evaluation["recommendations"].append("✅ Good professional background")
        elif "job" in profession or "employed" in profession or "employee" in profession or "worker" in profession or "salary" in profession:
            score += 15 # Lower score for job holders
            evaluation["recommendations"].append("✅ Good professional background (job holder)")
        else:
            evaluation["risk_factors"].append("⚠️ Professional status unclear")
        
        # Check business type (10 points)
        business_type = answers.get("business_type", "").lower()
        if "sole" in business_type or "proprietor" in business_type or "individual" in business_type:
            score += 10
            evaluation["recommendations"].append("✅ Sole proprietor/Individual business")
        elif "private" in business_type or "limited" in business_type or "pvt" in business_type or "company" in business_type or "corporate" in business_type:
            score += 10
            evaluation["recommendations"].append("✅ Private Limited Company")
        else:
            evaluation["risk_factors"].append("⚠️ Business type unclear")
        
        # Check salary (15 points)
        salary = answers.get("salary", 0)
        salary_mode = answers.get("salary_mode", "").lower()
        
        if salary > 100000 and salary_mode == "bank transfer": # Example threshold
            score += 15
            evaluation["recommendations"].append("✅ Strong financial profile with regular income")
        elif salary > 50000 and salary_mode == "bank transfer":
            score += 10
            evaluation["recommendations"].append("✅ Good income level with regular income")
        else:
            evaluation["risk_factors"].append("⚠️ Income level may be insufficient or irregular")
        
        # Check tax filing and income (30 points)
        is_tax_filer = answers.get("is_tax_filer", False)
        annual_income = answers.get("annual_income", 0)
        
        if is_tax_filer and annual_income > 1200000:  # 1.2M PKR
            score += 30
            evaluation["recommendations"].append("✅ Strong financial profile with tax compliance")
        elif is_tax_filer and annual_income > 800000:  # 800K PKR
            score += 20
            evaluation["recommendations"].append("✅ Good income level with tax compliance")
        else:
            evaluation["risk_factors"].append("⚠️ Income level may be insufficient or tax compliance unclear")
        
        # Check closing balance (25 points)
        closing_balance = answers.get("closing_balance", 0)
        if closing_balance >= 2000000:  # 2M PKR
            score += 25
            evaluation["recommendations"].append("✅ Sufficient financial reserves")
        elif closing_balance >= 1500000:  # 1.5M PKR
            score += 15
            evaluation["recommendations"].append("✅ Adequate financial reserves")
        else:
            evaluation["risk_factors"].append("⚠️ Insufficient financial reserves")
        
        # Check travel history (25 points)
        travel_history = answers.get("travel_history", [])
        if len(travel_history) >= 2:
            score += 25
            evaluation["recommendations"].append("✅ Strong travel history")
        elif len(travel_history) >= 1:
            score += 15
            evaluation["recommendations"].append("✅ Some international travel experience")
        else:
            evaluation["risk_factors"].append("⚠️ No previous international travel")
        
        # Calculate confidence and eligibility
        evaluation["confidence"] = score / max_score
        
        if score >= 70:
            evaluation["eligible"] = True
            evaluation["next_steps"].append("Proceed with visa application")
            evaluation["next_steps"].append("Prepare required documents")
        elif score >= 50:
            evaluation["eligible"] = True
            evaluation["next_steps"].append("Consider applying with additional documentation")
            evaluation["next_steps"].append("Strengthen financial profile")
        else:
            evaluation["eligible"] = False
            evaluation["next_steps"].append("Consider improving financial profile")
            evaluation["next_steps"].append("Build travel history")
            evaluation["next_steps"].append("Consult with visa consultant")
        
        evaluation["score"] = score
        evaluation["max_score"] = max_score
        
        return evaluation


class FSMService:
    """FSM service for managing visa evaluation bot state"""
    
    def __init__(self):
        self.fsm_instances: Dict[str, VisaEvaluationFSM] = {}
    
    async def get_fsm(self, session_id: str) -> VisaEvaluationFSM:
        """Get or create FSM instance for session"""
        if session_id not in self.fsm_instances:
            # Try to load from Redis
            state_data = None
            try:
                state_data = await redis_client.get_state(session_id)
                logger.info(f"Redis state data for session {session_id}: {state_data}")
            except Exception as e:
                logger.error(f"Error loading state from Redis for session {session_id}: {e}")
                # Continue without Redis - use in-memory only
                logger.info(f"Continuing with in-memory FSM for session {session_id}")
            
            fsm = VisaEvaluationFSM(session_id)
            
            if state_data:
                # Restore state and answers
                state_name = state_data.get('state', 'greeting')
                fsm.current_state = FSMStates(state_name)
                fsm.answers = state_data.get('answers', {})
                logger.info(f"Restored FSM state for session {session_id}: {fsm.current_state.value}")
                logger.info(f"Restored answers: {fsm.answers}")
            else:
                logger.info(f"Created new FSM for session {session_id}")
            
            self.fsm_instances[session_id] = fsm
        else:
            logger.info(f"Using existing FSM for session {session_id}: {self.fsm_instances[session_id].current_state.value}")
        
        return self.fsm_instances[session_id]
    
    async def save_fsm_state(self, session_id: str):
        """Save FSM state to Redis"""
        if session_id in self.fsm_instances:
            fsm = self.fsm_instances[session_id]
            state_data = {
                "state": fsm.current_state.value,
                "answers": fsm.answers
            }
            logger.info(f"Saving FSM state for session {session_id}: {state_data}")
            try:
                await redis_client.set_state(
                    session_id,
                    fsm.current_state.value,
                    {"answers": fsm.answers}
                )
                logger.info(f"Successfully saved FSM state for session {session_id}")
            except Exception as e:
                logger.error(f"Error saving FSM state for session {session_id}: {e}")
                # Continue without Redis - state is already in memory
                logger.info(f"Continuing with in-memory state for session {session_id}")
        else:
            logger.warning(f"No FSM instance found for session {session_id}")
    
    async def get_current_state(self, session_id: str) -> Dict[str, Any]:
        """Get current state information"""
        fsm = await self.get_fsm(session_id)
        state_info = {
            "current_state": fsm.current_state.value,
            "current_question": fsm.get_current_question(),
            "answers": fsm.answers
        }
        logger.info(f"get_current_state for session {session_id}: {state_info}")
        return state_info
    
    async def process_user_input(self, session_id: str, user_input: str, extracted_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input and move to next state with smart processing"""
        fsm = await self.get_fsm(session_id)
        
        logger.info(f"FSM processing input for session {session_id} in state {fsm.current_state.value}")
        logger.info(f"User input: {user_input}")
        logger.info(f"Current FSM answers before processing: {fsm.answers}")
        logger.info(f"Extracted info: {extracted_info}")
        
        # Use smart processing if extracted_info is provided and not in special states
        if extracted_info and fsm.current_state not in [FSMStates.COUNTRY_NOT_SUPPORTED, FSMStates.COMPLETE]:
            logger.info("Using smart processing logic")
            
            # Store any additional information from current state if not already extracted
            if fsm.current_state == FSMStates.ASK_PROFESSION and not extracted_info.get("profession", {}).get("value"):
                fsm.answers["profession"] = user_input
                logger.info(f"Stored profession from current state: {user_input}")
            elif fsm.current_state == FSMStates.ASK_BUSINESS_TYPE and not extracted_info.get("business_type", {}).get("value"):
                fsm.answers["business_type"] = user_input
                logger.info(f"Stored business type from current state: {user_input}")
            elif fsm.current_state == FSMStates.ASK_SALARY and not extracted_info.get("salary", {}).get("value"):
                fsm.answers["salary"] = user_input
                logger.info(f"Stored salary from current state: {user_input}")
            elif fsm.current_state == FSMStates.ASK_SALARY_MODE and not extracted_info.get("salary_mode", {}).get("value"):
                fsm.answers["salary_mode"] = user_input
                logger.info(f"Stored salary mode from current state: {user_input}")
            elif fsm.current_state == FSMStates.ASK_TAX_INFO and not extracted_info.get("tax_filer", {}).get("value"):
                fsm.answers["tax_response"] = user_input
                logger.info(f"Stored tax response from current state: {user_input}")
            elif fsm.current_state == FSMStates.ASK_BALANCE and not extracted_info.get("closing_balance", {}).get("value"):
                fsm.answers["balance_response"] = user_input
                logger.info(f"Stored balance response from current state: {user_input}")
            elif fsm.current_state == FSMStates.ASK_TRAVEL and not extracted_info.get("travel_history", {}).get("value"):
                fsm.answers["travel_response"] = user_input
                logger.info(f"Stored travel response from current state: {user_input}")
            
            # Use smart processing
            old_state = fsm.current_state.value
            next_state, next_question = fsm.smart_process_input(user_input, extracted_info)
            logger.info(f"Smart processing: Moving from {old_state} to {next_state.value}")
            logger.info(f"Smart processing response: {next_question}")
            
            # Update the FSM state
            fsm.current_state = next_state
            
        else:
            # Fallback to original logic for special states or when no extracted_info
            logger.info("Using traditional FSM logic")
            
            # Store the answer using original logic
            if fsm.current_state == FSMStates.GREETING:
                # No specific answer to store here, just move to next state
                pass
            elif fsm.current_state == FSMStates.ASK_COUNTRY:
                # No specific answer to store here, just move to next state
                pass
            elif fsm.current_state == FSMStates.COUNTRY_NOT_SUPPORTED:
                # No specific answer to store here, just move to next state
                pass
            elif fsm.current_state == FSMStates.ASK_PROFESSION:
                fsm.answers["profession"] = user_input
                logger.info(f"Stored profession answer: {user_input}")
            elif fsm.current_state == FSMStates.ASK_BUSINESS_TYPE:
                fsm.answers["business_type"] = user_input
                logger.info(f"Stored business type answer: {user_input}")
            elif fsm.current_state == FSMStates.ASK_SALARY:
                fsm.answers["salary"] = user_input
                logger.info(f"Stored salary answer: {user_input}")
            elif fsm.current_state == FSMStates.ASK_SALARY_MODE:
                fsm.answers["salary_mode"] = user_input
                logger.info(f"Stored salary mode answer: {user_input}")
            elif fsm.current_state == FSMStates.ASK_TAX_INFO:
                fsm.answers["tax_response"] = user_input
                logger.info(f"Stored tax answer: {user_input}")
            elif fsm.current_state == FSMStates.ASK_BALANCE:
                fsm.answers["balance_response"] = user_input
                logger.info(f"Stored balance answer: {user_input}")
            elif fsm.current_state == FSMStates.ASK_TRAVEL:
                fsm.answers["travel_response"] = user_input
                logger.info(f"Stored travel answer: {user_input}")
            
            # Move to next state using original logic
            old_state = fsm.current_state.value
            next_state, next_question = fsm.get_next_state(fsm.current_state, user_input)
            logger.info(f"Traditional logic: Moving from {old_state} to {next_state.value}")
            logger.info(f"Traditional logic response: {next_question}")
            
            # Update the FSM state
            fsm.current_state = next_state
        
        logger.info(f"FSM state after update: {fsm.current_state.value}")
        logger.info(f"FSM answers after update: {fsm.answers}")
        
        # If we're at evaluation state, perform evaluation
        if fsm.current_state == FSMStates.EVALUATION:
            logger.info("Performing visa evaluation...")
            evaluation = fsm.evaluate_profile(fsm.answers)
            fsm.answers["evaluation"] = evaluation
            next_question = self._format_evaluation_response(evaluation)
            logger.info(f"Evaluation complete. Score: {evaluation.get('score', 0)}/{evaluation.get('max_score', 100)}")
        
        # Save state
        await self.save_fsm_state(session_id)
        
        result = {
            "current_state": fsm.current_state.value,
            "question": next_question,
            "answers": fsm.answers,
            "is_complete": fsm.current_state == FSMStates.COMPLETE
        }
        
        logger.info(f"FSM process_user_input result: {result}")
        return result
    
    def _format_evaluation_response(self, evaluation: Dict[str, Any]) -> str:
        """Format evaluation results into a readable response"""
        response = "📋 **VISA EVALUATION REPORT**\n\n"
        
        # Score
        response += f"**Overall Score:** {evaluation['score']}/{evaluation['max_score']} ({evaluation['confidence']*100:.1f}%)\n\n"
        
        # Eligibility
        if evaluation["eligible"]:
            response += "✅ **RECOMMENDATION: ELIGIBLE**\n\n"
        else:
            response += "❌ **RECOMMENDATION: NOT ELIGIBLE**\n\n"
        
        # Recommendations
        if evaluation["recommendations"]:
            response += "**Strengths:**\n"
            for rec in evaluation["recommendations"]:
                response += f"• {rec}\n"
            response += "\n"
        
        # Risk factors
        if evaluation["risk_factors"]:
            response += "**Areas of Concern:**\n"
            for risk in evaluation["risk_factors"]:
                response += f"• {risk}\n"
            response += "\n"
        
        # Next steps
        if evaluation["next_steps"]:
            response += "**Next Steps:**\n"
            for step in evaluation["next_steps"]:
                response += f"• {step}\n"
        
        return response
    
    async def reset_session(self, session_id: str):
        """Reset session to initial state"""
        if session_id in self.fsm_instances:
            fsm = self.fsm_instances[session_id]
            fsm.current_state = FSMStates.GREETING
            fsm.answers = {}
            await self.save_fsm_state(session_id)
            logger.info(f"Reset session {session_id} to initial state")


# Global FSM service instance
fsm_service = FSMService() 
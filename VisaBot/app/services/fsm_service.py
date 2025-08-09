"""
FSM (Finite State Machine) service for visa evaluation bot
"""
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
from loguru import logger

from app.services.redis_service import redis_client
from app.services.rag_service import rag_service
from app.services.evaluation_service import evaluation_service


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
    ASK_LAST_TRAVEL_YEAR = "ask_last_travel_year"  # New state for last travel year
    ASK_VALID_VISA = "ask_valid_visa"  # New state for valid visa question
    ASK_SCHENGEN_REJECTION = "ask_schengen_rejection"  # New state for Schengen visa rejection
    ASK_AGE = "ask_age"  # New state for age
    ASK_BUSINESS_PREMISES = "ask_business_premises"  # New state for business premises
    ASK_BUSINESS_ONLINE_PRESENCE = "ask_business_online_presence"  # New state for business online presence
    ASK_BUSINESS_ASSETS = "ask_business_assets"  # New state for manufacturing/inventory/agri
    EVALUATION = "evaluation"
    COMPLETE = "complete"


class VisaEvaluationFSM:
    """Finite State Machine for Visa Evaluation Bot"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_state = FSMStates.ASK_COUNTRY  # Start directly with country question
        self.answers: Dict[str, Any] = {}
        
        # Questions for each state
        self.questions = {
            FSMStates.GREETING: "Welcome to Easy Visa PK free visa success ratio evaluation. I am here to assist and answer your questions. Which Country visa are you interested to apply?",
            FSMStates.ASK_COUNTRY: "Welcome to Easy Visa PK free visa success ratio evaluation. I am here to assist and answer your questions. Which Country visa are you interested to apply?",
            FSMStates.COUNTRY_NOT_SUPPORTED: "At the moment we are not providing Visa Success ratio evaluation for this country. We are only assisting in Schengen visas. Would you like to evaluate for a Schengen country instead?",
            FSMStates.ASK_PROFESSION: "Great! I'm going to ask you some questions to evaluate your success ratio. Are you a business person or job holder?",
            FSMStates.ASK_BUSINESS_TYPE: "Are you a sole proprietor or is it a Private Limited company?",
            FSMStates.ASK_SALARY: "What is your current salary?",
            FSMStates.ASK_SALARY_MODE: "Is your salary transferred to your bank account or do you receive it in cash?",
            FSMStates.ASK_TAX_INFO: "Are you a tax filer? If yes, what was your annual income in the last tax return?",
            FSMStates.ASK_BALANCE: "Can you manage a closing balance of 2 million PKR?",
            FSMStates.ASK_TRAVEL: "What is your previous travel history in the last 5 years?",
            FSMStates.ASK_LAST_TRAVEL_YEAR: "In which year was your last international travel?",
            FSMStates.ASK_VALID_VISA: "Do you have any valid visa of USA, UK, Canada, or Australia?",
            FSMStates.ASK_SCHENGEN_REJECTION: "Do you have any previous Schengen visa rejection? If yes, which year?",
            FSMStates.ASK_AGE: "What is your age?",
            FSMStates.ASK_BUSINESS_PREMISES: "Do you have an office/shop/warehouse with employees?",
            FSMStates.ASK_BUSINESS_ONLINE_PRESENCE: "Do you have a website and Facebook page for your business?",
            FSMStates.ASK_BUSINESS_ASSETS: "Does your business include manufacturing/keeping inventory of products/agricultural land?"
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
    
    def log_current_state(self):
        """Log current state and answers for debugging"""
        logger.info(f"Current FSM state: {self.current_state.value}")
        logger.info(f"Current answers: {self.answers}")
        logger.info(f"Current question: {self.get_current_question()}")
    
    def _is_supported_country(self, user_input: str) -> bool:
        """Check if the user input indicates a supported country"""
        input_lower = user_input.lower().strip()
        
        # Handle case where input might be a list
        if isinstance(input_lower, list):
            input_lower = input_lower[0].lower().strip() if input_lower else ""
        
        logger.info(f"Checking if '{input_lower}' is a supported country")
        
        # Check for supported countries
        for country in self.supported_countries:
            if country in input_lower:
                logger.info(f"Found supported country: {country}")
                return True
        
        logger.info(f"'{input_lower}' is not a supported country")
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

    def _has_target_countries_in_travel(self, travel_history: Any) -> bool:
        """Check if travel history includes USA/UK/Canada/Australia related mentions."""
        target_countries = [
            "usa", "united states", "america", "uk", "united kingdom", "britain", "england",
            "canada", "australia"
        ]
        if isinstance(travel_history, str):
            tl = travel_history.lower().strip()
            return any(c in tl for c in target_countries)
        if isinstance(travel_history, list):
            joined = " ".join([str(c).lower() for c in travel_history])
            return any(c in joined for c in target_countries)
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
                
                # Only store country if we're not in travel history state
                # This prevents travel history countries from being stored as target country
                if country_value and self.current_state != FSMStates.ASK_TRAVEL:
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
        
        # Store travel history (only if non-empty / meaningful)
        travel_info = extracted_info.get("travel_history", {})
        logger.info(f"Travel info from extraction: {travel_info}")
        try:
            confidence = float(travel_info.get("confidence", 0))
        except Exception:
            confidence = 0.0
        travel_value = travel_info.get("value")
        is_meaningful = (
            (isinstance(travel_value, list) and len(travel_value) > 0) or
            (isinstance(travel_value, str) and travel_value.strip() != "")
        )
        if is_meaningful and confidence >= 0.7:
            self.answers["travel_history"] = travel_value
            questions_answered.append("travel")
            logger.info(f"Stored travel history (extracted): {travel_value}")
        else:
            logger.info(
                f"Travel history not stored from extraction - value: {travel_value}, confidence: {confidence}"
            )
        
        # Store last travel year
        last_travel_year_info = extracted_info.get("last_travel_year", {})
        if last_travel_year_info.get("value") and last_travel_year_info.get("confidence", 0) >= 0.7:
            self.answers["last_travel_year"] = last_travel_year_info["value"]
            questions_answered.append("last_travel_year")
            logger.info(f"Stored last travel year: {last_travel_year_info['value']}")
        
        # Store valid visa information (guarded to avoid false positives outside context)
        valid_visa_info = extracted_info.get("valid_visa", {})
        if valid_visa_info.get("value") is not None and valid_visa_info.get("confidence", 0) >= 0.7:
            can_store_valid = False
            if self.current_state == FSMStates.ASK_VALID_VISA:
                can_store_valid = True
            else:
                # Allow storing only if travel history contains heavy countries
                th = self.answers.get("travel_history", "")
                if self._has_target_countries_in_travel(th):
                    can_store_valid = True
            if can_store_valid:
                self.answers["valid_visa"] = valid_visa_info["value"]
                questions_answered.append("valid_visa")
                logger.info(f"Stored valid visa (guarded): {valid_visa_info['value']}")
            else:
                logger.info(
                    f"Ignored valid_visa from extraction outside context. value: {valid_visa_info.get('value')}"
                )
        
        # Store Schengen rejection information
        schengen_rejection_info = extracted_info.get("schengen_rejection", {})
        if schengen_rejection_info.get("value") is not None and schengen_rejection_info.get("confidence", 0) >= 0.7:
            self.answers["schengen_rejection"] = schengen_rejection_info["value"]
            questions_answered.append("schengen_rejection")
            logger.info(f"Stored Schengen rejection: {schengen_rejection_info['value']}")
        
        # Store age information
        age_info = extracted_info.get("age", {})
        if age_info.get("value") and age_info.get("confidence", 0) >= 0.7:
            self.answers["age"] = age_info["value"]
            questions_answered.append("age")
            logger.info(f"Stored age: {age_info['value']}")
        
        # Store business premises information
        business_premises_info = extracted_info.get("business_premises", {})
        if business_premises_info.get("value") is not None and business_premises_info.get("confidence", 0) >= 0.7:
            self.answers["business_premises"] = business_premises_info["value"]
            questions_answered.append("business_premises")
            logger.info(f"Stored business premises: {business_premises_info['value']}")
        
        # Store business online presence information
        business_online_presence_info = extracted_info.get("business_online_presence", {})
        if business_online_presence_info.get("value") is not None and business_online_presence_info.get("confidence", 0) >= 0.7:
            self.answers["business_online_presence"] = business_online_presence_info["value"]
            questions_answered.append("business_online_presence")
            logger.info(f"Stored business online presence: {business_online_presence_info['value']}")

        # Store business assets/manufacturing/inventory/agri information
        business_assets_info = extracted_info.get("business_assets", {})
        if business_assets_info.get("value") is not None and business_assets_info.get("confidence", 0) >= 0.7:
            self.answers["business_assets"] = business_assets_info["value"]
            questions_answered.append("business_assets")
            logger.info(f"Stored business assets: {business_assets_info['value']}")
        
        return questions_answered
    
    def _find_next_unanswered_question(self, answered_questions: List[str]) -> Tuple[FSMStates, str]:
        """
        Find the next unanswered question based on what information is already available
        """
        # Define the question sequence with proper branching logic
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
            ("travel", FSMStates.ASK_TRAVEL),
            ("last_travel_year", FSMStates.ASK_LAST_TRAVEL_YEAR),
            ("valid_visa", FSMStates.ASK_VALID_VISA),
            ("schengen_rejection", FSMStates.ASK_SCHENGEN_REJECTION),
            ("age", FSMStates.ASK_AGE),
            ("business_premises", FSMStates.ASK_BUSINESS_PREMISES),
            ("business_assets", FSMStates.ASK_BUSINESS_ASSETS),
            ("business_online_presence", FSMStates.ASK_BUSINESS_ONLINE_PRESENCE)
        ]
        
        # Check what's already stored in answers (not just from current extraction)
        stored_answers = set()
        if self.answers.get("selected_country") or self.answers.get("country"):
            stored_answers.add("country")
            logger.info(f"Country already stored: {self.answers.get('selected_country') or self.answers.get('country')}")
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
        if self.answers.get("closing_balance") is not None or self.answers.get("balance_response"):
            stored_answers.add("balance")
        if self.answers.get("travel_history") is not None:
            stored_answers.add("travel")
            logger.info(f"TRAVEL CHECK: travel_history found in answers: {self.answers.get('travel_history')}")
        else:
            logger.info(f"TRAVEL CHECK: travel_history NOT found in answers")
        if self.answers.get("last_travel_year"):
            stored_answers.add("last_travel_year")
        if self.answers.get("valid_visa") is not None:
            stored_answers.add("valid_visa")
        if self.answers.get("schengen_rejection") is not None:
            stored_answers.add("schengen_rejection")
        if self.answers.get("age"):
            stored_answers.add("age")
        if self.answers.get("business_premises") is not None:
            stored_answers.add("business_premises")
        if self.answers.get("business_assets") is not None:
            stored_answers.add("business_assets")
        if self.answers.get("business_online_presence") is not None:
            stored_answers.add("business_online_presence")
        
        # Combine answered questions from current extraction and stored answers
        all_answered = set(answered_questions) | stored_answers
        logger.info(f"All answered questions: {all_answered}")
        logger.info(f"Stored answers: {stored_answers}")
        logger.info(f"Current extraction answers: {answered_questions}")
        
        # Determine profession type to decide which branch to follow
        profession = self.answers.get("profession", "").lower()
        is_business = any(word in profession for word in ["business", "owner", "entrepreneur", "proprietor"])
        is_job_holder = any(word in profession for word in ["job", "employed", "employee", "worker", "salary"])
        
        # Find the first unanswered question based on profession type
        for question, state in question_sequence:
            logger.info(f"Checking question: {question}, state: {state.value}, answered: {question in all_answered}")
            if question not in all_answered:
                logger.info(f"Question '{question}' is NOT answered, will ask for: {state.value}")
                logger.info(f"Current answers: {self.answers}")
                logger.info(f"All answered questions: {all_answered}")
                # Handle branching logic
                if question == "business_type":
                    if not is_business:
                        # Skip business_type if not a business person
                        logger.info(f"Skipping business_type - not a business person")
                        continue
                    else:
                        # If business person, ask business type
                        logger.info(f"Next unanswered question: {question} -> {state.value}")
                        return state, self.questions[state]
                elif question in ["salary", "salary_mode"]:
                    if not is_job_holder:
                        # Skip salary questions if not a job holder
                        logger.info(f"Skipping {question} - not a job holder")
                        continue
                    else:
                        # If job holder, ask salary
                        logger.info(f"Next unanswered question: {question} -> {state.value}")
                        return state, self.questions[state]
                elif question == "last_travel_year":
                    # Only ask last travel year if user has travel history
                    travel_history = self.answers.get("travel_history", "")
                    if isinstance(travel_history, str):
                        travel_lower = travel_history.lower().strip()
                        if any(phrase in travel_lower for phrase in ["no", "none", "never", "no history", "no travel", "no travel history", "never traveled", "no international travel"]):
                            # Skip last travel year if no travel history
                            logger.info(f"Skipping last_travel_year - no travel history")
                            continue
                    elif isinstance(travel_history, list) and len(travel_history) == 0:
                        # Skip last travel year if travel history is empty list (no travel)
                        logger.info(f"Skipping last_travel_year - empty travel history list")
                        continue
                    # If travel history exists, ask for last travel year
                    logger.info(f"Next unanswered question: {question} -> {state.value}")
                    return state, self.questions[state]
                elif question == "valid_visa":
                    # Only ask valid visa question if user mentioned USA, UK, Canada, Australia in travel history
                    travel_history = self.answers.get("travel_history", "")
                    if isinstance(travel_history, str):
                        travel_lower = travel_history.lower().strip()
                        target_countries = ["usa", "united states", "america", "uk", "united kingdom", "britain", "england", "canada", "australia"]
                        has_target_country = any(country in travel_lower for country in target_countries)
                        if not has_target_country:
                            # Skip valid visa question if no target countries in travel history
                            logger.info(f"Skipping valid_visa - no target countries in travel history")
                            continue
                    elif isinstance(travel_history, list) and len(travel_history) == 0:
                        # Skip valid visa question if travel history is empty list (no travel)
                        logger.info(f"Skipping valid_visa - empty travel history list")
                        continue
                    # If target countries mentioned, ask for valid visa
                    logger.info(f"Next unanswered question: {question} -> {state.value}")
                    return state, self.questions[state]
                elif question == "age":
                    # Always ask age question
                    logger.info(f"Next unanswered question: {question} -> {state.value}")
                    return state, self.questions[state]
                elif question == "business_premises":
                    # Only ask business premises if user is a business person
                    profession = self.answers.get("profession", "").lower()
                    if "business" in profession:
                        logger.info(f"Next unanswered question: {question} -> {state.value}")
                        return state, self.questions[state]
                    else:
                        # Skip business premises - not a business person
                        logger.info(f"Skipping business_premises - not a business person")
                        continue
                elif question == "business_online_presence":
                    # Only ask business online presence if user is a business person
                    profession = self.answers.get("profession", "").lower()
                    if "business" in profession:
                        logger.info(f"Next unanswered question: {question} -> {state.value}")
                        return state, self.questions[state]
                    else:
                        # Skip business online presence - not a business person
                        logger.info(f"Skipping business_online_presence - not a business person")
                        continue
                else:
                    # For common questions (country, profession, tax_info, balance, travel), proceed normally
                    if question == "travel":
                        logger.info(f"TRAVEL QUESTION: Next unanswered question: {question} -> {state.value}")
                        logger.info(f"TRAVEL QUESTION: Current answers: {self.answers}")
                        logger.info(f"TRAVEL QUESTION: All answered questions: {all_answered}")
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
        
        # Acknowledge last travel year if provided
        last_travel_year_info = extracted_info.get("last_travel_year", {})
        if last_travel_year_info.get("value") and last_travel_year_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I understand your last international travel was in {last_travel_year_info['value']}.")
        
        # Acknowledge valid visa information if provided
        valid_visa_info = extracted_info.get("valid_visa", {})
        if valid_visa_info.get("value") is not None and valid_visa_info.get("confidence", 0) >= 0.7:
            if valid_visa_info["value"]:
                response_parts.append(f"I see you have valid visas for USA, UK, Canada, or Australia.")
            else:
                response_parts.append(f"I understand you don't have valid visas for USA, UK, Canada, or Australia.")
        
        # Acknowledge Schengen rejection information if provided
        schengen_rejection_info = extracted_info.get("schengen_rejection", {})
        if schengen_rejection_info.get("value") is not None and schengen_rejection_info.get("confidence", 0) >= 0.7:
            if schengen_rejection_info["value"]:
                response_parts.append(f"I understand you have had a Schengen visa rejection.")
            else:
                response_parts.append(f"I understand you have not had any Schengen visa rejections.")
        
        # Acknowledge age information if provided
        age_info = extracted_info.get("age", {})
        if age_info.get("value") and age_info.get("confidence", 0) >= 0.7:
            response_parts.append(f"I understand you are {age_info['value']} years old.")
        
        # Acknowledge business premises information if provided
        business_premises_info = extracted_info.get("business_premises", {})
        if business_premises_info.get("value") is not None and business_premises_info.get("confidence", 0) >= 0.7:
            if business_premises_info["value"]:
                response_parts.append(f"I understand you have an office/shop/warehouse with employees.")
            else:
                response_parts.append(f"I understand you don't have an office/shop/warehouse with employees.")
        
        # Acknowledge business online presence information if provided
        business_online_presence_info = extracted_info.get("business_online_presence", {})
        if business_online_presence_info.get("value") is not None and business_online_presence_info.get("confidence", 0) >= 0.7:
            if business_online_presence_info["value"]:
                response_parts.append(f"I understand you have a website and Facebook page for your business.")
            else:
                response_parts.append(f"I understand you don't have a website and Facebook page for your business.")
        
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
        
        # Log current state before processing
        self.log_current_state()
        
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
        if current_state == FSMStates.ASK_COUNTRY:
            # Check if user mentioned a supported country
            logger.info(f"Processing country selection: '{user_input}'")
            if self._is_supported_country(user_input):
                # Store the selected country
                self.answers["selected_country"] = user_input
                logger.info(f"Stored supported country: {user_input}")
                return FSMStates.ASK_PROFESSION, self.questions[FSMStates.ASK_PROFESSION]
            elif self._is_non_supported_country(user_input):
                # Store the unsupported country and inform user
                self.answers["unsupported_country"] = user_input
                logger.info(f"Stored unsupported country: {user_input}")
                return FSMStates.COUNTRY_NOT_SUPPORTED, self.questions[FSMStates.COUNTRY_NOT_SUPPORTED]
            else:
                # Unclear response, ask again
                logger.info(f"Unclear country response: {user_input}")
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
            # Store tax information and move to balance
            input_lower = user_input.lower().strip()
            if "yes" in input_lower:
                self.answers["is_tax_filer"] = True
                # Try to extract annual income if provided
                import re
                numbers = re.findall(r'\d+', user_input)
                if numbers:
                    self.answers["annual_income"] = int(numbers[0])
                else:
                    self.answers["annual_income"] = 0
            else:
                self.answers["is_tax_filer"] = False
                self.answers["annual_income"] = 0
    
            return FSMStates.ASK_BALANCE, self.questions[FSMStates.ASK_BALANCE]
        
        elif current_state == FSMStates.ASK_BALANCE:
            # Store balance information and move to travel
            input_lower = user_input.lower().strip()
            if "yes" in input_lower:
                self.answers["closing_balance"] = True
            else:
                self.answers["closing_balance"] = False
            
            return FSMStates.ASK_TRAVEL, self.questions[FSMStates.ASK_TRAVEL]
        
        elif current_state == FSMStates.ASK_TRAVEL:
            # Store travel history and move to next question
            self.answers["travel_history"] = user_input
            logger.info(f"ASK_TRAVEL: Stored travel_history: {user_input}")
            # Check if we should ask last travel year or valid visa
            travel_lower = user_input.lower().strip()
            if any(phrase in travel_lower for phrase in ["no", "none", "never", "no history", "no travel", "no travel history", "never traveled", "no international travel"]):
                # No travel history, move to Schengen rejection question
                logger.info(f"ASK_TRAVEL: No travel history detected, moving to ASK_SCHENGEN_REJECTION")
                return FSMStates.ASK_SCHENGEN_REJECTION, self.questions[FSMStates.ASK_SCHENGEN_REJECTION]
            else:
                # Has travel history, move to last travel year
                logger.info(f"ASK_TRAVEL: Has travel history, moving to ASK_LAST_TRAVEL_YEAR")
                return FSMStates.ASK_LAST_TRAVEL_YEAR, self.questions[FSMStates.ASK_LAST_TRAVEL_YEAR]
        
        elif current_state == FSMStates.ASK_LAST_TRAVEL_YEAR:
            # Store last travel year and check if we should ask about valid visa
            self.answers["last_travel_year"] = user_input
            travel_history = self.answers.get("travel_history", "")
            if isinstance(travel_history, str):
                travel_lower = travel_history.lower().strip()
                target_countries = ["usa", "united states", "america", "uk", "united kingdom", "britain", "england", "canada", "australia"]
                has_target_country = any(country in travel_lower for country in target_countries)
                if has_target_country:
                    # Has target countries in travel history, ask about valid visa
                    return FSMStates.ASK_VALID_VISA, self.questions[FSMStates.ASK_VALID_VISA]
                else:
                    # No target countries, move to Schengen rejection question
                    return FSMStates.ASK_SCHENGEN_REJECTION, self.questions[FSMStates.ASK_SCHENGEN_REJECTION]
            elif isinstance(travel_history, list) and len(travel_history) == 0:
                # Empty travel history list (no travel), move to Schengen rejection question
                return FSMStates.ASK_SCHENGEN_REJECTION, self.questions[FSMStates.ASK_SCHENGEN_REJECTION]
            else:
                # No travel history, move to Schengen rejection question
                return FSMStates.ASK_SCHENGEN_REJECTION, self.questions[FSMStates.ASK_SCHENGEN_REJECTION]
        
        elif current_state == FSMStates.ASK_VALID_VISA:
            # Store valid visa information and move to Schengen rejection question
            self.answers["valid_visa"] = user_input
            return FSMStates.ASK_SCHENGEN_REJECTION, self.questions[FSMStates.ASK_SCHENGEN_REJECTION]
        
        elif current_state == FSMStates.ASK_SCHENGEN_REJECTION:
            # Store Schengen rejection information and move to age question
            self.answers["schengen_rejection"] = user_input
            return FSMStates.ASK_AGE, self.questions[FSMStates.ASK_AGE]
        
        elif current_state == FSMStates.ASK_AGE:
            # Store age information and check if we should ask business questions
            self.answers["age"] = user_input
            profession = self.answers.get("profession", "").lower()
            if "business" in profession:
                # Business person, ask about business premises
                return FSMStates.ASK_BUSINESS_PREMISES, self.questions[FSMStates.ASK_BUSINESS_PREMISES]
            else:
                # Not a business person, move to evaluation
                return FSMStates.EVALUATION, "Evaluating your profile..."
        
        elif current_state == FSMStates.ASK_BUSINESS_PREMISES:
            # Store business premises information and move to business assets
            self.answers["business_premises"] = user_input
            return FSMStates.ASK_BUSINESS_ASSETS, self.questions[FSMStates.ASK_BUSINESS_ASSETS]

        elif current_state == FSMStates.ASK_BUSINESS_ASSETS:
            # Store business assets/manufacturing/inventory/agri and move to online presence
            self.answers["business_assets"] = user_input
            return FSMStates.ASK_BUSINESS_ONLINE_PRESENCE, self.questions[FSMStates.ASK_BUSINESS_ONLINE_PRESENCE]
        
        elif current_state == FSMStates.ASK_BUSINESS_ONLINE_PRESENCE:
            # Store business online presence information and move to evaluation
            self.answers["business_online_presence"] = user_input
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
        
        # Check salary (15 points) - use safe extraction
        salary = self._safe_get_numeric_value(answers.get("salary", 0))
        salary_mode = answers.get("salary_mode", "").lower()
        
        if salary > 100000 and salary_mode == "bank transfer": # Example threshold
            score += 15
            evaluation["recommendations"].append("✅ Strong financial profile with regular income")
        elif salary > 50000 and salary_mode == "bank transfer":
            score += 10
            evaluation["recommendations"].append("✅ Good income level with regular income")
        else:
            evaluation["risk_factors"].append("⚠️ Income level may be insufficient or irregular")
        
        # Check tax filing and income (30 points) - use safe extraction
        is_tax_filer = answers.get("is_tax_filer", False)
        annual_income = self._safe_get_numeric_value(answers.get("annual_income", 0))
        
        if is_tax_filer and annual_income > 1200000:  # 1.2M PKR
            score += 30
            evaluation["recommendations"].append("✅ Strong financial profile with tax compliance")
        elif is_tax_filer and annual_income > 800000:  # 800K PKR
            score += 20
            evaluation["recommendations"].append("✅ Good income level with tax compliance")
        else:
            evaluation["risk_factors"].append("⚠️ Income level may be insufficient or tax compliance unclear")
        
        # Check closing balance (25 points) - use safe extraction
        closing_balance = self._safe_get_numeric_value(answers.get("closing_balance", 0))
        if closing_balance >= 2000000:  # 2M PKR
            score += 25
            evaluation["recommendations"].append("✅ Sufficient financial reserves")
        elif closing_balance >= 1500000:  # 1.5M PKR
            score += 15
            evaluation["recommendations"].append("✅ Adequate financial reserves")
        else:
            evaluation["risk_factors"].append("⚠️ Insufficient financial reserves")
        
        # Check travel history (25 points) - use safe extraction
        travel_history = self._safe_get_travel_history(answers)
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

    def _safe_get_travel_history(self, answers: Dict[str, Any]) -> List[str]:
        """Safely extract travel history as a list"""
        travel_history = answers.get("travel_history", [])
        
        # Handle different data types
        if isinstance(travel_history, str):
            # Parse string responses
            travel_lower = travel_history.lower().strip()
            
            # Handle negative responses
            if any(phrase in travel_lower for phrase in ["no", "none", "never", "no history", "no travel", "no travel history", "never traveled", "no international travel"]):
                return []
            
            # Try to extract countries from text
            countries = []
            # Common country keywords
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
                if country in travel_lower:
                    countries.append(country.title())
            
            return countries if countries else []
        
        elif isinstance(travel_history, list):
            return travel_history
        else:
            return []
    
    def _safe_get_numeric_value(self, value: Any) -> int:
        """Safely extract numeric value from various data types"""
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+', value)
            if numbers:
                return int(numbers[0])
            return 0
        else:
            return 0
    
    def _handle_off_track_question(self, user_input: str, current_state: FSMStates) -> Tuple[str, bool]:
        """
        Handle off-track questions and provide appropriate responses
        Returns: (response_message, should_continue_to_fsm)
        """
        input_lower = user_input.lower().strip()
        
        # Common off-track questions and their responses
        off_track_patterns = {
            # Visa approval questions
            "higher chances": "I understand you want to know about visa approval chances. Let me complete the evaluation first by asking a few more questions, then I'll provide you with a detailed analysis.",
            "approval rate": "I'll calculate your approval probability once I have all your information. Let's continue with the evaluation.",
            "success rate": "Your success rate will be determined based on your complete profile. Let me gather all the necessary information first.",
            "chances": "I'll assess your visa chances after completing the evaluation. Let's continue with the questions.",
            
            # Process questions
            "how long": "The visa application process typically takes 2-4 weeks for Schengen visas. Let me complete your evaluation first.",
            "processing time": "Processing times vary by country, usually 2-4 weeks. Let's finish your evaluation first.",
            "documents needed": "I'll provide a complete document list after your evaluation. Let's continue with the assessment.",
            "requirements": "I'll outline all requirements based on your profile. Let me complete the evaluation first.",
            
            # Cost questions
            "cost": "Visa fees vary by country (€90 for Schengen). Let me complete your evaluation first.",
            "fee": "Visa fees are typically €90 for Schengen visas. Let's finish your evaluation.",
            "price": "Visa costs vary by country. I'll provide specific details after your evaluation.",
            
            # General questions
            "what is": "I'm here to evaluate your visa application. Let me ask you a few questions to provide an accurate assessment.",
            "can you": "I can help with visa evaluation. Let me complete your profile assessment first.",
            "help me": "I'm here to help with your visa evaluation. Let's continue with the assessment.",
            
            # Interruption patterns
            "wait": "I understand. Let me ask you one more question to complete your evaluation.",
            "stop": "I'll be brief. Let me just ask one more question to finish your evaluation.",
            "enough": "Just one more question to complete your evaluation, then I'll provide full details.",
        }
        
        # Check for off-track patterns
        for pattern, response in off_track_patterns.items():
            if pattern in input_lower:
                return response, False  # Don't continue to FSM, use this response
        
        # If no off-track pattern found, continue with normal FSM processing
        return "", True
    
    def _get_current_question_with_context(self, current_state: FSMStates) -> str:
        """Get current question with additional context to keep user on track"""
        base_question = self.questions.get(current_state, "")
        
        # Add context based on state
        context_additions = {
            FSMStates.ASK_COUNTRY: " (Please specify a country like France, Germany, Italy, etc.)",
            FSMStates.ASK_PROFESSION: " (Please answer: business person or job holder)",
            FSMStates.ASK_BUSINESS_TYPE: " (Please specify: sole proprietor or private limited company)",
            FSMStates.ASK_SALARY: " (Please provide your monthly salary amount)",
            FSMStates.ASK_SALARY_MODE: " (Please specify: bank transfer or cash)",
            FSMStates.ASK_TAX_INFO: " (Please answer: yes/no and provide annual income if yes)",
            FSMStates.ASK_BALANCE: " (Please answer: yes/no for 2 million PKR balance)",
            FSMStates.ASK_TRAVEL: " (Please list countries visited in last 5 years, or say 'none' if no travel)",
            FSMStates.ASK_LAST_TRAVEL_YEAR: " (Please specify the year, e.g., 2023, 2022, etc.)",
            FSMStates.ASK_VALID_VISA: " (Please answer: yes/no)",
            FSMStates.ASK_SCHENGEN_REJECTION: " (Please answer: yes/no and specify year if yes)",
            FSMStates.ASK_AGE: " (Please specify your age in years)",
            FSMStates.ASK_BUSINESS_PREMISES: " (Please answer: yes/no)",
            FSMStates.ASK_BUSINESS_ONLINE_PRESENCE: " (Please answer: yes/no)",
        }
        
        context = context_additions.get(current_state, "")
        return base_question + context


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
                state_name = state_data.get('state', 'ask_country')  # Default to ask_country
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
        """
        Process user input and return next state and response
        Now integrates with RAG for off-track questions and complex evaluation
        """
        try:
            # Get FSM instance
            fsm = await self.get_fsm(session_id)
            
            # Check for off-track questions first using RAG
            rag_response = await rag_service.handle_off_track_question(
                user_input, 
                fsm.current_state.value, 
                {"answers": fsm.answers, "session_id": session_id}
            )
            
            if rag_response.confidence > 0.6 and not rag_response.should_return_to_fsm:
                # RAG handled the question completely
                logger.info(f"RAG handled off-track question with confidence: {rag_response.confidence}")
                return {
                    "current_state": fsm.current_state.value,
                    "question": rag_response.answer,
                    "answers": fsm.answers,
                    "is_complete": False,
                    "is_off_track": True,
                    "rag_handled": True
                }
            
            # If RAG suggests returning to FSM, use its transition message
            if rag_response.confidence > 0.6 and rag_response.should_return_to_fsm:
                # Use RAG's contextual response that includes transition back to FSM
                logger.info(f"RAG provided contextual response with transition to FSM")
                return {
                    "current_state": fsm.current_state.value,
                    "question": rag_response.answer,
                    "answers": fsm.answers,
                    "is_complete": False,
                    "is_off_track": True,
                    "rag_handled": True,
                    "rag_context": rag_response.context_for_fsm
                }
            
            # Fallback to original FSM logic for on-track questions
            # Check for off-track questions first (original logic)
            off_track_response, should_continue = fsm._handle_off_track_question(user_input, fsm.current_state)
            if not should_continue:
                # User asked an off-track question, provide response and stay in current state
                logger.info(f"Handling off-track question: {off_track_response}")
                return {
                    "current_state": fsm.current_state.value,
                    "question": off_track_response + "\n\n" + fsm._get_current_question_with_context(fsm.current_state),
                    "answers": fsm.answers,
                    "is_complete": False,
                    "is_off_track": True
                }
            
            # Initialize answered_questions
            answered_questions = []
            
            # Store extracted information if provided
            if extracted_info:
                answered_questions = fsm._store_extracted_info(extracted_info)
                logger.info(f"Stored extracted info, answered questions: {answered_questions}")
            
            # Always use traditional FSM logic as fallback to ensure answers are stored
            logger.info("Using traditional FSM logic to ensure answers are stored")
            
            # Store the answer using traditional logic
            if fsm.current_state == FSMStates.ASK_COUNTRY:
                # Handle country selection using traditional logic
                if "country" not in answered_questions:  # Only store if not already stored by extracted_info
                    if fsm._is_supported_country(user_input):
                        fsm.answers["selected_country"] = user_input
                        logger.info(f"Stored country answer: {user_input}")
                        answered_questions.append("country")
                    elif fsm._is_non_supported_country(user_input):
                        fsm.answers["unsupported_country"] = user_input
                        logger.info(f"Stored unsupported country: {user_input}")
                        # Don't add to answered_questions as this will be handled by get_next_state
                    else:
                        # Unclear response, don't store anything
                        logger.info(f"Unclear country response: {user_input}")
            elif fsm.current_state == FSMStates.COUNTRY_NOT_SUPPORTED:
                # No specific answer to store here, just move to next state
                pass
            elif fsm.current_state == FSMStates.ASK_PROFESSION:
                if "profession" not in answered_questions:  # Only store if not already stored by extracted_info
                    fsm.answers["profession"] = user_input
                    logger.info(f"Stored profession answer: {user_input}")
                    answered_questions.append("profession")
            elif fsm.current_state == FSMStates.ASK_BUSINESS_TYPE:
                if "business_type" not in answered_questions:  # Only store if not already stored by extracted_info
                    fsm.answers["business_type"] = user_input
                    logger.info(f"Stored business type answer: {user_input}")
                    answered_questions.append("business_type")
            elif fsm.current_state == FSMStates.ASK_SALARY:
                if "salary" not in answered_questions:  # Only store if not already stored by extracted_info
                    fsm.answers["salary"] = user_input
                    logger.info(f"Stored salary answer: {user_input}")
                    answered_questions.append("salary")
            elif fsm.current_state == FSMStates.ASK_SALARY_MODE:
                if "salary_mode" not in answered_questions:  # Only store if not already stored by extracted_info
                    fsm.answers["salary_mode"] = user_input
                    logger.info(f"Stored salary mode answer: {user_input}")
                    answered_questions.append("salary_mode")
            elif fsm.current_state == FSMStates.ASK_TAX_INFO:
                if "tax_info" not in answered_questions:  # Only store if not already stored by extracted_info
                    # Handle tax information more robustly
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        fsm.answers["is_tax_filer"] = True
                        # Try to extract annual income if provided
                        import re
                        numbers = re.findall(r'\d+', user_input)
                        if numbers:
                            fsm.answers["annual_income"] = int(numbers[0])
                        else:
                            # If no income provided, store the response for later processing
                            fsm.answers["tax_response"] = user_input
                        logger.info(f"Stored tax answer: {user_input}")
                        answered_questions.append("tax_info")
                    elif "no" in input_lower:
                        fsm.answers["is_tax_filer"] = False
                        fsm.answers["annual_income"] = 0
                        logger.info(f"Stored tax answer: {user_input}")
                        answered_questions.append("tax_info")
                    else:
                        # Store the response as is for later processing
                        fsm.answers["tax_response"] = user_input
                        logger.info(f"Stored tax answer: {user_input}")
                        answered_questions.append("tax_info")
            elif fsm.current_state == FSMStates.ASK_BALANCE:
                if "balance" not in answered_questions:  # Only store if not already stored by extracted_info
                    # Handle balance information more robustly
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        fsm.answers["closing_balance"] = True
                    elif "no" in input_lower:
                        fsm.answers["closing_balance"] = False
                    else:
                        # Store the response as is for later processing
                        fsm.answers["balance_response"] = user_input
                    logger.info(f"Stored balance answer: {user_input}")
                    answered_questions.append("balance")
            elif fsm.current_state == FSMStates.ASK_TRAVEL:
                logger.info(f"PROCESS_USER_INPUT: Processing ASK_TRAVEL state with input: {user_input}")
                input_lower = user_input.lower().strip()
                negative_phrases = [
                    "no", "none", "never", "no history", "no travel", "no travel history",
                    "never traveled", "no international travel"
                ]
                if "travel" not in answered_questions:
                    # Primary storage from raw input
                    if any(phrase in input_lower for phrase in negative_phrases):
                        fsm.answers["travel_history"] = []
                        logger.info("PROCESS_USER_INPUT: Stored empty travel_history (no travel)")
                    else:
                        fsm.answers["travel_history"] = user_input
                        logger.info(f"PROCESS_USER_INPUT: Stored travel_history from raw: {user_input}")
                    logger.info(f"Stored travel answer: {user_input}")
                    answered_questions.append("travel")
                else:
                    # Fallback: if extracted info marked travel as answered but value is empty, recover from raw input
                    current_travel = fsm.answers.get("travel_history")
                    is_empty = (
                        current_travel is None or
                        (isinstance(current_travel, list) and len(current_travel) == 0) or
                        (isinstance(current_travel, str) and current_travel.strip() == "")
                    )
                    if is_empty:
                        if any(phrase in input_lower for phrase in negative_phrases):
                            fsm.answers["travel_history"] = []
                            logger.info("PROCESS_USER_INPUT: Recovered empty travel_history (no travel)")
                        else:
                            fsm.answers["travel_history"] = user_input
                            logger.info(f"PROCESS_USER_INPUT: Recovered travel_history from raw: {user_input}")
                    else:
                        logger.info("PROCESS_USER_INPUT: Travel already answered by extracted_info (non-empty)")
            elif fsm.current_state == FSMStates.ASK_LAST_TRAVEL_YEAR:
                if "last_travel_year" not in answered_questions:  # Only store if not already stored by extracted_info
                    fsm.answers["last_travel_year"] = user_input
                    logger.info(f"Stored last travel year answer: {user_input}")
                    answered_questions.append("last_travel_year")
            elif fsm.current_state == FSMStates.ASK_VALID_VISA:
                if "valid_visa" not in answered_questions:  # Only store if not already stored by extracted_info
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        fsm.answers["valid_visa"] = True
                    elif "no" in input_lower:
                        fsm.answers["valid_visa"] = False
                    else:
                        fsm.answers["valid_visa"] = user_input
                    logger.info(f"Stored valid visa answer (explicit state): {user_input}")
                    answered_questions.append("valid_visa")
            elif fsm.current_state == FSMStates.ASK_SCHENGEN_REJECTION:
                if "schengen_rejection" not in answered_questions:  # Only store if not already stored by extracted_info
                    # Handle Schengen rejection information more robustly
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        # Try to extract year if provided
                        import re
                        years = re.findall(r'\b(20[12]\d|19[89]\d)\b', user_input)
                        if years:
                            fsm.answers["schengen_rejection"] = {"has_rejection": True, "year": years[0]}
                        else:
                            fsm.answers["schengen_rejection"] = {"has_rejection": True, "year": None}
                    elif "no" in input_lower:
                        fsm.answers["schengen_rejection"] = {"has_rejection": False, "year": None}
                    else:
                        # Store the response as is for later processing
                        fsm.answers["schengen_rejection"] = user_input
                    logger.info(f"Stored Schengen rejection answer: {user_input}")
                    answered_questions.append("schengen_rejection")
            elif fsm.current_state == FSMStates.ASK_AGE:
                if "age" not in answered_questions:  # Only store if not already stored by extracted_info
                    fsm.answers["age"] = user_input
                    logger.info(f"Stored age answer: {user_input}")
                    answered_questions.append("age")
            elif fsm.current_state == FSMStates.ASK_BUSINESS_PREMISES:
                if "business_premises" not in answered_questions:  # Only store if not already stored by extracted_info
                    # Handle business premises information more robustly
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        fsm.answers["business_premises"] = True
                    elif "no" in input_lower:
                        fsm.answers["business_premises"] = False
                    else:
                        # Store the response as is for later processing
                        fsm.answers["business_premises"] = user_input
                    logger.info(f"Stored business premises answer: {user_input}")
                    answered_questions.append("business_premises")
            elif fsm.current_state == FSMStates.ASK_BUSINESS_ASSETS:
                if "business_assets" not in answered_questions:  # Only store if not already stored by extracted_info
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        fsm.answers["business_assets"] = True
                    elif "no" in input_lower:
                        fsm.answers["business_assets"] = False
                    else:
                        # Store the response as is for later processing
                        fsm.answers["business_assets"] = user_input
                    logger.info(f"Stored business assets answer: {user_input}")
                    answered_questions.append("business_assets")
            elif fsm.current_state == FSMStates.ASK_BUSINESS_ONLINE_PRESENCE:
                if "business_online_presence" not in answered_questions:  # Only store if not already stored by extracted_info
                    # Handle business online presence information more robustly
                    input_lower = user_input.lower().strip()
                    if "yes" in input_lower:
                        fsm.answers["business_online_presence"] = True
                    elif "no" in input_lower:
                        fsm.answers["business_online_presence"] = False
                    else:
                        # Store the response as is for later processing
                        fsm.answers["business_online_presence"] = user_input
                    logger.info(f"Stored business online presence answer: {user_input}")
                    answered_questions.append("business_online_presence")
            
            # For country selection, use traditional logic
            if fsm.current_state == FSMStates.ASK_COUNTRY:
                next_state, next_question = fsm.get_next_state(fsm.current_state, user_input)
                fsm.current_state = next_state
                logger.info(f"Country selection - Next state: {next_state.value}")
            else:
                # Find next unanswered question for other states
                next_state, next_question = fsm._find_next_unanswered_question(answered_questions)
                # Update FSM state
                fsm.current_state = next_state
            
            # Check if evaluation is complete
            if next_state == FSMStates.EVALUATION:
                # Perform scenario-based evaluation using the new evaluation service
                target_country = fsm.answers.get("selected_country") or fsm.answers.get("country")
                scenario_evaluation = await evaluation_service.evaluate_visa_application(fsm.answers, target_country)
                
                # Format response using the evaluation service
                response_message = await evaluation_service.get_evaluation_summary(fsm.answers, target_country)
                
                # Store evaluation results
                fsm.answers["evaluation"] = scenario_evaluation
                
                # Move to complete state
                fsm.current_state = FSMStates.COMPLETE
                
                # Save FSM state
                await self.save_fsm_state(session_id)
                
                return {
                    "current_state": fsm.current_state.value,
                    "question": response_message,
                    "answers": fsm.answers,
                    "is_complete": True,
                    "evaluation": scenario_evaluation
                }
            
            # Generate contextual response for next question
            response_message = fsm._generate_contextual_response(extracted_info, next_question)
            
            # Save FSM state
            await self.save_fsm_state(session_id)
            
            return {
                "current_state": fsm.current_state.value,
                "question": response_message,
                "answers": fsm.answers,
                "is_complete": False
            }
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            raise


    
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
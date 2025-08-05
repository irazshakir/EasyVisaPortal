"""
FSM (Finite State Machine) service for visa evaluation bot
"""
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from loguru import logger

from app.services.redis_service import redis_client


class FSMStates(Enum):
    """FSM States for visa evaluation"""
    ASK_PROFESSION = "ask_profession"
    ASK_TAX_INFO = "ask_tax_info"
    ASK_BALANCE = "ask_balance"
    ASK_TRAVEL = "ask_travel"
    EVALUATION = "evaluation"
    COMPLETE = "complete"


class VisaEvaluationFSM:
    """Finite State Machine for Visa Evaluation Bot"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_state = FSMStates.ASK_PROFESSION
        self.answers: Dict[str, Any] = {}
        
        # Questions for each state
        self.questions = {
            FSMStates.ASK_PROFESSION: "Are you a business person or job holder?",
            FSMStates.ASK_TAX_INFO: "Are you a tax filer? If yes, what was your annual income in the last tax return?",
            FSMStates.ASK_BALANCE: "Can you manage a closing balance of 2 million PKR?",
            FSMStates.ASK_TRAVEL: "What is your previous travel history in the last 5 years?"
        }
    
    def get_current_question(self) -> str:
        """Get the current question for the user"""
        return self.questions.get(self.current_state, "")
    
    def get_next_state(self, current_state: FSMStates, user_input: str) -> Tuple[FSMStates, str]:
        """Determine next state based on current state and user input"""
        if current_state == FSMStates.ASK_PROFESSION:
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
        if "business" in profession or "job" in profession or "employed" in profession:
            score += 20
            evaluation["recommendations"].append("✅ Good professional background")
        else:
            evaluation["risk_factors"].append("⚠️ Professional status unclear")
        
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
                state_name = state_data.get('state', 'ask_profession')
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
    
    async def process_user_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Process user input and move to next state"""
        fsm = await self.get_fsm(session_id)
        
        logger.info(f"FSM processing input for session {session_id} in state {fsm.current_state.value}")
        logger.info(f"User input: {user_input}")
        logger.info(f"Current FSM answers before processing: {fsm.answers}")
        
        # Store the answer
        if fsm.current_state == FSMStates.ASK_PROFESSION:
            fsm.answers["profession"] = user_input
            logger.info(f"Stored profession answer: {user_input}")
        elif fsm.current_state == FSMStates.ASK_TAX_INFO:
            fsm.answers["tax_response"] = user_input
            logger.info(f"Stored tax answer: {user_input}")
        elif fsm.current_state == FSMStates.ASK_BALANCE:
            fsm.answers["balance_response"] = user_input
            logger.info(f"Stored balance answer: {user_input}")
        elif fsm.current_state == FSMStates.ASK_TRAVEL:
            fsm.answers["travel_response"] = user_input
            logger.info(f"Stored travel answer: {user_input}")
        
        logger.info(f"FSM answers after storing: {fsm.answers}")
        
        # Move to next state
        old_state = fsm.current_state.value
        next_state, next_question = fsm.get_next_state(fsm.current_state, user_input)
        logger.info(f"Moving from {old_state} to {next_state.value}")
        logger.info(f"Next question: {next_question}")
        
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
            fsm.current_state = FSMStates.ASK_PROFESSION
            fsm.answers = {}
            await self.save_fsm_state(session_id)
            logger.info(f"Reset session {session_id} to initial state")


# Global FSM service instance
fsm_service = FSMService() 
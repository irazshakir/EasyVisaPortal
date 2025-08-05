#!/usr/bin/env python3
"""
Simple test for FSM logic
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMStates, VisaEvaluationFSM
from loguru import logger

def test_fsm_logic():
    """Test FSM logic without Redis"""
    print("🧪 Testing FSM Logic (No Redis)")
    print("=" * 50)
    
    # Create FSM instance
    fsm = VisaEvaluationFSM("test_session")
    print(f"Initial state: {fsm.current_state.value}")
    print(f"Initial question: {fsm.get_current_question()}")
    
    # Test state transitions
    test_inputs = [
        "business",
        "Yes, I am a tax filer. My income is 1.5 million PKR",
        "Yes, I can manage 2 million PKR",
        "I have traveled to Dubai and Singapore"
    ]
    
    current_state = fsm.current_state
    for i, user_input in enumerate(test_inputs):
        print(f"\n--- Step {i+1} ---")
        print(f"Current state: {current_state.value}")
        print(f"User input: {user_input}")
        
        # Store answer
        if current_state == FSMStates.ASK_PROFESSION:
            fsm.answers["profession"] = user_input
        elif current_state == FSMStates.ASK_TAX_INFO:
            fsm.answers["tax_response"] = user_input
        elif current_state == FSMStates.ASK_BALANCE:
            fsm.answers["balance_response"] = user_input
        elif current_state == FSMStates.ASK_TRAVEL:
            fsm.answers["travel_response"] = user_input
        
        print(f"Stored answers: {fsm.answers}")
        
        # Get next state
        next_state, next_question = fsm.get_next_state(current_state, user_input)
        print(f"Next state: {next_state.value}")
        print(f"Next question: {next_question}")
        
        # Update state
        fsm.current_state = next_state
        current_state = next_state
        
        # If we're at evaluation, perform evaluation
        if current_state == FSMStates.EVALUATION:
            evaluation = fsm.evaluate_profile(fsm.answers)
            print(f"Evaluation score: {evaluation.get('score', 0)}/{evaluation.get('max_score', 100)}")
            print(f"Eligible: {evaluation.get('eligible', False)}")
            break
    
    print("\n✅ FSM logic test completed!")

if __name__ == "__main__":
    test_fsm_logic() 
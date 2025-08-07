#!/usr/bin/env python3
"""
Test script to debug FSM logic
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.fsm_service import VisaEvaluationFSM, FSMStates
from app.services.openai_service import openai_service

async def test_fsm_logic():
    """Test FSM logic to see why it's asking for country again"""
    
    # Create a test FSM instance
    fsm = VisaEvaluationFSM("test-session")
    
    # Simulate the scenario from the logs
    print("=== Initial State ===")
    print(f"Current state: {fsm.current_state.value}")
    print(f"Current answers: {fsm.answers}")
    
    # Simulate storing country and profession (as in the logs)
    fsm.answers["selected_country"] = "germany"
    fsm.answers["profession"] = "job holder"
    
    print("\n=== After storing country and profession ===")
    print(f"Current answers: {fsm.answers}")
    
    # Test the _find_next_unanswered_question method
    print("\n=== Testing _find_next_unanswered_question ===")
    next_state, next_question = fsm._find_next_unanswered_question([])
    print(f"Next state: {next_state.value}")
    print(f"Next question: {next_question}")
    
    # Test with extracted info
    print("\n=== Testing with extracted info ===")
    extracted_info = {
        "profession": {"value": "job holder", "confidence": 1.0, "source": "explicit"}
    }
    
    answered_questions = fsm._store_extracted_info(extracted_info)
    print(f"Answered questions from extraction: {answered_questions}")
    print(f"Answers after extraction: {fsm.answers}")
    
    next_state, next_question = fsm._find_next_unanswered_question(answered_questions)
    print(f"Next state: {next_state.value}")
    print(f"Next question: {next_question}")

if __name__ == "__main__":
    asyncio.run(test_fsm_logic()) 
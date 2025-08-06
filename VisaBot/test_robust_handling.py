#!/usr/bin/env python3
"""
Test script for robust handling improvements
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import VisaEvaluationFSM, FSMStates
from app.services.openai_service import openai_service


async def test_travel_history_handling():
    """Test travel history handling with various inputs"""
    print("🧪 Testing Travel History Handling")
    print("=" * 50)
    
    fsm = VisaEvaluationFSM("test_session")
    
    # Test cases for travel history
    test_cases = [
        ("no travel history", []),
        ("none", []),
        ("never traveled", []),
        ("no international travel", []),
        ("dubai, sri lanka, saudi arabia", ["Dubai", "Sri Lanka", "Saudi Arabia"]),
        ("visited dubai and turkey", ["Dubai", "Turkey"]),
        ("been to france and germany", ["France", "Germany"]),
        ("no", []),
        ("", []),
    ]
    
    for input_text, expected in test_cases:
        # Create test answers with the input
        test_answers = {"travel_history": input_text}
        
        # Test the safe extraction
        result = fsm._safe_get_travel_history(test_answers)
        
        print(f"Input: '{input_text}'")
        print(f"Expected: {expected}")
        print(f"Result: {result}")
        print(f"✅ Pass" if result == expected else f"❌ Fail")
        print("-" * 30)


async def test_off_track_handling():
    """Test off-track question handling"""
    print("\n🧪 Testing Off-Track Question Handling")
    print("=" * 50)
    
    fsm = VisaEvaluationFSM("test_session")
    
    # Test cases for off-track questions
    test_cases = [
        ("what do you think have higher chances of visa approval", False),
        ("how long does the process take", False),
        ("what documents do I need", False),
        ("how much does it cost", False),
        ("I am a business person", True),  # Should continue to FSM
        ("France", True),  # Should continue to FSM
        ("yes I can manage 2 million", True),  # Should continue to FSM
    ]
    
    for input_text, should_continue in test_cases:
        response, continue_to_fsm = fsm._handle_off_track_question(input_text, FSMStates.ASK_TAX_INFO)
        
        print(f"Input: '{input_text}'")
        print(f"Expected continue: {should_continue}")
        print(f"Actual continue: {continue_to_fsm}")
        print(f"Response: {response[:100]}...")
        print(f"✅ Pass" if continue_to_fsm == should_continue else f"❌ Fail")
        print("-" * 30)


async def test_numeric_extraction():
    """Test safe numeric value extraction"""
    print("\n🧪 Testing Numeric Value Extraction")
    print("=" * 50)
    
    fsm = VisaEvaluationFSM("test_session")
    
    # Test cases for numeric extraction
    test_cases = [
        (100000, 100000),
        ("100000", 100000),
        ("I earn 50000 per month", 50000),
        ("My salary is 75000", 75000),
        ("2 million PKR", 2000000),
        ("no salary", 0),
        ("", 0),
    ]
    
    for input_value, expected in test_cases:
        result = fsm._safe_get_numeric_value(input_value)
        
        print(f"Input: {input_value}")
        print(f"Expected: {expected}")
        print(f"Result: {result}")
        print(f"✅ Pass" if result == expected else f"❌ Fail")
        print("-" * 30)


async def test_openai_parsing():
    """Test OpenAI parsing with various inputs"""
    print("\n🧪 Testing OpenAI Parsing")
    print("=" * 50)
    
    test_inputs = [
        "I have no travel history",
        "I visited Dubai and Saudi Arabia",
        "My salary is 80000 per month via bank transfer",
        "I can manage 2 million PKR balance",
    ]
    
    for input_text in test_inputs:
        try:
            result = await openai_service.parse_user_input("ask_travel", input_text)
            print(f"Input: '{input_text}'")
            print(f"Parsed: {result.get('extracted_info', {}).get('travel_history', 'Not found')}")
            print("-" * 30)
        except Exception as e:
            print(f"Error parsing '{input_text}': {e}")
            print("-" * 30)


async def test_complete_flow():
    """Test complete flow with problematic inputs"""
    print("\n🧪 Testing Complete Flow")
    print("=" * 50)
    
    fsm = VisaEvaluationFSM("test_session")
    
    # Simulate a conversation with problematic inputs
    conversation = [
        ("I want to apply for France visa", FSMStates.ASK_COUNTRY),
        ("I am a business person", FSMStates.ASK_PROFESSION),
        ("what are my chances of approval", FSMStates.ASK_BUSINESS_TYPE),  # Off-track
        ("sole proprietor", FSMStates.ASK_BUSINESS_TYPE),
        ("yes I am a tax filer with 1.5 million income", FSMStates.ASK_TAX_INFO),
        ("yes I can manage 2 million", FSMStates.ASK_BALANCE),
        ("no travel history", FSMStates.ASK_TRAVEL),
    ]
    
    for user_input, expected_state in conversation:
        print(f"User: {user_input}")
        print(f"Expected state: {expected_state.value}")
        
        # Simulate the flow
        if fsm.current_state == expected_state:
            # Process normally
            if expected_state == FSMStates.ASK_COUNTRY:
                fsm.answers["selected_country"] = "France"
                fsm.current_state = FSMStates.ASK_PROFESSION
            elif expected_state == FSMStates.ASK_PROFESSION:
                fsm.answers["profession"] = "business person"
                fsm.current_state = FSMStates.ASK_BUSINESS_TYPE
            elif expected_state == FSMStates.ASK_BUSINESS_TYPE:
                # Check for off-track question
                response, continue_to_fsm = fsm._handle_off_track_question(user_input, fsm.current_state)
                if not continue_to_fsm:
                    print(f"Bot: {response}")
                    print("(Staying in current state due to off-track question)")
                else:
                    fsm.answers["business_type"] = "sole proprietor"
                    fsm.current_state = FSMStates.ASK_TAX_INFO
            elif expected_state == FSMStates.ASK_TAX_INFO:
                fsm.answers["is_tax_filer"] = True
                fsm.answers["annual_income"] = 1500000
                fsm.current_state = FSMStates.ASK_BALANCE
            elif expected_state == FSMStates.ASK_BALANCE:
                fsm.answers["closing_balance"] = 2000000
                fsm.current_state = FSMStates.ASK_TRAVEL
            elif expected_state == FSMStates.ASK_TRAVEL:
                fsm.answers["travel_history"] = user_input
                fsm.current_state = FSMStates.EVALUATION
        
        print(f"Current state: {fsm.current_state.value}")
        print("-" * 30)
    
    # Test evaluation
    if fsm.current_state == FSMStates.EVALUATION:
        evaluation = fsm.evaluate_profile(fsm.answers)
        print(f"Evaluation score: {evaluation.get('score', 0)}/{evaluation.get('max_score', 100)}")
        print(f"Eligible: {evaluation.get('eligible', False)}")


async def main():
    """Run all tests"""
    print("🚀 Starting Robust Handling Tests")
    print("=" * 60)
    
    await test_travel_history_handling()
    await test_off_track_handling()
    await test_numeric_extraction()
    await test_openai_parsing()
    await test_complete_flow()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 
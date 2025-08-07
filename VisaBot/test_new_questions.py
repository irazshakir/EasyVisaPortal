#!/usr/bin/env python3
"""
Test script to verify new questions (last travel year and valid visa)
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_new_questions():
    """Test the new questions functionality"""
    
    print("=== Testing New Questions ===")
    
    # Create FSM service
    fsm_service = FSMService()
    session_id = f"test_new_questions_{asyncio.get_event_loop().time()}"
    
    # Test flow with travel history that includes target countries
    test_flow = [
        ("germany", "Country selection"),
        ("business person", "Profession"),
        ("sole proprietor", "Business type"),
        ("yes, I am a tax filer and my annual income is 1500000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited USA, Dubai, and Sri Lanka", "Travel history"),
        ("2023", "Last travel year"),
        ("yes, I have a valid USA visa", "Valid visa")
    ]
    
    print("\n--- Test Flow with Target Countries in Travel History ---")
    for i, (user_input, description) in enumerate(test_flow, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id, user_input, None)
        print(f"Current state: {result['current_state']}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print("\n=== Final State ===")
    final_state = await fsm_service.get_current_state(session_id)
    print(f"Final state: {final_state['current_state']}")
    print(f"All answers: {final_state['answers']}")
    
    # Verify new fields were stored
    if "last_travel_year" in final_state['answers']:
        print("✅ Last travel year was properly stored")
    else:
        print("❌ Last travel year was NOT stored")
    
    if "valid_visa" in final_state['answers']:
        print("✅ Valid visa was properly stored")
    else:
        print("❌ Valid visa was NOT stored")
    
    # Test 2: No travel history (should skip new questions)
    print("\n--- Test 2: No Travel History (Should Skip New Questions) ---")
    session_id_2 = f"test_no_travel_{asyncio.get_event_loop().time()}"
    
    test_flow_2 = [
        ("france", "Country selection"),
        ("job holder", "Profession"),
        ("50000", "Salary"),
        ("bank transfer", "Salary mode"),
        ("yes, I am a tax filer and my annual income is 800000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("no travel history", "Travel history")
    ]
    
    for i, (user_input, description) in enumerate(test_flow_2, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id_2, user_input, None)
        print(f"Current state: {result['current_state']}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print("\n=== Final State (No Travel) ===")
    final_state_2 = await fsm_service.get_current_state(session_id_2)
    print(f"Final state: {final_state_2['current_state']}")
    print(f"All answers: {final_state_2['answers']}")
    
    # Verify new fields were NOT stored (should be skipped)
    if "last_travel_year" not in final_state_2['answers']:
        print("✅ Last travel year correctly skipped (no travel history)")
    else:
        print("❌ Last travel year was incorrectly stored")
    
    if "valid_visa" not in final_state_2['answers']:
        print("✅ Valid visa correctly skipped (no target countries)")
    else:
        print("❌ Valid visa was incorrectly stored")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_new_questions()) 
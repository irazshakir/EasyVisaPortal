#!/usr/bin/env python3
"""
Test script to verify travel logic fix
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_travel_logic_fix():
    """Test the travel logic fix"""
    
    print("=== Testing Travel Logic Fix ===")
    
    # Create FSM service
    fsm_service = FSMService()
    session_id = f"test_travel_logic_{asyncio.get_event_loop().time()}"
    
    # Test 1: No travel history (should skip new questions)
    print("\n--- Test 1: No Travel History (Should Skip New Questions) ---")
    test_flow_1 = [
        ("germany", "Country selection"),
        ("business person", "Profession"),
        ("sole proprietor", "Business type"),
        ("yes, I am a tax filer and my annual income is 1500000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("no travel history", "Travel history")
    ]
    
    for i, (user_input, description) in enumerate(test_flow_1, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id, user_input, None)
        print(f"Current state: {result['current_state']}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print("\n=== Final State (No Travel) ===")
    final_state = await fsm_service.get_current_state(session_id)
    print(f"Final state: {final_state['current_state']}")
    print(f"All answers: {final_state['answers']}")
    
    # Verify new fields were NOT stored (should be skipped)
    if "last_travel_year" not in final_state['answers']:
        print("✅ Last travel year correctly skipped (no travel history)")
    else:
        print("❌ Last travel year was incorrectly stored")
    
    if "valid_visa" not in final_state['answers']:
        print("✅ Valid visa correctly skipped (no target countries)")
    else:
        print("❌ Valid visa was incorrectly stored")
    
    # Test 2: Travel history with target countries (should ask new questions)
    print("\n--- Test 2: Travel History with Target Countries (Should Ask New Questions) ---")
    session_id_2 = f"test_travel_with_target_{asyncio.get_event_loop().time()}"
    
    test_flow_2 = [
        ("france", "Country selection"),
        ("job holder", "Profession"),
        ("50000", "Salary"),
        ("bank transfer", "Salary mode"),
        ("yes, I am a tax filer and my annual income is 800000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited USA, Dubai, and Sri Lanka", "Travel history"),
        ("2023", "Last travel year"),
        ("yes, I have a valid USA visa", "Valid visa")
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
    
    print("\n=== Final State (With Travel) ===")
    final_state_2 = await fsm_service.get_current_state(session_id_2)
    print(f"Final state: {final_state_2['current_state']}")
    print(f"All answers: {final_state_2['answers']}")
    
    # Verify new fields were stored
    if "last_travel_year" in final_state_2['answers']:
        print("✅ Last travel year was properly stored")
    else:
        print("❌ Last travel year was NOT stored")
    
    if "valid_visa" in final_state_2['answers']:
        print("✅ Valid visa was properly stored")
    else:
        print("❌ Valid visa was NOT stored")
    
    # Test 3: Travel history without target countries (should ask last travel year but skip valid visa)
    print("\n--- Test 3: Travel History without Target Countries (Should Ask Last Travel Year, Skip Valid Visa) ---")
    session_id_3 = f"test_travel_no_target_{asyncio.get_event_loop().time()}"
    
    test_flow_3 = [
        ("italy", "Country selection"),
        ("business person", "Profession"),
        ("private limited company", "Business type"),
        ("yes, I am a tax filer and my annual income is 1200000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited Dubai, Sri Lanka, and Thailand", "Travel history"),
        ("2022", "Last travel year")
    ]
    
    for i, (user_input, description) in enumerate(test_flow_3, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id_3, user_input, None)
        print(f"Current state: {result['current_state']}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print("\n=== Final State (Travel without Target Countries) ===")
    final_state_3 = await fsm_service.get_current_state(session_id_3)
    print(f"Final state: {final_state_3['current_state']}")
    print(f"All answers: {final_state_3['answers']}")
    
    # Verify last travel year was stored but valid visa was skipped
    if "last_travel_year" in final_state_3['answers']:
        print("✅ Last travel year was properly stored")
    else:
        print("❌ Last travel year was NOT stored")
    
    if "valid_visa" not in final_state_3['answers']:
        print("✅ Valid visa correctly skipped (no target countries in travel history)")
    else:
        print("❌ Valid visa was incorrectly stored")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_travel_logic_fix()) 
#!/usr/bin/env python3
"""
Test script to verify Schengen rejection question
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_schengen_rejection():
    """Test the Schengen rejection question functionality"""
    
    print("=== Testing Schengen Rejection Question ===")
    
    # Create FSM service
    fsm_service = FSMService()
    session_id = f"test_schengen_rejection_{asyncio.get_event_loop().time()}"
    
    # Test 1: Complete flow with Schengen rejection
    print("\n--- Test 1: Complete Flow with Schengen Rejection ---")
    test_flow_1 = [
        ("germany", "Country selection"),
        ("business person", "Profession"),
        ("sole proprietor", "Business type"),
        ("yes, I am a tax filer and my annual income is 1500000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited USA, Dubai, and Sri Lanka", "Travel history"),
        ("2023", "Last travel year"),
        ("yes, I have a valid USA visa", "Valid visa"),
        ("yes, I was rejected in 2022", "Schengen rejection")
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
    
    print("\n=== Final State (With Schengen Rejection) ===")
    final_state = await fsm_service.get_current_state(session_id)
    print(f"Final state: {final_state['current_state']}")
    print(f"All answers: {final_state['answers']}")
    
    # Verify Schengen rejection was stored
    if "schengen_rejection" in final_state['answers']:
        print("✅ Schengen rejection was properly stored")
        print(f"Schengen rejection data: {final_state['answers']['schengen_rejection']}")
    else:
        print("❌ Schengen rejection was NOT stored")
    
    # Test 2: No Schengen rejection
    print("\n--- Test 2: No Schengen Rejection ---")
    session_id_2 = f"test_no_schengen_rejection_{asyncio.get_event_loop().time()}"
    
    test_flow_2 = [
        ("france", "Country selection"),
        ("job holder", "Profession"),
        ("50000", "Salary"),
        ("bank transfer", "Salary mode"),
        ("yes, I am a tax filer and my annual income is 800000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited Dubai and Sri Lanka", "Travel history"),
        ("2022", "Last travel year"),
        ("no, never had any rejections", "Schengen rejection")
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
    
    print("\n=== Final State (No Schengen Rejection) ===")
    final_state_2 = await fsm_service.get_current_state(session_id_2)
    print(f"Final state: {final_state_2['current_state']}")
    print(f"All answers: {final_state_2['answers']}")
    
    # Verify Schengen rejection was stored
    if "schengen_rejection" in final_state_2['answers']:
        print("✅ Schengen rejection was properly stored")
        print(f"Schengen rejection data: {final_state_2['answers']['schengen_rejection']}")
    else:
        print("❌ Schengen rejection was NOT stored")
    
    # Test 3: No travel history (should still ask Schengen rejection)
    print("\n--- Test 3: No Travel History (Should Still Ask Schengen Rejection) ---")
    session_id_3 = f"test_no_travel_schengen_{asyncio.get_event_loop().time()}"
    
    test_flow_3 = [
        ("italy", "Country selection"),
        ("business person", "Profession"),
        ("private limited company", "Business type"),
        ("yes, I am a tax filer and my annual income is 1200000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("no travel history", "Travel history"),
        ("no, never applied before", "Schengen rejection")
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
    
    print("\n=== Final State (No Travel, No Schengen Rejection) ===")
    final_state_3 = await fsm_service.get_current_state(session_id_3)
    print(f"Final state: {final_state_3['current_state']}")
    print(f"All answers: {final_state_3['answers']}")
    
    # Verify Schengen rejection was stored
    if "schengen_rejection" in final_state_3['answers']:
        print("✅ Schengen rejection was properly stored")
        print(f"Schengen rejection data: {final_state_3['answers']['schengen_rejection']}")
    else:
        print("❌ Schengen rejection was NOT stored")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_schengen_rejection()) 
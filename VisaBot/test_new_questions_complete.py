#!/usr/bin/env python3
"""
Test script to verify all new questions (age, business premises, business online presence)
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_new_questions_complete():
    """Test all the new questions functionality"""
    
    print("=== Testing All New Questions ===")
    
    # Create FSM service
    fsm_service = FSMService()
    
    # Test 1: Business person flow (should ask all business questions)
    print("\n--- Test 1: Business Person Flow (Should Ask All Business Questions) ---")
    session_id_1 = f"test_business_person_{asyncio.get_event_loop().time()}"
    
    test_flow_1 = [
        ("germany", "Country selection"),
        ("business person", "Profession"),
        ("sole proprietor", "Business type"),
        ("yes, I am a tax filer and my annual income is 1500000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited USA, Dubai, and Sri Lanka", "Travel history"),
        ("2023", "Last travel year"),
        ("yes, I have a valid USA visa", "Valid visa"),
        ("no, never had any rejections", "Schengen rejection"),
        ("35", "Age"),
        ("yes, I have an office with 5 employees", "Business premises"),
        ("yes, I have a website and Facebook page", "Business online presence")
    ]
    
    for i, (user_input, description) in enumerate(test_flow_1, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id_1, user_input, None)
        print(f"Current state: {result['current_state']}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print("\n=== Final State (Business Person) ===")
    final_state_1 = await fsm_service.get_current_state(session_id_1)
    print(f"Final state: {final_state_1['current_state']}")
    print(f"All answers: {final_state_1['answers']}")
    
    # Verify all new fields were stored
    if "age" in final_state_1['answers']:
        print("✅ Age was properly stored")
    else:
        print("❌ Age was NOT stored")
    
    if "business_premises" in final_state_1['answers']:
        print("✅ Business premises was properly stored")
    else:
        print("❌ Business premises was NOT stored")
    
    if "business_online_presence" in final_state_1['answers']:
        print("✅ Business online presence was properly stored")
    else:
        print("❌ Business online presence was NOT stored")
    
    # Test 2: Job holder flow (should ask age but skip business questions)
    print("\n--- Test 2: Job Holder Flow (Should Ask Age, Skip Business Questions) ---")
    session_id_2 = f"test_job_holder_{asyncio.get_event_loop().time()}"
    
    test_flow_2 = [
        ("france", "Country selection"),
        ("job holder", "Profession"),
        ("50000", "Salary"),
        ("bank transfer", "Salary mode"),
        ("yes, I am a tax filer and my annual income is 800000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("I have visited Dubai and Sri Lanka", "Travel history"),
        ("2022", "Last travel year"),
        ("no, never had any rejections", "Schengen rejection"),
        ("28", "Age")
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
    
    print("\n=== Final State (Job Holder) ===")
    final_state_2 = await fsm_service.get_current_state(session_id_2)
    print(f"Final state: {final_state_2['current_state']}")
    print(f"All answers: {final_state_2['answers']}")
    
    # Verify age was stored but business questions were skipped
    if "age" in final_state_2['answers']:
        print("✅ Age was properly stored")
    else:
        print("❌ Age was NOT stored")
    
    if "business_premises" not in final_state_2['answers']:
        print("✅ Business premises correctly skipped (not a business person)")
    else:
        print("❌ Business premises was incorrectly stored")
    
    if "business_online_presence" not in final_state_2['answers']:
        print("✅ Business online presence correctly skipped (not a business person)")
    else:
        print("❌ Business online presence was incorrectly stored")
    
    # Test 3: No travel history flow (should still ask all questions)
    print("\n--- Test 3: No Travel History Flow (Should Still Ask All Questions) ---")
    session_id_3 = f"test_no_travel_{asyncio.get_event_loop().time()}"
    
    test_flow_3 = [
        ("italy", "Country selection"),
        ("business person", "Profession"),
        ("private limited company", "Business type"),
        ("yes, I am a tax filer and my annual income is 1200000", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance"),
        ("no travel history", "Travel history"),
        ("no, never applied before", "Schengen rejection"),
        ("42", "Age"),
        ("no, I work from home", "Business premises"),
        ("no, I don't have online presence", "Business online presence")
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
    
    print("\n=== Final State (No Travel, Business Person) ===")
    final_state_3 = await fsm_service.get_current_state(session_id_3)
    print(f"Final state: {final_state_3['current_state']}")
    print(f"All answers: {final_state_3['answers']}")
    
    # Verify all fields were stored
    if "age" in final_state_3['answers']:
        print("✅ Age was properly stored")
    else:
        print("❌ Age was NOT stored")
    
    if "business_premises" in final_state_3['answers']:
        print("✅ Business premises was properly stored")
    else:
        print("❌ Business premises was NOT stored")
    
    if "business_online_presence" in final_state_3['answers']:
        print("✅ Business online presence was properly stored")
    else:
        print("❌ Business online presence was NOT stored")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_new_questions_complete()) 
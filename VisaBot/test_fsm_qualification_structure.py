#!/usr/bin/env python3
"""
Test script to verify FSM follows proper qualification structure
and doesn't skip any questions, especially travel history
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_fsm_qualification_structure():
    """Test that FSM follows proper qualification structure"""
    
    print("=== Testing FSM Qualification Structure ===")
    
    # Create FSM service
    fsm_service = FSMService()
    
    # Test 1: Complete Business Person Flow (Should follow all questions)
    print("\n--- Test 1: Complete Business Person Flow ---")
    session_id_1 = f"test_business_complete_{asyncio.get_event_loop().time()}"
    
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
    
    expected_states = [
        "ask_country",
        "ask_profession", 
        "ask_business_type",
        "ask_tax_info",
        "ask_balance",
        "ask_travel",
        "ask_last_travel_year",
        "ask_valid_visa",
        "ask_schengen_rejection",
        "ask_age",
        "ask_business_premises",
        "ask_business_online_presence",
        "evaluation"
    ]
    
    actual_states = []
    
    for i, (user_input, description) in enumerate(test_flow_1, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id_1, user_input, None)
        current_state = result['current_state']
        actual_states.append(current_state)
        
        print(f"Current state: {current_state}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print(f"\nExpected states: {expected_states}")
    print(f"Actual states: {actual_states}")
    
    # Verify all expected states were visited
    missing_states = set(expected_states) - set(actual_states)
    if missing_states:
        print(f"❌ Missing states: {missing_states}")
    else:
        print("✅ All expected states were visited")
    
    # Test 2: Job Holder Flow (Should skip business questions)
    print("\n--- Test 2: Job Holder Flow ---")
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
    
    expected_states_2 = [
        "ask_country",
        "ask_profession",
        "ask_salary",
        "ask_salary_mode", 
        "ask_tax_info",
        "ask_balance",
        "ask_travel",
        "ask_last_travel_year",
        "ask_schengen_rejection",
        "ask_age",
        "evaluation"
    ]
    
    actual_states_2 = []
    
    for i, (user_input, description) in enumerate(test_flow_2, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id_2, user_input, None)
        current_state = result['current_state']
        actual_states_2.append(current_state)
        
        print(f"Current state: {current_state}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print(f"\nExpected states (Job Holder): {expected_states_2}")
    print(f"Actual states (Job Holder): {actual_states_2}")
    
    # Verify all expected states were visited
    missing_states_2 = set(expected_states_2) - set(actual_states_2)
    if missing_states_2:
        print(f"❌ Missing states: {missing_states_2}")
    else:
        print("✅ All expected states were visited")
    
    # Test 3: No Travel History Flow (Should skip travel-related questions)
    print("\n--- Test 3: No Travel History Flow ---")
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
    
    expected_states_3 = [
        "ask_country",
        "ask_profession",
        "ask_business_type",
        "ask_tax_info",
        "ask_balance", 
        "ask_travel",
        "ask_schengen_rejection",
        "ask_age",
        "ask_business_premises",
        "ask_business_online_presence",
        "evaluation"
    ]
    
    actual_states_3 = []
    
    for i, (user_input, description) in enumerate(test_flow_3, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id_3, user_input, None)
        current_state = result['current_state']
        actual_states_3.append(current_state)
        
        print(f"Current state: {current_state}")
        print(f"Question: {result['question'][:100]}...")
        print(f"Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("✅ Evaluation complete!")
            break
    
    print(f"\nExpected states (No Travel): {expected_states_3}")
    print(f"Actual states (No Travel): {actual_states_3}")
    
    # Verify all expected states were visited
    missing_states_3 = set(expected_states_3) - set(actual_states_3)
    if missing_states_3:
        print(f"❌ Missing states: {missing_states_3}")
    else:
        print("✅ All expected states were visited")
    
    # Test 4: Verify Travel History Question is Always Asked
    print("\n--- Test 4: Verify Travel History Question is Always Asked ---")
    
    # Check final states to ensure travel_history is stored
    final_state_1 = await fsm_service.get_current_state(session_id_1)
    final_state_2 = await fsm_service.get_current_state(session_id_2)
    final_state_3 = await fsm_service.get_current_state(session_id_3)
    
    print(f"\nBusiness Person - Travel History: {final_state_1['answers'].get('travel_history')}")
    print(f"Job Holder - Travel History: {final_state_2['answers'].get('travel_history')}")
    print(f"No Travel - Travel History: {final_state_3['answers'].get('travel_history')}")
    
    # Verify travel_history is stored in all cases
    if "travel_history" in final_state_1['answers']:
        print("✅ Business Person: Travel history stored")
    else:
        print("❌ Business Person: Travel history NOT stored")
    
    if "travel_history" in final_state_2['answers']:
        print("✅ Job Holder: Travel history stored")
    else:
        print("❌ Job Holder: Travel history NOT stored")
    
    if "travel_history" in final_state_3['answers']:
        print("✅ No Travel: Travel history stored")
    else:
        print("❌ No Travel: Travel history NOT stored")
    
    # Test 5: Verify All Required Information is Passed to Evaluation
    print("\n--- Test 5: Verify All Required Information is Passed to Evaluation ---")
    
    required_fields = [
        "selected_country", "profession", "is_tax_filer", "closing_balance", 
        "travel_history", "schengen_rejection", "age"
    ]
    
    business_fields = required_fields + ["business_type", "business_premises", "business_online_presence"]
    job_fields = required_fields + ["salary", "salary_mode"]
    
    print(f"\nBusiness Person - All fields: {list(final_state_1['answers'].keys())}")
    print(f"Job Holder - All fields: {list(final_state_2['answers'].keys())}")
    print(f"No Travel - All fields: {list(final_state_3['answers'].keys())}")
    
    # Check if all required fields are present
    missing_business = set(business_fields) - set(final_state_1['answers'].keys())
    missing_job = set(job_fields) - set(final_state_2['answers'].keys())
    missing_no_travel = set(business_fields) - set(final_state_3['answers'].keys())
    
    if not missing_business:
        print("✅ Business Person: All required fields present")
    else:
        print(f"❌ Business Person: Missing fields: {missing_business}")
    
    if not missing_job:
        print("✅ Job Holder: All required fields present")
    else:
        print(f"❌ Job Holder: Missing fields: {missing_job}")
    
    if not missing_no_travel:
        print("✅ No Travel: All required fields present")
    else:
        print(f"❌ No Travel: Missing fields: {missing_no_travel}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_fsm_qualification_structure()) 
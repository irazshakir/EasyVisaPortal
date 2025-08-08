#!/usr/bin/env python3
"""
Test script to specifically verify that the travel question is always asked
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_travel_question_specific():
    """Test that travel question is always asked"""
    
    print("=== Testing Travel Question is Always Asked ===")
    
    # Create FSM service
    fsm_service = FSMService()
    
    # Test 1: Simple flow to verify travel question is asked
    print("\n--- Test 1: Simple Flow to Verify Travel Question ---")
    session_id = f"test_travel_simple_{asyncio.get_event_loop().time()}"
    
    test_flow = [
        ("germany", "Country selection"),
        ("business person", "Profession"),
        ("sole proprietor", "Business type"),
        ("yes, I am a tax filer", "Tax info"),
        ("yes, I can manage 2 million PKR", "Balance")
    ]
    
    states_visited = []
    
    for i, (user_input, description) in enumerate(test_flow, 1):
        print(f"\n--- Step {i}: {description} ---")
        print(f"User input: '{user_input}'")
        
        result = await fsm_service.process_user_input(session_id, user_input, None)
        current_state = result['current_state']
        states_visited.append(current_state)
        
        print(f"Current state: {current_state}")
        print(f"Question: {result['question'][:100]}...")
        
        # Check if we're at the travel question
        if current_state == "ask_travel":
            print("✅ TRAVEL QUESTION FOUND!")
            print(f"Travel question: {result['question']}")
            break
    
    print(f"\nStates visited: {states_visited}")
    
    if "ask_travel" in states_visited:
        print("✅ Travel question was asked in the flow")
    else:
        print("❌ Travel question was NOT asked in the flow")
    
    # Test 2: Verify travel question is asked after balance
    print("\n--- Test 2: Verify Travel Question After Balance ---")
    
    # Get the current state to see what question is being asked
    current_state = await fsm_service.get_current_state(session_id)
    print(f"Current state after balance: {current_state['current_state']}")
    print(f"Current question: {current_state.get('current_question', 'No question found')}")
    
    if current_state['current_state'] == "ask_travel":
        print("✅ Travel question is correctly being asked after balance")
    else:
        print(f"❌ Expected 'ask_travel' but got '{current_state['current_state']}'")
    
    # Test 3: Answer travel question and verify next state
    print("\n--- Test 3: Answer Travel Question and Verify Next State ---")
    
    travel_answer = "I have visited Dubai and Sri Lanka"
    print(f"Travel answer: '{travel_answer}'")
    
    result = await fsm_service.process_user_input(session_id, travel_answer, None)
    print(f"Next state after travel: {result['current_state']}")
    print(f"Next question: {result['question'][:100]}...")
    
    if result['current_state'] == "ask_last_travel_year":
        print("✅ Correctly moved to last travel year question")
    else:
        print(f"❌ Expected 'ask_last_travel_year' but got '{result['current_state']}'")
    
    # Test 4: Verify travel history is stored
    print("\n--- Test 4: Verify Travel History is Stored ---")
    
    final_state = await fsm_service.get_current_state(session_id)
    travel_history = final_state['answers'].get('travel_history')
    print(f"Stored travel history: {travel_history}")
    
    if travel_history:
        print("✅ Travel history was properly stored")
    else:
        print("❌ Travel history was NOT stored")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_travel_question_specific()) 
#!/usr/bin/env python3
"""
Debug script to test FSM logic
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMStates, VisaEvaluationFSM, FSMService
from app.services.session_service import SessionService
from app.services.chat_service import ChatService
from app.models.chat import ChatRequest
from loguru import logger

async def debug_fsm():
    """Debug the FSM logic"""
    print("🔍 Debugging FSM Logic")
    print("=" * 50)
    
    # Test 1: Direct FSM instance
    print("\n1. Testing direct FSM instance...")
    fsm = VisaEvaluationFSM("test_session")
    print(f"   Initial state: {fsm.current_state.value}")
    print(f"   Initial question: {fsm.get_current_question()}")
    
    # Test state transition
    user_input = "business"
    print(f"\n   User input: {user_input}")
    
    # Store answer
    fsm.answers["profession"] = user_input
    print(f"   Stored answer: {fsm.answers}")
    
    # Get next state
    next_state, next_question = fsm.get_next_state(fsm.current_state, user_input)
    print(f"   Next state: {next_state.value}")
    print(f"   Next question: {next_question}")
    
    # Update state
    fsm.current_state = next_state
    print(f"   Updated state: {fsm.current_state.value}")
    
    # Test 2: FSM Service
    print("\n2. Testing FSM Service...")
    fsm_service = FSMService()
    
    # Process user input
    result = await fsm_service.process_user_input("test_session_2", "business")
    print(f"   FSM result: {result}")
    
    # Test 3: Chat Service
    print("\n3. Testing Chat Service...")
    chat_service = ChatService()
    
    # First message (should get initial question)
    request1 = ChatRequest(session_id=None, message="hello")
    response1 = await chat_service.process_chat_message(request1)
    print(f"   First response: {response1.message}")
    print(f"   Session ID: {response1.session_id}")
    print(f"   State: {response1.state}")
    
    # Second message (should process answer and move to next state)
    request2 = ChatRequest(session_id=response1.session_id, message="business")
    response2 = await chat_service.process_chat_message(request2)
    print(f"   Second response: {response2.message}")
    print(f"   State: {response2.state}")
    
    # Third message (should be in next state)
    request3 = ChatRequest(session_id=response1.session_id, message="Yes, I am a tax filer. My income is 1.5 million PKR")
    response3 = await chat_service.process_chat_message(request3)
    print(f"   Third response: {response3.message}")
    print(f"   State: {response3.state}")

if __name__ == "__main__":
    asyncio.run(debug_fsm()) 
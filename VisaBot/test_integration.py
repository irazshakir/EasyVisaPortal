#!/usr/bin/env python3
"""
Integration test for the complete chat flow with new greeting and country selection
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.chat_service import chat_service
from app.models.chat import ChatRequest

async def test_complete_flow():
    """Test the complete chat flow"""
    
    print("=== Testing Complete Chat Flow ===\n")
    
    # Test 1: First message - should get greeting
    print("Test 1: First message")
    session_id = "test_integration_1"
    request = ChatRequest(session_id=session_id, message="Hello")
    
    response = await chat_service.process_chat_message(request)
    print(f"Response: {response.message}")
    print(f"State: {response.state}")
    print()
    
    # Test 2: User mentions supported country (France)
    print("Test 2: User mentions France")
    request = ChatRequest(session_id=session_id, message="France")
    
    response = await chat_service.process_chat_message(request)
    print(f"Response: {response.message}")
    print(f"State: {response.state}")
    print()
    
    # Test 3: User mentions non-supported country (USA)
    print("Test 3: User mentions USA")
    session_id_2 = "test_integration_2"
    request = ChatRequest(session_id=session_id_2, message="Hello")
    
    response = await chat_service.process_chat_message(request)
    print(f"Greeting: {response.message}")
    print(f"State: {response.state}")
    print()
    
    request = ChatRequest(session_id=session_id_2, message="USA")
    response = await chat_service.process_chat_message(request)
    print(f"Response: {response.message}")
    print(f"State: {response.state}")
    print()
    
    # Test 4: User accepts Schengen offer
    print("Test 4: User accepts Schengen offer")
    request = ChatRequest(session_id=session_id_2, message="Yes, I want to try Schengen")
    response = await chat_service.process_chat_message(request)
    print(f"Response: {response.message}")
    print(f"State: {response.state}")
    print()
    
    print("=== Integration Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_complete_flow()) 
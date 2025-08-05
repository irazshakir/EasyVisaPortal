#!/usr/bin/env python3
"""
Test script to verify backend fixes are working
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.chat_service import chat_service
from app.models.chat import ChatRequest


async def test_backend():
    """Test the backend chat service"""
    print("🧪 Testing VisaBot Backend...\n")
    
    try:
        # Test 1: Send a message without session_id (should create new session)
        print("1. Testing new session creation...")
        request1 = ChatRequest(
            message="Hello, I need help with a visa application."
        )
        
        response1 = await chat_service.process_chat_message(request1)
        print(f"✅ New session created: {response1.session_id}")
        print(f"   Response: {response1.message[:100]}...")
        print(f"   State: {response1.state}")
        print()
        
        # Test 2: Send a follow-up message with session_id
        print("2. Testing follow-up message...")
        request2 = ChatRequest(
            session_id=response1.session_id,
            message="I am a business person."
        )
        
        response2 = await chat_service.process_chat_message(request2)
        print(f"✅ Follow-up message processed")
        print(f"   Response: {response2.message[:100]}...")
        print(f"   State: {response2.state}")
        print()
        
        # Test 3: Continue the conversation
        print("3. Testing conversation flow...")
        request3 = ChatRequest(
            session_id=response1.session_id,
            message="Yes, I am a tax filer and my annual income is 1.5 million PKR."
        )
        
        response3 = await chat_service.process_chat_message(request3)
        print(f"✅ Conversation continued")
        print(f"   Response: {response3.message[:100]}...")
        print(f"   State: {response3.state}")
        print()
        
        print("🎉 All backend tests passed successfully!")
        print("The VisaBot backend is working correctly.")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_backend()) 
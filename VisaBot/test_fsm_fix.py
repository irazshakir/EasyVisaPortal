"""
Test script to debug FSM state storage issues
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates
from app.services.redis_service import redis_client


async def test_specific_issue():
    """Test the specific issue with tax state not updating"""
    print("\n=== Testing Specific Tax Issue ===")
    
    fsm_service = FSMService()
    session_id = "test_tax_issue"
    
    # Clear any existing session
    await redis_client.delete(f"fsm:{session_id}")
    
    # Simulate the exact conversation from the user
    inputs = [
        "germany",
        "business", 
        "sole proprietor",
        "yes",
        "yes",
        "yes , annual income i dont remember"
    ]
    
    for i, user_input in enumerate(inputs, 1):
        print(f"\n{i}. Input: '{user_input}'")
        result = await fsm_service.process_user_input(session_id, user_input, None)
        print(f"   State: {result['current_state']}")
        print(f"   Question: {result['question'][:100]}...")
        print(f"   Answers: {result['answers']}")
        
        if result.get('is_complete'):
            print("   ✅ Evaluation complete!")
            break


async def test_tax_handling():
    """Test tax handling specifically"""
    print("\n=== Testing Tax Handling ===")
    
    fsm_service = FSMService()
    session_id = "test_tax_handling"
    
    # Clear any existing session
    await redis_client.delete(f"fsm:{session_id}")
    
    # Test different tax responses
    test_cases = [
        ("yes", "Simple yes"),
        ("yes, 500000", "Yes with income"),
        ("no", "Simple no"),
        ("yes , annual income i dont remember", "Yes with unclear income")
    ]
    
    for user_input, description in test_cases:
        print(f"\nTesting: {description} - '{user_input}'")
        result = await fsm_service.process_user_input(session_id, user_input, None)
        print(f"   State: {result['current_state']}")
        print(f"   Answers: {result['answers']}")
        
        # Check if tax info was stored correctly
        if "is_tax_filer" in result['answers']:
            print(f"   ✅ Tax filer status stored: {result['answers']['is_tax_filer']}")
        if "annual_income" in result['answers']:
            print(f"   ✅ Annual income stored: {result['answers']['annual_income']}")
        if "tax_response" in result['answers']:
            print(f"   ✅ Tax response stored: {result['answers']['tax_response']}")


if __name__ == "__main__":
    asyncio.run(test_specific_issue())
    asyncio.run(test_tax_handling()) 
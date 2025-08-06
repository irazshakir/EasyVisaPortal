"""
Simple test to verify tax state storage fix
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.fsm_service import FSMService, FSMStates


async def test_tax_fix():
    """Test the tax state storage fix"""
    print("=== Testing Tax State Storage Fix ===")
    
    fsm_service = FSMService()
    session_id = "test_tax_fix_123"
    
    # Test the exact scenario from the user
    inputs = [
        "germany",
        "business", 
        "sole proprietor",
        "yes"  # This should now be properly stored
    ]
    
    for i, user_input in enumerate(inputs, 1):
        print(f"\n{i}. Input: '{user_input}'")
        result = await fsm_service.process_user_input(session_id, user_input, None)
        print(f"   State: {result['current_state']}")
        print(f"   Answers: {result['answers']}")
        
        # Check if we moved past the tax question
        if result['current_state'] != 'ask_tax_info':
            print(f"   ✅ Successfully moved past tax question to: {result['current_state']}")
        else:
            print(f"   ❌ Still stuck on tax question")


if __name__ == "__main__":
    asyncio.run(test_tax_fix()) 
#!/usr/bin/env python3
"""
Test Redis connection
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.redis_service import redis_client
from loguru import logger

async def test_redis():
    """Test Redis connection and basic operations"""
    print("🔍 Testing Redis Connection")
    print("=" * 50)
    
    try:
        # Test connection
        print("\n1. Testing Redis connection...")
        await redis_client.connect()
        ping_result = await redis_client.ping()
        print(f"   Redis ping result: {ping_result}")
        
        # Test basic operations
        print("\n2. Testing basic Redis operations...")
        test_key = "test:visabot:session"
        test_data = {"state": "ask_profession", "answers": {"test": "value"}}
        
        # Set data
        await redis_client.set_session_data(test_key, test_data)
        print(f"   Set data for key: {test_key}")
        
        # Get data
        retrieved_data = await redis_client.get_session_data(test_key)
        print(f"   Retrieved data: {retrieved_data}")
        
        # Test state operations
        print("\n3. Testing state operations...")
        await redis_client.set_state("test_session", "ask_tax_info", {"answers": {"profession": "business"}})
        state_data = await redis_client.get_state("test_session")
        print(f"   State data: {state_data}")
        
        # Clean up
        await redis_client.delete_session_data(test_key)
        await redis_client.delete_session_data("test_session:state")
        print("\n   Cleaned up test data")
        
        print("\n✅ Redis test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Redis test failed: {e}")
        logger.error(f"Redis test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis()) 
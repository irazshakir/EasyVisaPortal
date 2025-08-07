#!/usr/bin/env python3
"""
VisaBot Startup and Test Script
"""
import asyncio
import json
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import settings
from app.services.redis_service import redis_client
from app.core.database import init_database, create_tables
from app.services.chat_service import ChatService
from app.services.session_service import SessionService
from loguru import logger


async def test_redis_connection():
    """Test Redis connection"""
    try:
        await redis_client.ping()
        logger.info("✅ Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False


async def test_database_connection():
    """Test database connection"""
    try:
        await init_database()
        
        # Test connection with a simple query
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            from app.services.database_service import DatabaseService
            db_service = DatabaseService(session)
            connection_ok = await db_service.test_connection()
            
            if connection_ok:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def test_chat_service():
    """Test chat service functionality"""
    try:
        chat_service = ChatService()
        session_service = SessionService()
        
        # Create a test session
        session = await session_service.create_session()
        session_id = session.session_id
        
        # Test message processing
        response = await chat_service.process_message(
            session_id=session_id,
            message="Hello, I need help with visa application",
            context={"language": "en"}
        )
        
        logger.info(f"✅ Chat service test successful")
        logger.info(f"   Session ID: {response.session_id}")
        logger.info(f"   Bot Response: {response.message[:100]}...")
        logger.info(f"   Current State: {response.state}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Chat service test failed: {e}")
        return False


async def test_openai_service():
    """Test OpenAI service"""
    try:
        from app.services.openai_service import OpenAIService
        
        openai_service = OpenAIService()
        
        # Test intent analysis
        intent_result = await openai_service.analyze_intent("I want to apply for a tourist visa")
        
        logger.info(f"✅ OpenAI service test successful")
        logger.info(f"   Intent: {intent_result.get('intent')}")
        logger.info(f"   Confidence: {intent_result.get('confidence')}")
        
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI service test failed: {e}")
        return False


async def test_fsm_service():
    """Test FSM service"""
    try:
        from app.services.fsm_service import fsm_service
        
        # Test FSM functionality
        session_id = "test-fsm-session"
        
        # Get initial state
        state_info = await fsm_service.get_current_state(session_id)
        logger.info(f"   Initial state: {state_info['current_state']}")
        
        # Test transition
        await fsm_service.transition(session_id, "start")
        state_info = await fsm_service.get_current_state(session_id)
        logger.info(f"   After transition: {state_info['current_state']}")
        
        logger.info("✅ FSM service test successful")
        return True
    except Exception as e:
        logger.error(f"❌ FSM service test failed: {e}")
        return False


async def run_integration_test():
    """Run a complete integration test"""
    logger.info("🚀 Starting VisaBot Integration Test")
    logger.info("=" * 50)
    
    # Test all components
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Database Connection", test_database_connection),
        ("OpenAI Service", test_openai_service),
        ("FSM Service", test_fsm_service),
        ("Chat Service", test_chat_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Results Summary:")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! VisaBot is ready to use.")
        return True
    else:
        logger.warning("⚠️  Some tests failed. Please check the configuration.")
        return False


async def start_bot():
    """Start the VisaBot application"""
    logger.info("🚀 Starting VisaBot...")
    
    # Check if required environment variables are set
    if not settings.OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY is not set. Please check your .env file.")
        return False
    
    # Run integration test
    test_passed = await run_integration_test()
    
    if test_passed:
        logger.info("\n🎉 VisaBot is ready!")
        logger.info("📝 Next steps:")
        logger.info("   1. Start the FastAPI server: python -m uvicorn app.main:app --reload")
        logger.info("   2. Open http://localhost:8000/docs to see the API documentation")
        logger.info("   3. Test the chat endpoint with your frontend")
        logger.info("   4. Check the FRONTEND_INTEGRATION.md for integration examples")
    
    return test_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(start_bot())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n👋 VisaBot startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Simple database connection test
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "app"))

from app.core.database import init_database, AsyncSessionLocal
from app.services.database_service import DatabaseService
from loguru import logger

async def test_db():
    """Test database connection"""
    try:
        logger.info("🔍 Testing database connection...")
        
        # Initialize database
        await init_database()
        
        # Test connection
        async with AsyncSessionLocal() as session:
            db_service = DatabaseService(session)
            connection_ok = await db_service.test_connection()
            
            if connection_ok:
                logger.info("✅ Database connection successful!")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db())
    if success:
        print("\n🎉 Database connection test passed!")
    else:
        print("\n💥 Database connection test failed!")
        sys.exit(1) 
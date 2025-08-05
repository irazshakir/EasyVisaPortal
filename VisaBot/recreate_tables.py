#!/usr/bin/env python3
"""
Simple table recreation script for VisaBot
This script will recreate all tables with the new schemas (safer option)
"""
import asyncio
import sys
from loguru import logger

# Add the app directory to the Python path
sys.path.append('.')

from app.core.database import init_database, create_tables


async def recreate_tables():
    """Recreate all tables with new schemas"""
    logger.info("🔄 Starting table recreation process...")
    
    try:
        # Initialize database connection
        await init_database()
        
        # Create tables (SQLAlchemy will handle existing tables)
        logger.info("🏗️ Creating/recreating tables...")
        await create_tables()
        
        logger.info("🎉 Tables recreated successfully!")
        
    except Exception as e:
        logger.error(f"❌ Table recreation failed: {e}")
        raise


if __name__ == "__main__":
    # Run the table recreation
    asyncio.run(recreate_tables()) 
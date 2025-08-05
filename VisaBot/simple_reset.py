#!/usr/bin/env python3
"""
Simple database reset script for VisaBot
This script uses the existing database functions to reset the database
"""
import asyncio
import sys
from sqlalchemy import text
from loguru import logger

# Add the app directory to the Python path
sys.path.append('.')

from app.core.database import init_database, create_tables


async def drop_tables_simple():
    """Drop tables using the existing database connection"""
    try:
        from app.core.database import engine
        if not engine:
            await init_database()
            from app.core.database import engine
        
        async with engine.begin() as conn:
            # Drop tables in the correct order (respecting foreign keys)
            tables_to_drop = [
                'visa_recommendations',
                'visa_evaluations', 
                'chat_messages',
                'chat_sessions',
                'users'
            ]
            
            for table in tables_to_drop:
                try:
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    logger.info(f"✅ Dropped table: {table}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not drop {table}: {e}")
            
            logger.info("🗑️ All tables dropped successfully")
            
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        raise


async def simple_reset():
    """Simple database reset"""
    logger.info("🔄 Starting simple database reset...")
    
    try:
        # Initialize database
        await init_database()
        
        # Drop existing tables
        logger.info("🗑️ Dropping existing tables...")
        await drop_tables_simple()
        
        # Create new tables
        logger.info("🏗️ Creating new tables...")
        await create_tables()
        
        logger.info("🎉 Database reset completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(simple_reset()) 
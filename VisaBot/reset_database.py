#!/usr/bin/env python3
"""
Database reset script for VisaBot
This script will drop all existing tables and recreate them with the new schemas
"""
import asyncio
import sys
from sqlalchemy import text
from loguru import logger

# Add the app directory to the Python path
sys.path.append('.')

from app.core.database import init_database, create_tables
from app.models.database import Base


async def get_engine():
    """Get the database engine"""
    from app.core.database import engine
    if not engine:
        await init_database()
        from app.core.database import engine
    return engine


async def drop_all_tables():
    """Drop all existing tables"""
    try:
        engine = await get_engine()
        async with engine.begin() as conn:
            # Get all table names
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%' 
                AND tablename NOT LIKE 'sql_%'
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                logger.info("No existing tables found to drop")
                return
            
            logger.info(f"Found {len(tables)} existing tables: {tables}")
            
            # Drop all tables
            for table in tables:
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                logger.info(f"Dropped table: {table}")
            
            logger.info("All existing tables dropped successfully")
            
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise


async def create_tables_with_engine():
    """Create all tables with new schemas"""
    try:
        engine = await get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created successfully with new schemas")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


async def verify_tables():
    """Verify that all tables were created correctly"""
    try:
        engine = await get_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%' 
                AND tablename NOT LIKE 'sql_%'
                ORDER BY tablename
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'users',
                'chat_sessions', 
                'chat_messages',
                'visa_evaluations',
                'visa_recommendations'
            ]
            
            logger.info(f"Created tables: {tables}")
            
            missing_tables = set(expected_tables) - set(tables)
            extra_tables = set(tables) - set(expected_tables)
            
            if missing_tables:
                logger.warning(f"Missing expected tables: {missing_tables}")
            
            if extra_tables:
                logger.warning(f"Extra tables found: {extra_tables}")
            
            if not missing_tables and not extra_tables:
                logger.info("✅ All expected tables created successfully!")
            else:
                logger.warning("⚠️ Some table mismatches detected")
                
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        raise


async def reset_database():
    """Main function to reset the database"""
    logger.info("🔄 Starting database reset process...")
    
    try:
        # Initialize database connection
        await init_database()
        
        # Drop all existing tables
        logger.info("🗑️ Dropping existing tables...")
        await drop_all_tables()
        
        # Create new tables
        logger.info("🏗️ Creating new tables...")
        await create_tables_with_engine()
        
        # Verify tables
        logger.info("✅ Verifying table creation...")
        await verify_tables()
        
        logger.info("🎉 Database reset completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise
    finally:
        # Close database connection
        try:
            engine = await get_engine()
            if engine:
                await engine.dispose()
                logger.info("Database connection closed")
        except:
            pass


if __name__ == "__main__":
    # Run the database reset
    asyncio.run(reset_database()) 
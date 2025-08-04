"""
Application event handlers
"""
from typing import Callable
from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.services.redis_service import redis_client
from app.core.database import init_database, create_tables, close_database


def create_start_app_handler(app: FastAPI) -> Callable:
    """Create startup event handler"""
    
    async def start_app() -> None:
        logger.info("Starting VisaBot application...")
        
        # Initialize Redis connection
        try:
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
        
        # Initialize database connection
        try:
            await init_database()
            await create_tables()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
        
        logger.info(f"VisaBot started successfully on {settings.HOST}:{settings.PORT}")
    
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """Create shutdown event handler"""
    
    async def stop_app() -> None:
        logger.info("Shutting down VisaBot application...")
        
        # Close Redis connection
        try:
            await redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
        
        # Close database connection
        try:
            await close_database()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
        
        logger.info("VisaBot shutdown complete")
    
    return stop_app 
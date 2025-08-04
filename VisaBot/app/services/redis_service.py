"""
Redis service for session and state management
"""
import json
import asyncio
from typing import Optional, Dict, Any
from redis.asyncio import Redis
from loguru import logger

from app.core.config import settings


class RedisService:
    """Redis service for managing sessions and state"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = Redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def set_session_data(self, session_id: str, data: Dict[str, Any], ttl: int = None):
        """Set session data in Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"session:{session_id}"
        await self.redis.set(key, json.dumps(data), ex=ttl or settings.BOT_SESSION_TIMEOUT)
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"session:{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def delete_session_data(self, session_id: str):
        """Delete session data from Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"session:{session_id}"
        await self.redis.delete(key)
    
    async def set_state(self, session_id: str, state: str, context: Dict[str, Any] = None):
        """Set FSM state for a session"""
        state_data = {
            "state": state,
            "context": context or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.set_session_data(f"{session_id}:state", state_data)
    
    async def get_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get FSM state for a session"""
        return await self.get_session_data(f"{session_id}:state")
    
    async def ping(self):
        """Ping Redis to check connection"""
        if not self.redis:
            await self.connect()
        return await self.redis.ping()


# Global Redis client instance
redis_client = RedisService() 
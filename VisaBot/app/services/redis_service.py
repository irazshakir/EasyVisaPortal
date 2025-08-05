"""
Redis service for session and state management - enhanced for visa evaluation bot
"""
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from redis.asyncio import Redis
from loguru import logger

from app.core.config import settings


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class RedisService:
    """Redis service for managing sessions and state - enhanced for visa evaluation bot"""
    
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
        await self.redis.set(key, json.dumps(data, cls=DateTimeEncoder), ex=ttl or settings.BOT_SESSION_TIMEOUT)
    
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
    
    # Enhanced methods for visa evaluation bot
    async def set_evaluation_data(self, session_id: str, evaluation_data: Dict[str, Any], ttl: int = None):
        """Store visa evaluation data in Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"evaluation:{session_id}"
        await self.redis.set(key, json.dumps(evaluation_data, cls=DateTimeEncoder), ex=ttl or settings.BOT_SESSION_TIMEOUT)
    
    async def get_evaluation_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get visa evaluation data from Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"evaluation:{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set_answers(self, session_id: str, answers: Dict[str, Any], ttl: int = None):
        """Store FSM answers in Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"answers:{session_id}"
        await self.redis.set(key, json.dumps(answers, cls=DateTimeEncoder), ex=ttl or settings.BOT_SESSION_TIMEOUT)
    
    async def get_answers(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get FSM answers from Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"answers:{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set_conversation_history(self, session_id: str, messages: list, ttl: int = None):
        """Store conversation history in Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"conversation:{session_id}"
        await self.redis.set(key, json.dumps(messages, cls=DateTimeEncoder), ex=ttl or settings.BOT_SESSION_TIMEOUT)
    
    async def get_conversation_history(self, session_id: str) -> Optional[list]:
        """Get conversation history from Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"conversation:{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def add_message_to_history(self, session_id: str, message: Dict[str, Any], ttl: int = None):
        """Add a message to conversation history"""
        history = await self.get_conversation_history(session_id) or []
        history.append(message)
        
        # Limit history length
        if len(history) > settings.MAX_CONVERSATION_HISTORY:
            history = history[-settings.MAX_CONVERSATION_HISTORY:]
        
        await self.set_conversation_history(session_id, history, ttl)
    
    async def clear_session_data(self, session_id: str):
        """Clear all session-related data from Redis"""
        if not self.redis:
            await self.connect()
        
        # Delete all keys related to this session
        keys_to_delete = [
            f"session:{session_id}",
            f"{session_id}:state",
            f"evaluation:{session_id}",
            f"answers:{session_id}",
            f"conversation:{session_id}"
        ]
        
        for key in keys_to_delete:
            await self.redis.delete(key)
        
        logger.info(f"Cleared all data for session: {session_id}")
    
    async def get_session_keys(self, session_id: str) -> list:
        """Get all Redis keys for a session"""
        if not self.redis:
            await self.connect()
        
        pattern = f"*{session_id}*"
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        
        return keys
    
    async def set_session_metadata(self, session_id: str, metadata: Dict[str, Any], ttl: int = None):
        """Store session metadata in Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"metadata:{session_id}"
        await self.redis.set(key, json.dumps(metadata, cls=DateTimeEncoder), ex=ttl or settings.BOT_SESSION_TIMEOUT)
    
    async def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata from Redis"""
        if not self.redis:
            await self.connect()
        
        key = f"metadata:{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def increment_session_counter(self, session_id: str, counter_name: str = "message_count") -> int:
        """Increment a counter for a session"""
        if not self.redis:
            await self.connect()
        
        key = f"counter:{session_id}:{counter_name}"
        return await self.redis.incr(key)
    
    async def get_session_counter(self, session_id: str, counter_name: str = "message_count") -> int:
        """Get a counter value for a session"""
        if not self.redis:
            await self.connect()
        
        key = f"counter:{session_id}:{counter_name}"
        value = await self.redis.get(key)
        return int(value) if value else 0
    
    async def set_session_ttl(self, session_id: str, ttl: int):
        """Set TTL for all session-related keys"""
        if not self.redis:
            await self.connect()
        
        keys = await self.get_session_keys(session_id)
        for key in keys:
            await self.redis.expire(key, ttl)
    
    async def ping(self):
        """Ping Redis to check connection"""
        if not self.redis:
            await self.connect()
        return await self.redis.ping()


# Global Redis client instance
redis_client = RedisService() 
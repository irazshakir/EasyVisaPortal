"""
Session service for managing chat sessions and history
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.services.redis_service import redis_client
from app.models.session import SessionInfo
from app.models.chat import ChatMessage, ConversationHistory


class SessionService:
    """Service for managing chat sessions"""
    
    async def create_session(self) -> SessionInfo:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        session_info = SessionInfo(
            session_id=session_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True
        )
        
        # Store session info in Redis
        await redis_client.set_session_data(
            f"session_info:{session_id}",
            session_info.dict()
        )
        
        # Initialize conversation history
        conversation = ConversationHistory(session_id=session_id)
        await redis_client.set_session_data(
            f"conversation:{session_id}",
            conversation.dict()
        )
        
        logger.info(f"Created new session: {session_id}")
        return session_info
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        session_data = await redis_client.get_session_data(f"session_info:{session_id}")
        
        if session_data:
            return SessionInfo(**session_data)
        return None
    
    async def get_or_create_session(self, session_id: Optional[str] = None) -> SessionInfo:
        """Get existing session or create new one"""
        if session_id:
            session = await self.get_session(session_id)
            if session:
                return session
        
        return await self.create_session()
    
    async def update_activity(self, session_id: str):
        """Update session last activity"""
        session = await self.get_session(session_id)
        if session:
            session.last_activity = datetime.utcnow()
            await redis_client.set_session_data(
                f"session_info:{session_id}",
                session.dict()
            )
    
    async def end_session(self, session_id: str):
        """End a session"""
        session = await self.get_session(session_id)
        if session:
            session.is_active = False
            await redis_client.set_session_data(
                f"session_info:{session_id}",
                session.dict()
            )
            logger.info(f"Ended session: {session_id}")
    
    async def delete_session(self, session_id: str):
        """Delete a session and all its data"""
        # Delete session info
        await redis_client.delete_session_data(f"session_info:{session_id}")
        
        # Delete conversation history
        await redis_client.delete_session_data(f"conversation:{session_id}")
        
        # Delete FSM state
        await redis_client.delete_session_data(f"{session_id}:state")
        
        logger.info(f"Deleted session: {session_id}")
    
    async def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions"""
        # Note: This is a simplified implementation
        # In a real application, you might want to use Redis SCAN or a database
        sessions = []
        
        # For now, return empty list as we don't have a way to list all sessions
        # without additional Redis operations or database storage
        return sessions
    
    async def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to session conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        
        # Get current conversation
        conversation_data = await redis_client.get_session_data(f"conversation:{session_id}")
        
        if conversation_data:
            conversation = ConversationHistory(**conversation_data)
        else:
            conversation = ConversationHistory(session_id=session_id)
        
        # Add message
        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()
        
        # Limit history length
        from app.core.config import settings
        if len(conversation.messages) > settings.MAX_CONVERSATION_HISTORY:
            conversation.messages = conversation.messages[-settings.MAX_CONVERSATION_HISTORY:]
        
        # Save updated conversation
        await redis_client.set_session_data(
            f"conversation:{session_id}",
            conversation.dict()
        )
    
    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session"""
        conversation_data = await redis_client.get_session_data(f"conversation:{session_id}")
        
        if conversation_data:
            conversation = ConversationHistory(**conversation_data)
            return conversation.messages
        
        return []
    
    async def clear_history(self, session_id: str):
        """Clear chat history for a session"""
        conversation = ConversationHistory(session_id=session_id)
        await redis_client.set_session_data(
            f"conversation:{session_id}",
            conversation.dict()
        )
        logger.info(f"Cleared history for session: {session_id}") 
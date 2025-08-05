"""
Session service for managing visa evaluation bot sessions
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.services.redis_service import redis_client
from app.models.session import SessionInfo
from app.models.chat import ChatMessage, ConversationHistory
from app.services.fsm_service import FSMStates


class SessionService:
    """Service for managing visa evaluation bot sessions"""
    
    def __init__(self):
        # In-memory session storage (as requested)
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(self) -> SessionInfo:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        session_info = SessionInfo(
            session_id=session_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True
        )
        
        # Initialize session data in memory
        self.sessions[session_id] = {
            "state": FSMStates.GREETING.value,
            "answers": {},
            "created_at": session_info.created_at,
            "last_activity": session_info.last_activity,
            "is_active": True
        }
        
        # Also store in Redis for persistence
        await redis_client.set_session_data(
            f"session_info:{session_id}",
            session_info.model_dump()
        )
        
        # Initialize conversation history
        conversation = ConversationHistory(session_id=session_id)
        await redis_client.set_session_data(
            f"conversation:{session_id}",
            conversation.model_dump()
        )
        
        logger.info(f"Created new session: {session_id}")
        return session_info
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information from memory"""
        return self.sessions.get(session_id)
    
    async def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
        """Get existing session or create new one. Returns (session_id, session_data)"""
        if session_id and session_id in self.sessions:
            session = await self.get_session(session_id)
            if session:
                await self.update_activity(session_id)
                return session_id, session
        
        # Create new session
        session_info = await self.create_session()
        return session_info.session_id, self.sessions[session_info.session_id]
    
    async def update_session(self, session_id: str, state: FSMStates, answer: Dict[str, Any]):
        """Update session state and answers"""
        if session_id in self.sessions:
            old_state = self.sessions[session_id]["state"]
            self.sessions[session_id]["state"] = state.value
            self.sessions[session_id]["answers"].update(answer)
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            
            logger.info(f"Updated session {session_id}: state={old_state} -> {state.value}")
            logger.info(f"Session answers: {self.sessions[session_id]['answers']}")
        else:
            logger.warning(f"Session {session_id} not found for update")
    
    async def update_activity(self, session_id: str):
        """Update session last activity"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
    
    async def reset_session(self, session_id: str):
        """Reset session to initial state"""
        if session_id in self.sessions:
            self.sessions[session_id]["state"] = FSMStates.GREETING.value
            self.sessions[session_id]["answers"] = {}
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            
            logger.info(f"Reset session {session_id} to initial state")
    
    async def end_session(self, session_id: str):
        """End a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["is_active"] = False
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            logger.info(f"Ended session: {session_id}")
    
    async def delete_session(self, session_id: str):
        """Delete a session and all its data"""
        # Remove from memory
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        # Delete from Redis
        await redis_client.delete_session_data(f"session_info:{session_id}")
        await redis_client.delete_session_data(f"conversation:{session_id}")
        await redis_client.delete_session_data(f"{session_id}:state")
        
        logger.info(f"Deleted session: {session_id}")
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        active_sessions = []
        for session_id, session_data in self.sessions.items():
            if session_data.get("is_active", True):
                active_sessions.append({
                    "session_id": session_id,
                    "state": session_data["state"],
                    "created_at": session_data["created_at"],
                    "last_activity": session_data["last_activity"]
                })
        return active_sessions
    
    async def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to session conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        
        # Get current conversation from Redis
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
        
        # Save updated conversation to Redis
        await redis_client.set_session_data(
            f"conversation:{session_id}",
            conversation.model_dump()
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
            conversation.model_dump()
        )
        logger.info(f"Cleared history for session: {session_id}")
    
    def get_session_state(self, session_id: str) -> Optional[FSMStates]:
        """Get current FSM state for session"""
        if session_id in self.sessions:
            state_value = self.sessions[session_id]["state"]
            try:
                return FSMStates(state_value)
            except ValueError:
                return FSMStates.ASK_PROFESSION
        return None
    
    def get_session_answers(self, session_id: str) -> Dict[str, Any]:
        """Get collected answers for session"""
        if session_id in self.sessions:
            return self.sessions[session_id]["answers"]
        return {}


# Global session service instance
session_service = SessionService() 
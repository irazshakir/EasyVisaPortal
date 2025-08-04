"""
Database service for persistent storage operations
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.database import (
    User, ChatSession, ChatMessage, VisaApplication, Document
)
from app.models.chat import ChatRequest, ChatResponse
from app.models.session import SessionInfo


class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Simple query to test connection
            from sqlalchemy import text
            result = await self.db.execute(text("SELECT 1"))
            result.fetchone()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # User operations
    async def create_user(self, email: str, full_name: str = None, phone: str = None, nationality: str = None, user_metadata: Dict[str, Any] = None) -> User:
        """Create a new user"""
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=full_name,
            phone=phone,
            nationality=nationality,
            user_metadata=user_metadata
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    # Chat session operations
    async def create_chat_session(self, session_id: str, user_id: str = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            current_state="greeting",
            context={},
            is_active=True
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by session ID"""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.session_id == session_id)
            .options(selectinload(ChatSession.messages))
        )
        return result.scalar_one_or_none()
    
    async def update_session_state(self, session_id: str, state: str, context: Dict[str, Any] = None):
        """Update session state and context"""
        await self.db.execute(
            update(ChatSession)
            .where(ChatSession.session_id == session_id)
            .values(
                current_state=state,
                context=context or {},
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
        )
        await self.db.commit()
    
    async def end_session(self, session_id: str):
        """End a chat session"""
        await self.db.execute(
            update(ChatSession)
            .where(ChatSession.session_id == session_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.db.commit()
    
    # Chat message operations
    async def add_message(self, session_id: str, role: str, content: str, message_metadata: Dict[str, Any] = None) -> ChatMessage:
        """Add a message to the database"""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=message_metadata
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat history for a session"""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order
    
    # Visa application operations
    async def create_visa_application(
        self,
        user_id: str,
        session_id: str,
        visa_type: str,
        destination_country: str,
        purpose_of_travel: str,
        travel_dates: Dict[str, str] = None
    ) -> VisaApplication:
        """Create a new visa application"""
        application = VisaApplication(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            application_number=f"VA{uuid.uuid4().hex[:8].upper()}",
            visa_type=visa_type,
            destination_country=destination_country,
            purpose_of_travel=purpose_of_travel,
            travel_dates=travel_dates,
            status="draft"
        )
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def get_visa_application(self, application_id: str) -> Optional[VisaApplication]:
        """Get visa application by ID"""
        result = await self.db.execute(
            select(VisaApplication)
            .where(VisaApplication.id == application_id)
            .options(selectinload(VisaApplication.documents))
        )
        return result.scalar_one_or_none()
    
    async def get_user_applications(self, user_id: str) -> List[VisaApplication]:
        """Get all applications for a user"""
        result = await self.db.execute(
            select(VisaApplication)
            .where(VisaApplication.user_id == user_id)
            .order_by(VisaApplication.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_application_status(self, application_id: str, status: str):
        """Update application status"""
        await self.db.execute(
            update(VisaApplication)
            .where(VisaApplication.id == application_id)
            .values(status=status, updated_at=datetime.utcnow())
        )
        await self.db.commit()
    
    # Document operations
    async def create_document(
        self,
        user_id: str,
        file_name: str,
        file_path: str,
        file_type: str,
        file_size: int,
        document_type: str,
        application_id: str = None,
        document_metadata: Dict[str, Any] = None
    ) -> Document:
        """Create a new document record"""
        document = Document(
            id=str(uuid.uuid4()),
            user_id=user_id,
            application_id=application_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            document_type=document_type,
            status="uploaded",
            document_metadata=document_metadata
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document
    
    async def get_documents_by_application(self, application_id: str) -> List[Document]:
        """Get all documents for an application"""
        result = await self.db.execute(
            select(Document)
            .where(Document.application_id == application_id)
            .order_by(Document.created_at.desc())
        )
        return result.scalars().all()
    
    # Analytics and reporting
    async def get_session_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get session statistics"""
        query = select(ChatSession)
        if user_id:
            query = query.where(ChatSession.user_id == user_id)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        return {
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s.is_active]),
            "completed_sessions": len([s for s in sessions if not s.is_active])
        }
    
    async def get_application_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get application statistics"""
        query = select(VisaApplication)
        if user_id:
            query = query.where(VisaApplication.user_id == user_id)
        
        result = await self.db.execute(query)
        applications = result.scalars().all()
        
        status_counts = {}
        for app in applications:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1
        
        return {
            "total_applications": len(applications),
            "status_breakdown": status_counts
        } 
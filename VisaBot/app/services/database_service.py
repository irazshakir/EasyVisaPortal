"""
Database service for persistent storage operations - aligned with FSM visa evaluation bot
"""
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.database import (
    User, ChatSession, ChatMessage, VisaEvaluation, VisaRecommendation
)
from app.models.chat import ChatRequest, ChatResponse
from app.models.session import SessionInfo
from app.services.fsm_service import FSMStates


class DatabaseService:
    """Service for database operations - aligned with FSM visa evaluation bot"""
    
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
    
    # Chat session operations - aligned with FSM states
    async def create_chat_session(self, session_id: str, user_id: str = None) -> ChatSession:
        """Create a new chat session with initial FSM state"""
        session = ChatSession(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            current_state=FSMStates.ASK_PROFESSION.value,  # Start with first FSM state
            context={"answers": {}, "evaluation": None},  # Initialize with empty answers
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
    
    async def update_session_state(self, session_id: str, state: FSMStates, context: Dict[str, Any] = None):
        """Update session state and context - aligned with FSM states"""
        await self.db.execute(
            update(ChatSession)
            .where(ChatSession.session_id == session_id)
            .values(
                current_state=state.value,
                context=context or {},
                updated_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
        )
        await self.db.commit()
    
    async def update_session_answers(self, session_id: str, answers: Dict[str, Any]):
        """Update session with collected answers from FSM"""
        session = await self.get_chat_session(session_id)
        if session:
            current_context = session.context or {}
            current_context["answers"] = answers
            await self.update_session_state(session_id, FSMStates(session.current_state), current_context)
    
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
    
    # Visa evaluation operations - aligned with FSM evaluation
    async def create_visa_evaluation(
        self,
        user_id: str,
        session_id: str,
        evaluation_data: Dict[str, Any],
        eligibility_score: int,
        eligibility_status: str,
        assessment_notes: str = None
    ) -> VisaEvaluation:
        """Create a new visa evaluation from FSM results"""
        evaluation = VisaEvaluation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            evaluation_number=f"VE{uuid.uuid4().hex[:8].upper()}",
            
            # Extract data from FSM evaluation
            visa_type=evaluation_data.get("visa_type", "general"),
            destination_country=evaluation_data.get("destination_country", "unknown"),
            purpose_of_travel=evaluation_data.get("purpose_of_travel", "evaluation"),
            
            # User profile from FSM answers
            employment_status=evaluation_data.get("answers", {}).get("profession"),
            financial_means=evaluation_data.get("answers", {}).get("balance_response"),
            
            # Evaluation results
            eligibility_score=eligibility_score,
            eligibility_status=eligibility_status,
            risk_level=self._calculate_risk_level(eligibility_score),
            
            # Store complete evaluation data
            evaluation_data=evaluation_data,
            assessment_notes=assessment_notes
        )
        self.db.add(evaluation)
        await self.db.commit()
        await self.db.refresh(evaluation)
        return evaluation
    
    async def get_visa_evaluation(self, evaluation_id: str) -> Optional[VisaEvaluation]:
        """Get visa evaluation by ID"""
        result = await self.db.execute(
            select(VisaEvaluation)
            .where(VisaEvaluation.id == evaluation_id)
            .options(selectinload(VisaEvaluation.recommendations))
        )
        return result.scalar_one_or_none()
    
    async def get_evaluation_by_session(self, session_id: str) -> Optional[VisaEvaluation]:
        """Get visa evaluation by session ID"""
        result = await self.db.execute(
            select(VisaEvaluation)
            .where(VisaEvaluation.session_id == session_id)
            .options(selectinload(VisaEvaluation.recommendations))
        )
        return result.scalar_one_or_none()
    
    async def get_user_evaluations(self, user_id: str) -> List[VisaEvaluation]:
        """Get all evaluations for a user"""
        result = await self.db.execute(
            select(VisaEvaluation)
            .where(VisaEvaluation.user_id == user_id)
            .order_by(VisaEvaluation.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_evaluation_status(self, evaluation_id: str, status: str):
        """Update evaluation status"""
        await self.db.execute(
            update(VisaEvaluation)
            .where(VisaEvaluation.id == evaluation_id)
            .values(eligibility_status=status, updated_at=datetime.utcnow())
        )
        await self.db.commit()
    
    # Visa recommendation operations
    async def create_visa_recommendation(
        self,
        evaluation_id: str,
        recommendation_type: str,
        title: str,
        description: str,
        action_items: List[str] = None,
        required_documents: List[str] = None,
        tips: List[str] = None,
        warnings: List[str] = None,
        priority: str = "medium"
    ) -> VisaRecommendation:
        """Create a recommendation based on evaluation results"""
        recommendation = VisaRecommendation(
            id=str(uuid.uuid4()),
            evaluation_id=evaluation_id,
            recommendation_type=recommendation_type,
            title=title,
            description=description,
            priority=priority,
            action_items=action_items,
            required_documents=required_documents,
            tips=tips,
            warnings=warnings
        )
        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)
        return recommendation
    
    async def get_evaluation_recommendations(self, evaluation_id: str) -> List[VisaRecommendation]:
        """Get all recommendations for an evaluation"""
        result = await self.db.execute(
            select(VisaRecommendation)
            .where(VisaRecommendation.evaluation_id == evaluation_id)
            .order_by(VisaRecommendation.created_at.desc())
        )
        return result.scalars().all()
    
    # Analytics and reporting - aligned with FSM states
    async def get_session_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get session statistics with FSM state breakdown"""
        query = select(ChatSession)
        if user_id:
            query = query.where(ChatSession.user_id == user_id)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        # Count sessions by FSM state
        state_counts = {}
        for session in sessions:
            state = session.current_state
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s.is_active]),
            "completed_sessions": len([s for s in sessions if not s.is_active]),
            "state_breakdown": state_counts
        }
    
    async def get_evaluation_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get evaluation statistics"""
        query = select(VisaEvaluation)
        if user_id:
            query = query.where(VisaEvaluation.user_id == user_id)
        
        result = await self.db.execute(query)
        evaluations = result.scalars().all()
        
        status_counts = {}
        score_ranges = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        
        for eval in evaluations:
            # Count by status
            status_counts[eval.eligibility_status] = status_counts.get(eval.eligibility_status, 0) + 1
            
            # Count by score range
            score = eval.eligibility_score or 0
            if score <= 25:
                score_ranges["0-25"] += 1
            elif score <= 50:
                score_ranges["26-50"] += 1
            elif score <= 75:
                score_ranges["51-75"] += 1
            else:
                score_ranges["76-100"] += 1
        
        return {
            "total_evaluations": len(evaluations),
            "status_breakdown": status_counts,
            "score_breakdown": score_ranges,
            "average_score": sum(e.eligibility_score or 0 for e in evaluations) / len(evaluations) if evaluations else 0
        }
    
    def _calculate_risk_level(self, score: int) -> str:
        """Calculate risk level based on eligibility score"""
        if score >= 70:
            return "low"
        elif score >= 50:
            return "medium"
        else:
            return "high" 
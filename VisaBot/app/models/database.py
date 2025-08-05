"""
SQLAlchemy database models for visa evaluation and guidance bot
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model for visa evaluation clients"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    user_metadata = Column(JSON, nullable=True)


class ChatSession(Base):
    """Chat session for visa evaluation conversation"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    current_state = Column(String, default="ask_profession")  # Updated to match FSM initial state
    context = Column(JSON, default={})  # Stores FSM evaluation context
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    user = relationship("User", back_populates="sessions")
    evaluations = relationship("VisaEvaluation", back_populates="session")


class ChatMessage(Base):
    """Individual chat message for evaluation conversation"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"), nullable=False)
    role = Column(String, nullable=False)  # "user", "assistant", "system" - aligned with database service
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Intent, confidence, evaluation step
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class VisaEvaluation(Base):
    """Visa evaluation results and assessment"""
    __tablename__ = "visa_evaluations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"), nullable=False)
    evaluation_number = Column(String, unique=True, index=True)
    
    # Evaluation criteria collected from FSM
    visa_type = Column(String, nullable=False)  # tourist, business, student, work, etc.
    destination_country = Column(String, nullable=False)
    purpose_of_travel = Column(String, nullable=False)
    travel_dates = Column(JSON, nullable=True)  # {"start": "2024-01-01", "end": "2024-01-15"}
    
    # User profile information from FSM answers
    nationality = Column(String, nullable=True)
    current_residence = Column(String, nullable=True)
    employment_status = Column(String, nullable=True)  # employed, student, retired, etc.
    financial_means = Column(String, nullable=True)  # sufficient, limited, etc.
    
    # Evaluation results
    eligibility_score = Column(Integer, nullable=True)  # 0-100 score
    eligibility_status = Column(String, nullable=False)  # eligible, not_eligible, conditional
    risk_level = Column(String, nullable=True)  # low, medium, high
    
    # Detailed assessment
    evaluation_data = Column(JSON, nullable=True)  # All collected evaluation data from FSM
    assessment_notes = Column(Text, nullable=True)  # Detailed assessment notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="evaluations")
    session = relationship("ChatSession", back_populates="evaluations")
    recommendations = relationship("VisaRecommendation", back_populates="evaluation")


class VisaRecommendation(Base):
    """Recommendations and guidance based on evaluation"""
    __tablename__ = "visa_recommendations"
    
    id = Column(String, primary_key=True, index=True)
    evaluation_id = Column(String, ForeignKey("visa_evaluations.id"), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String, nullable=False)  # proceed, reconsider, alternative_visa, etc.
    title = Column(String, nullable=False)  # "Proceed with Tourist Visa Application"
    description = Column(Text, nullable=False)  # Detailed recommendation
    priority = Column(String, default="medium")  # high, medium, low
    
    # Action items and guidance
    action_items = Column(JSON, nullable=True)  # List of specific actions to take
    required_documents = Column(JSON, nullable=True)  # List of documents needed
    timeline = Column(String, nullable=True)  # "Apply 3 months before travel"
    estimated_processing_time = Column(String, nullable=True)  # "2-4 weeks"
    
    # Additional guidance
    tips = Column(JSON, nullable=True)  # List of helpful tips
    warnings = Column(JSON, nullable=True)  # List of warnings/risks
    alternatives = Column(JSON, nullable=True)  # Alternative visa types or approaches
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    evaluation = relationship("VisaEvaluation", back_populates="recommendations")


# Add back references
User.sessions = relationship("ChatSession", back_populates="user")
User.evaluations = relationship("VisaEvaluation", back_populates="user") 
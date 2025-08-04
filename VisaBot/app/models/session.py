"""
Session-related Pydantic models
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


class SessionState(BaseModel):
    """Session state model for FSM"""
    session_id: str
    current_state: str
    context: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 
"""
Session management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.services.session_service import SessionService
from app.models.session import SessionInfo

router = APIRouter()


@router.post("/", response_model=SessionInfo)
async def create_session(
    session_service: SessionService = Depends(SessionService)
):
    """Create a new chat session"""
    try:
        session = await session_service.create_session()
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(SessionService)
):
    """Get session information"""
    try:
        session = await session_service.get_session(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/", response_model=List[SessionInfo])
async def list_sessions(
    session_service: SessionService = Depends(SessionService)
):
    """List all active sessions"""
    try:
        sessions = await session_service.list_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_service: SessionService = Depends(SessionService)
):
    """Delete a session"""
    try:
        await session_service.delete_session(session_id)
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found") 
"""
Chat endpoints for visa evaluation bot
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.chat_service import chat_service
from app.services.session_service import session_service
from app.models.chat import ChatRequest, ChatResponse
from app.core.config import settings

router = APIRouter()


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"message": "VisaBot API is working!", "status": "success"}

@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """Chat with the visa evaluation bot"""
    try:
        # Process the message through the bot
        response = await chat_service.process_chat_message(request)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status and progress"""
    try:
        status = await chat_service.get_session_status(session_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{session_id}")
async def reset_session(session_id: str):
    """Reset a session to start over"""
    try:
        result = await chat_service.reset_session(session_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evaluation/{session_id}")
async def get_evaluation_summary(session_id: str):
    """Get evaluation summary for completed sessions"""
    try:
        summary = await chat_service.get_evaluation_summary(session_id)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = await session_service.get_chat_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions")
async def list_active_sessions():
    """List all active sessions"""
    try:
        sessions = await chat_service.list_active_sessions()
        if "error" in sessions:
            raise HTTPException(status_code=500, detail=sessions["error"])
        return sessions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End a chat session"""
    try:
        await session_service.end_session(session_id)
        return {"message": "Session ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found") 
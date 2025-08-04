"""
Chat endpoints for bot interactions
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.chat_service import ChatService
from app.services.session_service import SessionService
from app.models.chat import ChatRequest, ChatResponse
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    chat_service: ChatService = Depends(ChatService),
    session_service: SessionService = Depends(SessionService)
):
    """Chat with the visa bot"""
    try:
        # Get or create session
        session = await session_service.get_or_create_session(request.session_id)
        
        # Process the message through the bot
        response = await chat_service.process_message(
            session_id=session.session_id,
            message=request.message,
            context=request.context
        )
        
        return ChatResponse(
            session_id=session.session_id,
            message=response.message,
            state=response.state,
            metadata=response.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    session_service: SessionService = Depends(SessionService)
):
    """Get chat history for a session"""
    try:
        history = await session_service.get_chat_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/session/{session_id}")
async def end_session(
    session_id: str,
    session_service: SessionService = Depends(SessionService)
):
    """End a chat session"""
    try:
        await session_service.end_session(session_id)
        return {"message": "Session ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found") 
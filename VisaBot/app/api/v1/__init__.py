"""
API v1 package
"""
from fastapi import APIRouter

from app.api.v1.endpoints import chat, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(websocket.router, prefix="/websocket", tags=["websocket"]) 
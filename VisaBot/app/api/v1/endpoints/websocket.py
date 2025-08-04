"""
WebSocket endpoints for real-time chat
"""
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger

from app.services.chat_service import ChatService
from app.services.session_service import SessionService
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    chat_service: ChatService = Depends(ChatService),
    session_service: SessionService = Depends(SessionService)
):
    """WebSocket endpoint for real-time chat"""
    await websocket_manager.connect(websocket, session_id)
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "session_id": session_id,
            "message": "Connected to VisaBot. How can I help you today?"
        }))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            if message_data.get("type") == "message":
                user_message = message_data.get("message", "")
                
                # Process through chat service
                response = await chat_service.process_message(
                    session_id=session_id,
                    message=user_message,
                    context=message_data.get("context")
                )
                
                # Send response back to client
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "session_id": session_id,
                    "message": response.message,
                    "state": response.state,
                    "metadata": response.metadata,
                    "timestamp": response.timestamp.isoformat()
                }))
                
                # Broadcast to other connected clients if needed
                await websocket_manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "message_sent",
                        "session_id": session_id,
                        "user_message": user_message,
                        "bot_response": response.message
                    },
                    exclude_websocket=websocket
                )
            
            elif message_data.get("type") == "typing":
                # Handle typing indicators
                await websocket_manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "typing",
                        "session_id": session_id,
                        "is_typing": message_data.get("is_typing", False)
                    },
                    exclude_websocket=websocket
                )
            
            elif message_data.get("type") == "ping":
                # Handle ping/pong for connection health
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "session_id": session_id
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        websocket_manager.disconnect(websocket, session_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "session_id": session_id,
            "message": "An error occurred. Please try again."
        }))
        websocket_manager.disconnect(websocket, session_id)


@router.get("/ws/status/{session_id}")
async def get_websocket_status(session_id: str):
    """Get WebSocket connection status for a session"""
    connections = websocket_manager.get_session_connections(session_id)
    return {
        "session_id": session_id,
        "connected_clients": len(connections),
        "is_connected": len(connections) > 0
    } 
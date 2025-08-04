"""
WebSocket manager for handling multiple connections
"""
import json
from typing import Dict, List, Set, Any
from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Map session_id to set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map WebSocket to session_id for cleanup
        self.websocket_sessions: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket to a session"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        self.websocket_sessions[websocket] = session_id
        
        logger.info(f"WebSocket connected to session: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket from a session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            # Remove empty session
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        if websocket in self.websocket_sessions:
            del self.websocket_sessions[websocket]
        
        logger.info(f"WebSocket disconnected from session: {session_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to a specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            # Remove broken connection
            session_id = self.websocket_sessions.get(websocket)
            if session_id:
                self.disconnect(websocket, session_id)
    
    async def broadcast_to_session(
        self,
        session_id: str,
        message: Dict[str, Any],
        exclude_websocket: WebSocket = None
    ):
        """Broadcast message to all WebSockets in a session"""
        if session_id not in self.active_connections:
            return
        
        disconnected_websockets = set()
        
        for websocket in self.active_connections[session_id]:
            if websocket != exclude_websocket:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {e}")
                    disconnected_websockets.add(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected_websockets:
            self.disconnect(websocket, session_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSockets"""
        for session_id in list(self.active_connections.keys()):
            await self.broadcast_to_session(session_id, message)
    
    def get_session_connections(self, session_id: str) -> List[WebSocket]:
        """Get all WebSocket connections for a session"""
        return list(self.active_connections.get(session_id, set()))
    
    def get_connection_count(self, session_id: str) -> int:
        """Get number of connections for a session"""
        return len(self.active_connections.get(session_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())
    
    async def send_typing_indicator(self, session_id: str, is_typing: bool = True):
        """Send typing indicator to session"""
        await self.broadcast_to_session(session_id, {
            "type": "typing",
            "session_id": session_id,
            "is_typing": is_typing
        })
    
    async def send_system_message(self, session_id: str, message: str, message_type: str = "info"):
        """Send system message to session"""
        await self.broadcast_to_session(session_id, {
            "type": "system",
            "session_id": session_id,
            "message": message,
            "message_type": message_type
        })
    
    async def send_error_message(self, session_id: str, error_message: str):
        """Send error message to session"""
        await self.broadcast_to_session(session_id, {
            "type": "error",
            "session_id": session_id,
            "message": error_message
        })
    
    def cleanup_inactive_connections(self):
        """Clean up inactive connections (can be called periodically)"""
        # This method can be extended to implement connection health checks
        # For now, we rely on exception handling during message sending
        pass 
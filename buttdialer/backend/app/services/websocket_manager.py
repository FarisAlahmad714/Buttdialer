from typing import List, Dict
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str, user_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(client_id)
        
        logger.info(f"WebSocket connected: {client_id} for user {user_id}")
        
    def disconnect(self, client_id: str, user_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(client_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                
        logger.info(f"WebSocket disconnected: {client_id}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def send_user_message(self, message: dict, user_id: int):
        if user_id in self.user_connections:
            disconnected_clients = []
            
            for client_id in self.user_connections[user_id]:
                if client_id in self.active_connections:
                    websocket = self.active_connections[client_id]
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Error sending message to {client_id}: {e}")
                        disconnected_clients.append(client_id)
                        
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                self.disconnect(client_id, user_id)
                
    async def broadcast(self, message: dict, exclude_client: str = None):
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if client_id != exclude_client:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)
                    
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            # Find user_id for this client
            for user_id, clients in self.user_connections.items():
                if client_id in clients:
                    self.disconnect(client_id, user_id)
                    break
                    
    async def send_call_update(self, call_data: dict, agent_id: int):
        """Send call update to specific agent"""
        message = {
            "type": "call_update",
            "data": call_data
        }
        await self.send_user_message(message, agent_id)
        
    async def send_call_notification(self, notification: dict, team_id: int = None):
        """Send call notification to team or all admins"""
        message = {
            "type": "call_notification",
            "data": notification
        }
        
        if team_id:
            # Send to team members
            # This would require additional logic to get team members
            pass
        else:
            # Send to all connected users
            await self.broadcast(message)

# Global connection manager
manager = ConnectionManager()
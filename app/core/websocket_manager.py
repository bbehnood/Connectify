from fastapi import WebSocket
from typing import Dict, Optional, Any
import json


class ConnectionManager:
    def __init__(self) -> None:
        # Stores active WebSocket connections. Key: connection_id, Value: WebSocket object
        self.active_connections: Dict[str, WebSocket] = {}
        # Stores user information. Key: connection_id, Value: username
        self.user_connections: Dict[str, str] = {}

    async def connect(self, websoket: WebSocket, connection_id: str):
        await websoket.accept()
        self.active_connections[connection_id] = websoket
        print(f"Client connected: {connection_id}")

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            if connection_id in self.user_connections:
                del self.user_connections[connection_id]
            print(f"Client disconnected: {connection_id}")

    async def send_personal_message(self, message: str, websoket: WebSocket):
        await websoket.send_text(message)

    async def broadcast(
        self, message: Dict[str, Any], sender_connection_id: Optional[str] = None
    ):
        """
        Broadcasts a message to all connected clients.
        If sender_connection_id is provided, the message is not sent back to the sender.
        """
        message_json = json.dumps(message)

        for connection_id, connection in self.active_connections.items():
            if connection_id != sender_connection_id:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f"Error sending message to: {connection_id}: {e}")
                    # Disconnect the client if send fails
                    self.disconnect(connection_id)

    async def set_username(self, connection_id: str, username: str):
        if connection_id in self.active_connections:
            self.user_connections[connection_id] = username
            # Inform the user of their new username
            await self.active_connections[connection_id].send_json(
                {
                    "type": "system",
                    "sender": "Server",
                    "message": f"Your username is now: {username}",
                }
            )
            # Announce the new user to everyone
            await self.broadcast(
                {
                    "type": "system",
                    "sender": "Server",
                    "message": f"User '{username}' has joined the chat.",
                },
                sender_connection_id=connection_id,
            )
            print(f"User {connection_id} set username to {username}")
        else:
            print(
                f"Attempted to set username for non-existent connection: {connection_id}"
            )

        def get_username(self, connection_id: str) -> Optional[str]:
            return self.user_connections.get(connection_id)

        def get_connection_count(self) -> int:
            return len(self.active_connections)


# Instantiate the manager globally
manager = ConnectionManager()

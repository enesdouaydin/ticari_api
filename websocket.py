from fastapi import  WebSocket
from typing import List


from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_queue: List[dict] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    def add_message_to_queue(self, message: dict):
        self.message_queue.append(message)

    def get_messages_from_queue(self):
        messages = self.message_queue.copy()
        self.message_queue.clear()
        return messages

manager = ConnectionManager()
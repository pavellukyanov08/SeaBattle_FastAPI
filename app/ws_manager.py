from typing import Dict, List
from fastapi import WebSocket


class ConnectManger:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}


    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)


    def disconnect(self, game_id: str, websocket: WebSocket):
        if game_id in self.active_connections and websocket in self.active_connections[game_id]:
            self.active_connections[game_id].remove(websocket)


    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)


    async def broadcast(self, game_id: str, message: dict):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_json(message)


manager = ConnectManger()

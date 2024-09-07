from typing import Dict

from fastapi import WebSocket, WebSocketException, status

class ConnectionManager:


    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = dict()


    async def connect(self, websocket: WebSocket, current_user: str):
        # Evento de conexão
        await websocket.accept()
        self.active_connections[current_user] = websocket


    async def personal_message(self, data: str, user: str):
        # Enviar mensagem para usuário requerido `user`
        if user not in self.active_connections.keys():
            raise WebSocketException(
                code=status.WS_1014_BAD_GATEWAY, reason='O destinatário não está conectado no momento!'
            )

        await self.active_connections[user].send_text(data=data)


    
    async def broadcast(self, websocket: WebSocket, data: str):
        # Envia mensagem via websocket
        for user, connection in self.active_connections.items():
            await connection.send_text(data=data)



    def close_connection(self, user: str, websocket: WebSocket):
        self.active_connections.pop(user)


manager = ConnectionManager()

from typing import Dict, List

from fastapi import WebSocket, WebSocketException, status


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[Dict[str, WebSocket]]] = dict()

    async def connect(
        self, websocket: WebSocket, chat_id: str, current_user: str
    ) -> None:
        # Evento de conexão
        await websocket.accept()

        # Adiciona usuário no chat
        if chat_id not in self.active_connections:
            self.active_connections = {chat_id: list()}

        self.active_connections[chat_id].append({current_user: websocket})

    async def personal_message(self, chat_id: str, data: str, user: str):
        # Enviar mensagem para usuário requerido `user`
        recipient_user = {
            user: connected_user.get(user)
            for connected_user in self.active_connections.get(chat_id)
            if user in connected_user.keys()
        }
        if not recipient_user:
            raise WebSocketException(
                code=status.WS_1014_BAD_GATEWAY,
                reason='O destinatário não está conectado no momento!',
            )

        await recipient_user[user].send_text(data=data)

    async def broadcast(self, websocket: WebSocket, data: str):
        # Envia mensagem via websocket
        for _, connection in self.active_connections.items():
            await connection.send_text(data=data)

    def close_connection(self, chat_id: str, user: str, websocket: WebSocket):
        self.active_connections.pop(user)


manager = ConnectionManager()

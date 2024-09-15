import asyncio
import json

import redis.asyncio as aioredis
from fastapi import WebSocket, WebSocketException, status

from chave_propria.settings.Settings import Settings


class ConnectionManager:
    def __init__(self) -> None:
        self.redis_client = aioredis.Redis(
            host=Settings().REDIS_HOST,
            port=Settings().REDIS_PORT,
            db=Settings().REDIS_DB,
        )

    async def connect(
        self,
        websocket: WebSocket,
        chat_id: str,
        current_user: str,
    ) -> None:
        # Aceita conexão via WebSocket
        await websocket.accept()

        # Adiciona informação do usuário conectado
        await self.redis_client.hset(
            name=chat_id, mapping={current_user: 'connected'}
        )

        pub_sub = self.redis_client.pubsub()

        await pub_sub.subscribe(chat_id)

        asyncio.create_task(
            coro=self.subscriber(
                subscribe=pub_sub,
                websocket=websocket,
                current_user=current_user,
            )
        )

    async def publisher(self, chat_id: str, data: str, user_to_send: str):
        # Busca usuário requerido
        recipient_user = await self.redis_client.hget(
            name=chat_id, key=user_to_send
        )

        # Se o usuário requerido não estiver conectado
        print(recipient_user)
        if not recipient_user:
            print('usuário não conectado')
            raise WebSocketException(
                code=status.WS_1014_BAD_GATEWAY,
                reason='O destinatário não está conectado no momento!',
            )

        try:
            # Publica a mensagem
            await self.redis_client.publish(
                channel=chat_id,
                message=json.dumps(
                    {
                        'recipient': user_to_send,
                        'text': data,
                    }
                ),
            )
        except Exception as e:
            print(f'\n\nERRO PARA PUBLICAR NO CANAL: {e}\n')

    async def subscriber(
        self,
        subscribe,
        websocket: WebSocket,
        current_user: str,
        chat_id: str = None,
    ) -> None:
        while True:
            message = await subscribe.get_message(
                ignore_subscribe_messages=True,
            )
            if message:
                data = json.loads(message['data'])
                if data['recipient'] == current_user:
                    await websocket.send_text(data=data['text'])

    async def close_connection(
        self, chat_id: str, current_user: str, websocket: WebSocket
    ):
        await self.redis_client.hdel(chat_id, current_user)


manager = ConnectionManager()

from typing import Annotated, List, Tuple

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select, union_all
from sqlalchemy.orm import Session

from chave_propria.database.database_connection import database_session
from chave_propria.database.models import Contatos, User
from chave_propria.utils.security.security import get_current_user
from chave_propria.utils.WebSocket_ConnectionManager import manager

message = APIRouter(prefix='/ws', tags=['Message'])

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(database_session)]


def busca_amigos(current_user_id: int, chat_id: str, session: Session):
    # Se o usuário atual é remetente
    sender_user = (
        select(User.username)
        .join(Contatos, Contatos.contato_id == User.id)
        .where(
            Contatos.chat_id == chat_id,
            Contatos.user_id == current_user_id,
        )
    )

    # Se o usuário atual é destinatário
    recipient_user = (
        select(User.username)
        .join(
            Contatos,
            Contatos.user_id == User.id,
        )
        .where(
            Contatos.chat_id == chat_id, Contatos.contato_id == current_user_id
        )
    )

    command = union_all(sender_user, recipient_user)

    recipient_username = session.execute(command).scalar()

    return recipient_username


@message.websocket('/communicate/')
async def communicate(
    get_current_user: T_CurrentUser,
    session: T_Session,
    chat_id: str,
    websocket: WebSocket,
):
    # Verificar se o `user_email` está na lista de amigos do usuário atual
    recipient_username = busca_amigos(
        current_user_id=get_current_user.id,
        chat_id=chat_id,
        session=session,
    )

    print('Recebi uma conexão websocket')


    # Ativa conexão com websocket
    await manager.connect(
        websocket=websocket,
        current_user=get_current_user.username,
        chat_id=chat_id,
    )

    try:
        while True:
            received_data = await websocket.receive_text()
            print(
                f'DADO RECEBIDO => {received_data} ENVIANDO PARA {recipient_username}'
            )
            await manager.personal_message(
                chat_id=chat_id, data=received_data, user=recipient_username
            )
    except WebSocketDisconnect:
        manager.close_connection(
            websocket=websocket, user=get_current_user.username
        )

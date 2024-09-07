from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select, union_all
from sqlalchemy.orm import Session

from chave_propria.database.database_connection import database_session
from chave_propria.utils.security.security import get_current_user
from chave_propria.database.models import User, Contatos
from chave_propria.utils.WebSocket_ConnectionManager import manager

message = APIRouter(prefix='/ws', tags=['Message'])

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(database_session)]


def busca_amigos(
    current_user_id: int, recipient_user_email: str, session: Session
):
    # Se o usuário atual é remetente
    sender_user = select(User.username).join(
        Contatos, Contatos.contato_id == User.id
    ).where(
        User.email == recipient_user_email,
        Contatos.user_id == current_user_id,
    )

    # Se o usuário atual é destinatário
    recipient_user = select(User.username).join(
        Contatos, Contatos.user_id == User.id,
    ).where(
        User.email == recipient_user_email,
        Contatos.contato_id == current_user_id
    )

    command = union_all(sender_user, recipient_user)

    recipient_username = session.execute(statement=command).scalar()

    return recipient_username


@message.websocket('/communicate/')
async def communicate(
    get_current_user: T_CurrentUser,
    session: T_Session,
    user_email: str,
    websocket: WebSocket,
):  
    # Verificar se o `user_email` está na lista de amigos do usuário atual
    recipient_username = busca_amigos(
        current_user_id=get_current_user.id,
        recipient_user_email=user_email,
        session=session,
    )


    # Ativa conexão com websocket
    await manager.connect(websocket=websocket, current_user=get_current_user.username)

    try:
        while True:
            received_data = await websocket.receive_text()
            print(f"DADO RECEBIDO => {received_data} ENVIANDO PARA {recipient_username}")
            await manager.personal_message(data=received_data, user=recipient_username)
    except WebSocketDisconnect:
        manager.close_connection(websocket=websocket, user=get_current_user.username)

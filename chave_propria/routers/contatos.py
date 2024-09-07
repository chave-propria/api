from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, union_all
from sqlalchemy.orm import Session

from chave_propria.utils.security.security import get_current_user
from chave_propria.utils.schemas import UserInvite, Message, Invites
from chave_propria.database.models import User, Contatos
from chave_propria.database.database_connection import database_session

contatos = APIRouter(prefix='/contatos', tags=['Contatos'])


T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(database_session)]

@contatos.get('/')
def todos_contatos(current_user: T_CurrentUser, session: T_Session):
    return {'msg': 'teste'}


@contatos.post('/', response_model=Message)
def adiciona_contato(
    user: UserInvite,
    current_user: T_CurrentUser,
    session: T_Session,
):
    # TODO: Adicionar verificar caso um convite já estiver sido enviado
    # Verifica se o user_id está na tabela Users
    user_exists = session.scalar(
        select(User).where(User.email == user.email)
    )
    if not user_exists:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='usuário não encontrado!'
        )
    
    add_contato = Contatos(user_id=current_user.id, contato_id=user_exists.id)

    session.add(add_contato)
    session.commit()

    return {'status': 'ok', 'msg': 'Convite enviado com sucesso'}


@contatos.post('/aceita/{convite_id}')
def aceita_convite(
    convite_id: int, current_user: T_CurrentUser,session: T_Session
):
    guest_user_id = session.scalar(
        select(Contatos.contato_id).where(Contatos.id == convite_id)
    )

    if not guest_user_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Convite não encontrado'
        )
    if current_user.id != guest_user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Não permitido'
        )

    try:
        # TODO: Validar
        session.execute(
            update(Contatos).where(
                Contatos.id == convite_id
            ).values(status='accepted')
        )

        session.commit()
    except Exception as e:
        session.rollback()
        print(f'ERRO => {e}')
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='Erro para aceitar o convite')


@contatos.get('/convites', response_model=list[Invites])
def verifica_convites_pendentes(
    current_user: T_CurrentUser,
    session: T_Session,
    limite: int = 10,
    status: str = 'pending'
):

    # Caso o usuário logado tenha enviado convites (Remetente)
    sender_user = select(Contatos.id, User.email, Contatos.status).join(
        User, Contatos.user_id == User.id
    ).where(
        Contatos.contato_id == current_user.id,
        Contatos.status == status,
    )

    # Caso usuário logado tenha recebido convites (Destinatário)
    recipient_user = select(Contatos.id, User.email, Contatos.status).join(
        User, Contatos.contato_id == User.id
    ).where(
        Contatos.user_id == current_user.id,
        Contatos.status == status,
    )

    command = union_all(sender_user, recipient_user).limit(limite)

    convites = session.execute(command).all()

    # Converter a lista de tuplas em uma lista de dicionários
    contatos = [dict(zip(['id', 'email', 'status'], linha)) for linha in convites]

    return contatos
    
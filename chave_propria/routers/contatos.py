from hashlib import sha384
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, union_all, update
from sqlalchemy.orm import Session

from chave_propria.database.database_connection import database_session
from chave_propria.database.models import Contatos, User
from chave_propria.utils.schemas import Invites, Message, UserInvite
from chave_propria.utils.security.security import get_current_user

contatos = APIRouter(prefix='/contatos', tags=['Contatos'])

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(database_session)]


@contatos.post('/', response_model=Message)
def adiciona_contato(
    user: UserInvite,
    current_user: T_CurrentUser,
    session: T_Session,
):
    # Verifica se o user_id está na tabela Users
    user_exists = session.scalar(select(User).where(User.email == user.email))

    if not user_exists:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='usuário não encontrado!'
        )

    # Caso o usuário logado tenha recebido convites (Destinatário)
    recipient_user = select(Contatos.status).where(
        Contatos.contato_id == current_user.id,
        Contatos.user_id == user_exists.id,
    )

    # Caso usuário logado tenha recebido convites (Destinatário)
    sender_user = select(Contatos.status).where(
        Contatos.user_id == current_user.id,
        Contatos.contato_id == user_exists.id,
    )

    command = union_all(sender_user, recipient_user)

    exists_invite = session.execute(command).all()

    print(f'\n\n{exists_invite}\n\n')

    if exists_invite:
        if 'accepted' in exists_invite:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Os usuários já são amigos!',
            )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Existe um convite deste usuário!',
        )

    # Verificar adição de hash entre (current_user.username && email do contato)
    hash_users = lambda users: sha384('_'.join(users).encode()).hexdigest()[
        :10
    ]

    chat_id = hash_users(sorted({current_user.email, user_exists.email}))

    add_contato = Contatos(
        user_id=current_user.id,
        contato_id=user_exists.id,
        chat_id=chat_id,
    )

    session.add(add_contato)
    session.commit()

    return {'status': 'ok', 'msg': 'Convite enviado com sucesso'}


@contatos.post('/aceita/{convite_id}', response_model=Message)
def aceita_convite(
    convite_id: int, current_user: T_CurrentUser, session: T_Session
):
    guest_user_id = session.scalar(
        select(Contatos.contato_id).where(Contatos.id == convite_id)
    )

    if not guest_user_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Convite não encontrado'
        )
    # Se o usuário atual não for o usuário que recebeu o convite
    if current_user.id != guest_user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Não permitido'
        )

    try:
        # TODO: Validar
        session.execute(
            update(Contatos)
            .where(Contatos.id == convite_id)
            .values(status='accepted')
        )

        session.commit()
    except Exception as e:
        session.rollback()
        print(f'ERRO => {e}')
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Erro para aceitar o convite',
        )

    return {'status': 'ok', 'msg': 'Convite aceito com sucesso!'}


@contatos.get('/convites', response_model=list[Invites])
def verifica_convites(
    current_user: T_CurrentUser,
    session: T_Session,
    limite: int = 10,
    status: str = 'pending',
):

    # Caso o usuário logado tenha enviado convites (Remetente)
    sender_user = (
        select(Contatos.id, User.email, Contatos.chat_id)
        .join(User, Contatos.user_id == User.id)
        .where(
            Contatos.contato_id == current_user.id,
            Contatos.status == status,
        )
    )

    # Caso usuário logado tenha recebido convites (Destinatário)
    recipient_user = (
        select(Contatos.id, User.email, Contatos.chat_id)
        .join(User, Contatos.contato_id == User.id)
        .where(
            Contatos.user_id == current_user.id,
            Contatos.status == status,
        )
    )

    command = union_all(sender_user, recipient_user).limit(limite)

    # Retorna uma lista de tuplas com os valores na ordem [(id: int, email: str, status: str)]
    convites = session.execute(command).all()

    # Converter a lista de tuplas em uma lista de dicionários
    contatos = [
        dict(zip(['id', 'email', 'chat_id'], linha)) for linha in convites
    ]

    return contatos

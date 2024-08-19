from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from chave_propria.database.database_connection import database_session
from chave_propria.database.models import User
from chave_propria.utils.schemas import Message, UserPublic, UserSchema
from chave_propria.utils.security.security import (
    get_current_user,
    password_hash,
)

users = APIRouter(prefix='/usuario', tags=['Usuários'])

T_Session = Annotated[Session, Depends(database_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@users.post(
    '/',
    status_code=HTTPStatus.CREATED,
    description='Realiza a criação de usuários',
    response_model=UserPublic,
)
def cria_usuario(user: UserSchema, session: T_Session):
    # Verifica se já existe usuário com o mesmo username ou email
    db_user = session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='username já cadastrado',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='email já cadastrado',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@users.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    description='Realiza a busca de usuários',
    response_model=UserPublic,
)
def busca_usuario(
    user_id: int,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Não permitido'
        )

    return current_user


@users.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    description='Deleta usuário',
    response_model=Message,
)
def deleta_usuario(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Não permitido'
        )

    session.delete(current_user)
    session.commit()

    return {'status': 'ok', 'msg': 'usuário deletado com sucesso'}

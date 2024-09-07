from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from chave_propria.database.database_connection import database_session
from chave_propria.database.models import User
from chave_propria.utils.schemas import Token
from chave_propria.utils.security.security import (
    create_access_token,
    get_current_user,
    verify_hashed_password,
)

auth = APIRouter(tags=['Auth'], prefix='/auth')

T_Session = Annotated[Session, Depends(database_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_User = Annotated[User, Depends(get_current_user)]


@auth.post('/token', response_model=Token)
def login_for_access_token(
    form: T_OAuth2Form,
    session: T_Session,
    response: Response,
):
    user = session.scalar(select(User).where(User.username == form.username))

    if not user or not verify_hashed_password(
        plain_password=form.password,
        hashed_password=user.password,
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='username ou senha incorretos',
        )

    access_token = create_access_token(jwt_claims={'sub': user.username})

    # TODO: VERIFICAR PARA ADICIONAR COOKIE COM TOKEN JWT   
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
    )

    return {'access_token': access_token, 'token_type': 'Bearer'}


@auth.post('/refresh_token', response_model=Token)
def refresh_token(user: T_User):
    # O refresh token é feito criando-se um novo token com as informações do usuário logado atualmente
    refreshed_token = create_access_token(jwt_claims={'sub': user.username})

    return {'access_token': refreshed_token, 'token_type': 'Bearer'}

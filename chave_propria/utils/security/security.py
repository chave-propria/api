from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Dict
from zoneinfo import ZoneInfo

from fastapi import Depends, Cookie, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import ExpiredSignatureError, DecodeError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from chave_propria.database.database_connection import database_session
from chave_propria.database.models import User
from chave_propria.settings.Settings import Settings

# recebe o retorno da autenticação em `/auth/token`
oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/token')
context = PasswordHash.recommended()


def password_hash(password: str) -> str:
    """
    Realiza o hash da senha

    Arguments:
        password (str): A senha que será feito o hash

    Returns:
        str: O hash da senha
    """
    return context.hash(password)


def verify_hashed_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano é correspondente ao hash

    Arguments:
        plain_password (str): A senha em texto plano
        hashed_password (str): O hash da senha a ser verificado

    Returns:
        bool: True, caso a senha em texto plano seja correspondente ao hash, caso contrário retorna False
    """
    return context.verify(password=plain_password, hash=hashed_password)


def create_access_token(jwt_claims: Dict[str, str]) -> str:
    """
    Realiza o encode do JWT

    Arguments:
        jwt_claims (Dict[str, str]): As claims do JWT que serão adicionadas no encode

    Returns:
        str: O Token JWT após o encode
    """
    encode_claims = jwt_claims.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )

    encode_claims.update({'exp': expire})

    encoded_jwt = encode(
        encode_claims, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )

    return encoded_jwt


def get_current_user(
    session: Session = Depends(database_session),
    access_token=Cookie(),
    # token: str = Depends(oauth2_schema),
) -> User:
    """
    Identifica o usuário após a autenticação

    Arguments:
        session (Session): A sessão com o Banco de Dados
        token (str): O token recebido após sucesso na autenticação

    Returns:
        User: O respectivo usuário no banco de dados
    """
    creadential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Não foi possível validar as credenciais',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    # token = request.cookies.get('access_token')

    if not access_token:
        raise creadential_exception

    try:
        payload: dict = decode(
            access_token, Settings().SECRET_KEY, algorithms=[Settings().ALGORITHM]
        )

        # pega o username a partir do payload (decode do token recebido)
        username = payload.get('sub')
        if not username:
            raise creadential_exception
    except ExpiredSignatureError:
        raise creadential_exception
    except DecodeError:
        raise creadential_exception

    db_user = session.scalar(select(User).where(User.username == username))

    if not db_user:
        raise creadential_exception

    return db_user

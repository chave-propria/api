from factory import Factory, LazyAttribute, Sequence
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from chave_propria.api.remetente import remetente
from chave_propria.database.database_connection import database_session
from chave_propria.database.models import User, table_registry
from chave_propria.utils.security.security import password_hash


class UserFactory(Factory):
    # Define o modelo base da classe que quer contruir
    class Meta:
        model = User

    # Gera uma sequência para username. Ex.: teste_0, teste_1, ...
    username = Sequence(lambda n: f'teste_{n}')

    # `obj` é o `self` da classe Meta. Ex.: teste_0@teste.com, teste_1@teste.com, ...
    email = LazyAttribute(lambda obj: f'{obj.username}@teste.com')
    password = LazyAttribute(lambda obj: f'{obj.username}_minha_senha')


@fixture
def client(db_session):
    def test_session_override():
        return db_session

    # No momento de testes, a dependencia de sessão de banco é substituída pela sessão de teste
    with TestClient(remetente) as test_client:
        remetente.dependency_overrides[
            database_session
        ] = test_session_override

        yield test_client

    remetente.dependency_overrides.clear()


@fixture
def user(db_session: Session):
    clean_password = 'senha_teste'

    fake_user = UserFactory(password=password_hash(clean_password))

    # fake_user = User(
    #     username='Teste',
    #     email='teste@teste.com',
    #     password=password_hash(clean_password),
    # )

    db_session.add(fake_user)
    db_session.commit()
    db_session.refresh(fake_user)

    fake_user.clean_password = clean_password  # Monkey Patch

    return fake_user


@fixture
def db_session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )  # Especificações para conexão com o banco

    # Cria o banco baseado na `engine`
    table_registry.metadata.create_all(engine)

    # Gerenciamento de contexto
    with Session(engine) as db_session:
        yield db_session

    # Limpa o banco após as execuções do `yield`
    table_registry.metadata.drop_all(engine)


@fixture
def get_token(client, user) -> str:
    # Envia a requisição para login via token através do usuário em `user`
    token = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    # Retorna o token do usuário
    return token.json()['access_token']

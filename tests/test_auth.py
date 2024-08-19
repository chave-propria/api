from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from chave_propria.database.models import User


def test_token(client: TestClient, user: User):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token


def test_token_deve_expirar_apos_determinado_tempo(
    client: TestClient, user: User
):
    with freeze_time('2024-09-17 12:00:00'):
        # Gera o token às 12h00
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )
        token = response.json()['access_token']

        assert response.status_code == HTTPStatus.OK

    with freeze_time('2024-09-17 12:31:00'):
        # Utiliza o token às 12h31
        response = client.delete(
            f'/usuario/{user.id}', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_deve_retornar_erro_quanto_usuario_nao_existir(
    client: TestClient, user: User
):
    response = client.post(
        '/auth/token',
        data={'username': 'fake_user', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_token_deve_retornar_erro_quanto_senha_nao_existir(
    client: TestClient, user: User
):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'fake_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_refresh_token(client: TestClient, get_token: str):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {get_token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()


def test_refresh_token_deve_retornar_erro_se_token_ja_tiver_expirado(
    client: TestClient, user: User
):
    with freeze_time('2024-09-17 12:00:00'):
        # realiza a criação to token às 12h00
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in response.json()

    with freeze_time('2024-09-17 12:31:00'):
        # realiza o refresh do token 31 minutos após a criação
        token = response.json()['access_token']

        refresh_token = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert refresh_token.status_code == HTTPStatus.UNAUTHORIZED

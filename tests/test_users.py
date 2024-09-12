from http import HTTPStatus

from chave_propria.utils.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/usuario',
        json={
            'username': 'pedro_teste',
            'email': 'pedro@teste.com',
            'password': 'senhateste123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED


def test_create_user_deve_retornar_erro_quando_username_ja_existir(
    client, user
):
    response = client.post(
        '/usuario',
        json={
            'username': user.username,
            'email': 'teste2@email.com',
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_user_deve_retornar_erro_quando_email_ja_existir(client, user):
    response = client.post(
        '/usuario',
        json={
            'username': 'teste2',
            'email': user.email,
            'password': 'senha',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user(client, user, get_token):
    # converte o `user` (tipo User do SQLALCHEMY) para o tipo `UserPublic` do pydantic
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        f'/usuario/{user.id}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.json() == user_schema


# def test_get_user_deve_retornar_erro_quando_id_nao_encontrado(client):
#     response = client.get('/usuario/2')

#     assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_user(client, user, get_token):
    response = client.delete(
        f'/usuario/{user.id}',
        headers={'Authorization': f'Bearer {get_token}'},
    )

    assert response.json() == {
        'status': 'ok',
        'msg': 'usuário deletado com sucesso',
    }


# def test_delete_user_deve_retornar_erro_quando_id_nao_encontrado(client):
#     response = client.delete('/usuario/2')

#     assert response.status_code == HTTPStatus.UNAUTHORIZED

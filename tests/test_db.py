from sqlalchemy import select

from chave_propria.database.models import User


def test_cria_usuario_no_banco(db_session):
    user = User(
        email='pedro@teste.com',
        username='pedro_bueno',
        password='senha',
    )

    db_session.add(user)
    db_session.commit()  # Adiciona os dados na tabela do banco

    # Retorna um objeto da classe User
    user_result = db_session.scalar(
        select(User).where(User.email == 'pedro@teste.com')
    )

    assert user_result.username == 'pedro_bueno'

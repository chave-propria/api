from jwt import decode

from chave_propria.utils.security.security import Settings, create_access_token


def test_jwt():
    claims = {'sub': 'pedro_bueno'}

    jwt = create_access_token(jwt_claims=claims)

    decode_jwt = decode(jwt, Settings().SECRET_KEY, Settings().ALGORITHM)

    assert decode_jwt['sub'] == claims['sub']
    assert decode_jwt['sub']

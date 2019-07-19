# from pytest import fixture  # type: ignore
# from models.accounts import User  # type: ignore


# @fixture
# def user() -> User:
#     return User(email="richard@leximpact.pop")


# def test_create_user(dbsession, user):
#     dbsession.add(user)
#     dbsession.flush()
#     query = dbsession.query(User).get(user.email)
#     assert query.email == user.email


# def test_update_user(dbsession, user):
#     dbsession.add(user)
#     dbsession.flush()
#     user.token = "asdf1234"
#     query = dbsession.query(User).get(user.email)
#     assert query.token == user.token


# from server.services.token_services import (  # type: ignore
#     create_nonce,
#     create_token,
#     decode_token,
#     create_payload,
# )


# def test_decode_token():
#     user = "richard@leximpact.pop"
#     uuid = create_nonce().decode("ascii")
#     iss = "Moi"
#     aud = "Vous"
#     payload = create_payload(user, uuid, iss, aud)
#     secret = "asdf1234"
#     algo = "HS256"
#     token = create_token(payload, secret, algo)
#     assert decode_token(token, secret, iss, aud, algo) == (user, uuid)

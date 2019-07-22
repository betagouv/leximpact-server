from pytest import fixture  # type: ignore
from models import User, find_user, create_user, update_user_token  # type: ignore


@fixture
def user() -> User:
    return User(email="richard@leximpact.pop")


def test_find_user(session, user):
    assert not find_user(session, user.email)


def test_create_user(session, user):
    assert create_user(session, user)
    assert find_user(session, user.email).email == user.email


def test_update_user_token(session, user):
    token = "asdf1234"
    create_user(session, user)
    update_user_token(session, user.email, "asdf1234")
    assert find_user(session, user.email).token == token

from pytest import fixture  # type: ignore
from models import User, find_user, create_user  # type: ignore


@fixture
def user() -> User:
    return User(email="richard@leximpact.pop")


def test_find_user(session, user):
    assert not find_user(session, user.email)


def test_create_user(session, user):
    create_user(session, user)
    assert find_user(session, user.email).email == user.email


def test_update_user(session, user):
    create_user(session, user)
    user.token = "asdf1234"
    assert find_user(session, user.email).token == user.token

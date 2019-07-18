from pytest import fixture  # type: ignore
from models.accounts import User  # type: ignore


@fixture
def user() -> User:
    return User(email="richard@leximpact.pop")


def test_create_user(dbsession, user):
    dbsession.add(user)
    dbsession.flush()
    query = dbsession.query(User).get(user.email)
    assert query.email == user.email


def test_update_user(dbsession, user):
    dbsession.add(user)
    dbsession.flush()
    user.token = "asdf1234"
    query = dbsession.query(User).get(user.email)
    assert query.token == user.token

from pytest import fixture  # type: ignore
from models import User, create_user, find_user  # type: ignore
from server.services import login_user  # type: ignore


@fixture
def email():
    return "richard@leximpact.pop"


@fixture
def user(session, email):
    create_user(session, User(email=email))
    return find_user(session, email)


def test_login_user_when_not_in_list(session):
    assert not login_user(session, "malevolent@villain.hacker")


def test_login_user_when_empty(session):
    assert not login_user(session, "")

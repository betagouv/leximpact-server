import pytest

from server.services.password import (  # type: ignore
    create_salt,
    create_password,
    verify_password,
)


@pytest.fixture
def passphrase():
    return "Ô combien !"


@pytest.fixture
def salt():
    return create_salt()


@pytest.fixture
def password(passphrase, salt):
    return create_password(passphrase, salt)


def test_create_salt():
    assert len(create_salt()) == 64


def test_verify_password(passphrase, salt):
    password = create_password(passphrase, salt)
    assert verify_password(password, passphrase, salt)

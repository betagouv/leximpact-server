import pytest

from server.services.password import (  # type: ignore
    create_password,
    verify_password,
    create_salt,
    hash_passphrase,
)


@pytest.fixture
def passphrase():
    return "Coucou Richard !"


@pytest.fixture
def salt():
    return create_salt()


@pytest.fixture
def hashed(passphrase, salt):
    return hash_passphrase(passphrase, salt)


def test_create_password(passphrase, salt, hashed):
    password = create_password(passphrase)
    assert isinstance(password, str)
    assert len(password) == len(salt + hashed)


def test_verify_password(passphrase):
    password = create_password(passphrase)
    assert verify_password(password, passphrase)


def test_create_salt():
    salt = create_salt()
    assert isinstance(salt, bytes)


def test_hash_passphrase(passphrase, salt):
    hashed = hash_passphrase(passphrase, salt)
    assert isinstance(hashed, bytes)

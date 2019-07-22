from pytest import fixture  # type: ignore
from models import JWT, encode, decode  # type: ignore


@fixture
def jwt():
    return JWT()


def test_create(jwt):
    assert jwt.algo
    assert jwt.iss
    assert jwt.iss
    assert not jwt.encoded
    assert not jwt.decoded


def test_encode(jwt):
    assert encode(jwt, "richard@leximpact.pop").encoded


def test_decode(jwt):
    email = "richard@leximpact.pop"
    encoded = encode(jwt, email)
    assert decode(encoded).decoded["sub"] == email

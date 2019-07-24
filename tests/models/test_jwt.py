from pytest import fixture  # type: ignore
from models import (
    JWT,
    encode_jwt,
    decode_jwt,
    create_nonce,
    create_token,
    decode_token,
    create_payload,
)  # type: ignore


@fixture
def email():
    return "richard@leximpact.pop"


@fixture
def jwt():
    return JWT()


def test_create(jwt):
    assert jwt.algo
    assert jwt.iss
    assert jwt.iss
    assert not jwt.encoded
    assert not jwt.decoded


def test_encode_jwt(jwt, email):
    assert encode_jwt(jwt, email).encoded


def test_decode_jwt(jwt, email):
    encoded = encode_jwt(jwt, email)
    assert decode_jwt(encoded).decoded["sub"] == email


def test_decode_token(email):
    jti = create_nonce()
    iss = "Moi"
    aud = "Vous"
    payload = create_payload(email, jti, iss, aud)
    secret = "asdf1234"
    algo = "HS256"
    token = create_token(payload, secret, algo)
    assert decode_token(token, secret, iss, aud, algo)["sub"] == email

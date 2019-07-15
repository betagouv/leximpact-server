from datetime import datetime, timedelta
from hashlib import sha3_512
from jwt import encode, decode
from secrets import randbelow, token_bytes
from toolz.functoolz import compose  # type: ignore
from typing import Dict, Tuple, Union

Payload = Dict[str, Union[bytes, datetime, str]]
Auth = Tuple[bytes, bytes]


def create_nonce() -> bytes:
    """Creates a 128 bytes nonce hash"""
    return compose(sha3_512, token_bytes, randbelow)(512).hexdigest().encode("ascii")


def create_token(payload: Payload, secret: str, algo: str) -> bytes:
    """Generates a token"""
    return encode(payload, secret, algorithm=algo)


def decode_token(token: bytes, secret: str, iss: str, aud: str, algo: str) -> Auth:
    """Check the token and returns the user"""
    payload = decode(token, secret, issuer=iss, audience=aud, algorithms=[algo])
    user = payload["sub"]
    uuid = payload["jti"]

    return user, uuid


def create_payload(user: str, nonce: bytes, iss: str, aud: str) -> Payload:
    return {
        "sub": user,
        "jti": nonce,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "iss": iss,
        "aud": aud,
    }

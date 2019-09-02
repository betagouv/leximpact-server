from datetime import datetime, timedelta
from hashlib import sha3_512
from secrets import randbelow, token_bytes
from typing import Dict, TypeVar, Union, Any
from os import getenv

from dotenv import load_dotenv
from jwt import encode, decode
from toolz.functoolz import compose  # type: ignore

load_dotenv(dotenv_path=".env")

T = TypeVar("T", bound="JWT")
Payload = Dict[str, Union[bytes, datetime, str]]


class JWT:
    """Un baton JWT"""

    def __init__(self: T) -> None:
        self.algo: str = "HS256"
        self.iss: str = getenv("JWT_ISSUER")  # type: ignore
        self.aud: str = getenv("JWT_AUDIENCE")  # type: ignore
        self.secret: str = getenv("JWT_SECRET")  # type: ignore
        self.encoded: str = None  # type: ignore
        self.decoded: Dict[str, Any] = None  # type: ignore


def encode_jwt(jwt: T, email: str) -> T:
    nonce = create_nonce()
    payload = create_payload(email, nonce, jwt.iss, jwt.aud)
    jwt.encoded = create_token(payload, jwt.secret, jwt.algo)
    return jwt


def decode_jwt(jwt: T) -> T:
    jwt.decoded = decode_token(jwt.encoded, jwt.secret, jwt.iss, jwt.aud, jwt.algo)
    return jwt


def create_nonce() -> str:
    """Creates a 128 string nonce hash"""
    return compose(sha3_512, token_bytes, randbelow)(512).hexdigest()


def create_token(payload: Payload, secret: str, algo: str) -> str:
    """Generates a token"""
    return encode(payload, secret, algorithm=algo).decode("ascii")


def decode_token(token: str, secret: str, iss: str, aud: str, algo: str) -> Payload:
    """Check the token and returns the user"""
    return decode(
        token.encode("ascii"), secret, issuer=iss, audience=aud, algorithms=[algo]
    )


def create_payload(user: str, nonce: str, iss: str, aud: str) -> Payload:
    return {
        "sub": user,
        "jti": nonce,
        "exp": datetime.utcnow() + timedelta(hours=168),
        "iat": datetime.utcnow(),
        "iss": iss,
        "aud": aud,
    }

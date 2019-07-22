from os import getenv
from dotenv import load_dotenv
from typing import Optional, TypeVar
from lib import create_nonce, create_payload, create_token, decode_token  # type: ignore

load_dotenv(dotenv_path=".env")

T = TypeVar("T", bound="JWT")


class JWT:
    """Un baton JWT"""

    def __init__(self: T) -> None:
        self.algo: str = "HS256"
        self.iss: str = getenv("JWT_ISSUER")  # type: ignore
        self.aud: str = getenv("JWT_AUDIENCE")  # type: ignore
        self.secret: str = getenv("JWT_SECRET")  # type: ignore
        self.encoded: str = None  # type: ignore
        self.decoded: Optional[dict] = None


def encode(jwt: T, email: str) -> T:
    nonce = create_nonce()
    payload = create_payload(email, nonce, jwt.iss, jwt.aud)
    jwt.encoded = create_token(payload, jwt.secret, jwt.algo)
    return jwt


def decode(jwt: T) -> T:
    jwt.decoded = decode_token(jwt.encoded, jwt.secret, jwt.iss, jwt.aud, jwt.algo)
    return jwt

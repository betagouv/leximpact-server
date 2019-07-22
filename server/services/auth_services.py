from os import getenv
from dotenv import load_dotenv
from typing import Optional
from models import User, find_user, update_user_token
from server.tools import create_nonce, create_payload, create_token  # type: ignore

load_dotenv(dotenv_path=".env")


def login_user(session, email: str) -> Optional[User]:
    user = find_user(session, email)

    if not user:
        return None

    nonce = create_nonce().decode("ascii")
    iss = getenv("JWT_ISSUER")
    aud = getenv("JWT_AUDIENCE")
    secret = getenv("JWT_SECRET")
    payload = create_payload(user.email, nonce, iss, aud)  # type: ignore
    token = create_token(payload, secret, "HS256").decode("ascii")  # type: ignore

    return update_user_token(session, user.email, token)

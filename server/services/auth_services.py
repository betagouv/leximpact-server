from typing import Optional
from models.user import User, find_user, update_user_token
from models.jwt import JWT, encode_jwt


def login_user(session, email: str) -> Optional[User]:
    user = find_user(session, email)

    if not user:
        return None

    token = encode_jwt(JWT(), user.email).encoded
    return update_user_token(session, user.email, token)

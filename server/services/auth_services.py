from typing import Optional
from models.user import User, find_user, update_user_token
from models.jwt import JWT, encode_jwt, decode_jwt
from jwt.exceptions import InvalidSignatureError
from datetime import datetime

def check_user(session,tokenencoded:str) -> bool:
    checkjwt=JWT()
    checkjwt.encoded=tokenencoded
    try:
        decode_jwt(checkjwt)
        return find_user(session,checkjwt.decoded["sub"]) and datetime.utcnow().timestamp()<checkjwt.decoded["exp"]
    except InvalidSignatureError:
        return False

def login_user(session, email: str) -> str:#Optional[User]:
    user = find_user(session, email)

    if not user:
        return None
    return encode_jwt(JWT(), user.email)

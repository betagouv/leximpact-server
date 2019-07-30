from typing import Optional
from models.user import find_user, update_user_token
from models.request import create_request
from models.jwt import JWT, encode_jwt, decode_jwt
from jwt.exceptions import InvalidSignatureError
from datetime import datetime

def check_user(session,tokenencoded:str) -> Optional[str]:
    checkjwt=JWT()
    checkjwt.encoded=tokenencoded
    try:
        decode_jwt(checkjwt)
        user=find_user(session,checkjwt.decoded["sub"])
        if user is not None and datetime.utcnow().timestamp()<checkjwt.decoded["exp"]:
            return checkjwt.decoded["sub"]
        else:
            return None
    except InvalidSignatureError:
        return None

def login_user(session, email: str) -> str:#Optional[User]:
    user = find_user(session, email)

    if not user:
        return None
    return encode_jwt(JWT(), user.email)

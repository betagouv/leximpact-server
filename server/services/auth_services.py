from models.user import find_user
from typing import Dict, Optional, Any
from models.request import create_request, count_requests
from models import create_suspension, count_active_suspensions
from models.jwt import JWT, encode_jwt, decode_jwt
from jwt.exceptions import (  # type: ignore
    InvalidSignatureError,
    ExpiredSignatureError,
    DecodeError,
)
from datetime import datetime, timedelta


# Prevention of brute force attacks
limite_requetes = 20
time_period_request = timedelta(minutes=-2)


# Now returns a dict : {"success" : boolean stating if the token is valid,
# "email" : {if success, email of user},
# "error" : {if not success, reason for error}}
# Will also create the suspension if the count of request is too high, OK ?
def check_user(session, tokenencoded: str) -> Dict[str, Any]:
    checkjwt = JWT()
    checkjwt.encoded = tokenencoded
    resultat = {}  # type: Dict[str, Any]
    try:
        decode_jwt(checkjwt)
        user = find_user(session, checkjwt.decoded["sub"])
        if user is None:
            resultat["success"] = False
            resultat["error"] = "User not found in email database"
            return resultat
        if datetime.utcnow().timestamp() > checkjwt.decoded["exp"]:
            resultat["success"] = False
            resultat["error"] = "Token has expired!"
            return resultat
        if count_active_suspensions(session, checkjwt.decoded["sub"]):
            resultat["success"] = False
            resultat["error"] = "User is suspended"
            return resultat
        create_request(session, checkjwt.decoded["sub"])
        if (
            count_requests(session, checkjwt.decoded["sub"], since=time_period_request)
            > limite_requetes
        ):
            create_suspension(session, checkjwt.decoded["sub"])
            resultat["success"] = False
            resultat["error"] = "User is suspended"
            return resultat
        resultat["success"] = True
        resultat["email"] = checkjwt.decoded["sub"]
        return resultat
    except InvalidSignatureError:
        resultat["success"] = False
        resultat["error"] = "Token signature was invalid"
        return resultat
    except ExpiredSignatureError:
        resultat["success"] = False
        resultat["error"] = "Token has expired"
        return resultat
    except DecodeError:
        resultat["success"] = False
        resultat["error"] = "Token invalid : not Decodable"
        return resultat


def login_user(session, email: str) -> Optional[JWT]:  # Optional[User]:
    user = find_user(session, email)

    if not user:
        return None
    return encode_jwt(JWT(), user.email)

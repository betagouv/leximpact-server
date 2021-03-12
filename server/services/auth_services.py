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
from server.services.mail_services import send_mail
import logging
from os import getenv

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
            email = checkjwt.decoded["sub"]
            delay_hours = 1
            create_suspension(session, email, delay_hours)
            alert_suspension(email, delay_hours, session)
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
    email = email.lower()
    domain = email.split("@")[1]
    # We accept login if email is in a collab domain (clb-an.fr or clb-dep.fr)
    # Or if it appears in our DB
    if domain not in ("clb-an.fr", "clb-dep.fr"):
        user = find_user(session, email)
        if not user:
            return None
    return encode_jwt(JWT(), email)


# Send an email when an account is suspended
def alert_suspension(email, delay_hours, session):
    email_team = getenv("MAILJET_SENDER")
    content_team = f"Bonjour<br/>\n<p>L'utilisateur {email} vient d'être suspendu pour {delay_hours} heure(s).<br/> Il a fait plus de {limite_requetes} requêtes en {time_period_request.total_seconds()/-60} minutes.</p><br/>\nVotre dévoué serveur LexImpact"
    logging.info(f"BRUTE FORCE STOPPED : {content_team}")
    send_mail(
        recipient=email_team,
        subject="Nouvelle suspension",
        content=content_team
    )
    send_mail(
        recipient=email,
        subject="Compte LexImpact suspendu",
        content=f"Bonjour<br/>\r\n<p>Votre compte LexImpact vient d'être suspendu pour {delay_hours} heure(s) en raison d'une utilisation trop importante.<br/>Ceci est requis pour la protection des données d’enquête vous permettant le calcul par déciles de population.</p>\nMerci de votre compréhension,<br/>\nL'équipe LexImpact"
    )

from typing import Dict, Tuple
from server.services.database_services import with_session
from server.services.auth_services import login_user
from server.services.mail_services import send_mail

from utils.folder_finder import path_folder_assets  # type: ignore
import logging

with open(path_folder_assets() + "/MailEmailLinkToken.html", "r", encoding="utf-8") as file:
    mail_content_initial = file.read()


@with_session
def login(session, **params: Dict[str, str]) -> Tuple[str, int]:
    email = params["body"]["email"].lower()
    domains = email.split("@")
    if len(domains) != 2:
        msg = "Erreur : L'email n'est pas au bon format (pas le bon nombre de @)"
        logging.warning(f"{msg} - {email}")
        return msg, 200
    jwt = login_user(session, email)
    if jwt is not None:
        mail_content = mail_content_initial.replace(
            "$INSERT_LINK_HERE",
            "https://leximpact.an.fr/connection/{}".format(jwt.encoded),
        )
        send_mail(
            recipient=params["body"]["email"],
            subject="Lien de connexion LexImpact IR",
            content=mail_content,
        )
        logging.info(f"Token JWT sent to {email}")
    else:
        logging.warning(f"JWT is None for {email}, please check that email is in users table.")
    return (
        "Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation",
        200,
    )

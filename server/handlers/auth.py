from typing import Dict, Tuple
from server.services import login_user, check_user, with_session, send_mail


@with_session
def login(session, **params: Dict[str, str]) -> Tuple[str, int]:
    jwt = login_user(session, params["body"]["email"])
    if jwt is not None:
        mail_content = "Votre adresse e-mail est valide, voici votre <a href=https://leximpact.beta.gouv.fr/connection/{}>lien vers Leximpact POP</a>".format(
            jwt.encoded
        )
        send_mail(
            recipient=params["body"]["email"],
            subject="your magic link or token",
            content=mail_content,
        )
    return (
        "Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation",
        200,
    )

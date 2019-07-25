from typing import Dict, Tuple
from server.services import login_user, with_session,send_mail


@with_session
def login(session, **params: Dict[str, str]) -> Tuple[str, int]:
    jwt=login_user(session, params["body"]["email"])
    if jwt is not None:
        mail_content="<a href=https://leximpact.beta.gouv.fr/{}>Here's your link my friend. Why am I speaking english?</a>".format(jwt.encoded)
        send_mail(recipient=params["body"]["email"],subject="your magic link or token",content=mail_content)
    return "Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation", 200

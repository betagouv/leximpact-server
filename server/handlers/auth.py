from typing import Dict, Tuple
from server.services import login_user, with_session, send_mail


# Ces lignes horribles sont nécessaires car l'appli et les tests ne s'exécutent pas du même folder
try:
    with open("../assets/MailEmailLinkToken.html", "r", encoding="utf-8") as file:
        mail_content_initial = file.read()
except FileNotFoundError:
    with open("assets/MailEmailLinkToken.html", "r", encoding="utf-8") as file:
        mail_content_initial = file.read()


@with_session
def login(session, **params: Dict[str, str]) -> Tuple[str, int]:
    email = params["body"]["email"].lower()
    domains = email.split("@")
    if len(domains) != 2:
        return "Erreur : L'email n'est pas au bon format (pas le bon nombre de @)", 200
    jwt = login_user(session, email)
    if jwt is not None:
        mail_content = mail_content_initial.replace(
            "$INSERT_LINK_HERE",
            "https://leximpact.an.fr/connection/{}".format(jwt.encoded),
        )
        send_mail(
            recipient=params["body"]["email"],
            subject="Lien de connexion LexImpact POP",
            content=mail_content,
        )
    return (
        "Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation",
        200,
    )

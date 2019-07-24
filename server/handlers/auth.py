from typing import Dict, Tuple
from server.services import login_user, with_session


@with_session
def login(session, **params: Dict[str, str]) -> Tuple[str, int]:
    jwt=login_user(session, params["body"]["email"])
    if jwt is not None:
        return str(token.encoded), 201

    return "", 401

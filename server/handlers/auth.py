from typing import Dict, Tuple
from server.services import login_user, with_session


@with_session
def login(session, **params: Dict[str, str]) -> Tuple[str, int]:
    if login_user(session, params["body"]["email"]):
        return "", 201

    return "", 401

from pytest import fixture  # type: ignore
from models import User, create_user, find_user  # type: ignore
from server.services import login_user, check_user  # type: ignore
from models import create_request, count_requests
from datetime import datetime, timedelta
#from models.request import create_request, count_requests

from models import create_token, create_payload, create_nonce

@fixture
def email():
    return "richard@leximpact.pop"


@fixture
def user(session, email):
    create_user(session, User(email=email))
    return find_user(session, email)


def test_login_user_when_not_in_list(session):
    assert not login_user(session, "malevolent@villain.hacker")

def test_too_much_request(session, user, email):
    # Create token
    jti = create_nonce()
    iss, aud = "Moi", "Toi"
    payload = create_payload(email, jti, iss, aud)
    secret, algo = "asdf1234", "HS256"
    tokenencoded = create_token(payload, secret, algo)
    #tokenencoded = login_user(session, email)
    # Do 19 requests
    for i in range(0,20):
        #create_request(session, email)
        resultat = check_user(session, tokenencoded)
        #print(resultat)
        count = count_requests(session, email, since=timedelta(minutes=-2))
        assert count == i + 1
        assert resultat["success"] == True
    count = count_requests(session, email, since=timedelta(minutes=-2))
    assert count == 20
    #print("Nombre de requêtes : ", count)
    # One more call to ban the user
    resultat = check_user(session, tokenencoded)
    # Check banned
    assert resultat["success"] == False
    assert resultat["error"] == "User is suspended"
    # Check mail is called
    # TODO

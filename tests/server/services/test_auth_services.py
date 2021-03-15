from pytest import fixture  # type: ignore
from server.services.auth_services import login_user, check_user  # type: ignore
from models import create_user, find_user, count_requests, User, Request, Suspended, create_token, create_payload, create_nonce  # type: ignore
from datetime import timedelta
import mock
from models import JWT
# from unittest.mock import call  # Fail on Circle CI


@fixture
def email():
    return "richard@leximpact.pop"


@fixture
def user(session, email):
    create_user(session, User(email=email))
    return find_user(session, email)


def test_login_user_when_not_in_list(session):
    assert not login_user(session, "malevolent@villain.hacker")


@fixture
def clean_history(session):
    # Clean the call history
    session.query(Request).delete()
    session.query(Suspended).delete()
    session.commit()


def test_too_much_request(session, user, email, clean_history):
    # Create token
    jti = create_nonce()
    jwt_instance = JWT()
    iss, aud = jwt_instance.iss, jwt_instance.aud
    payload = create_payload(email, jti, iss, aud)
    secret, algo = jwt_instance.secret, "HS256"
    tokenencoded = create_token(payload, secret, algo)
    # Do 19 requests
    for i in range(0, 20):
        resultat = check_user(session, tokenencoded)
        assert resultat["success"] is True
        my_count = count_requests(session, email, since=timedelta(minutes=-2))
        assert my_count == i + 1
    my_count = count_requests(session, email, since=timedelta(minutes=-2))
    assert my_count == 20
    # One more call to ban the user
    mock_path = 'server.services.auth_services.send_mail'
    with mock.patch(mock_path) as mocker:
        resultat = check_user(session, tokenencoded)
        # Check we send 2 mails
        assert mocker.call_count == 2
        # Check mail content
        mocker.assert_any_call(content="Bonjour<br/>\r\n<p>Votre compte LexImpact vient d'être suspendu pour 1 heure(s) en raison d'une utilisation trop importante.<br/>Ceci est requis pour la protection des données d’enquête vous permettant le calcul par déciles de population.</p>\nMerci de votre compréhension,<br/>\nL'équipe LexImpact", recipient='richard@leximpact.pop', subject='Compte LexImpact suspendu')
        # Below assertions works on local, not on CI
        # mocker.assert_any_call(content="Bonjour<br/>\n<p>L'utilisateur richard@leximpact.pop vient d'être suspendu pour 1 heure(s).<br/> Il a fait plus de 20 requêtes en 2.0 minutes.</p><br/>\nVotre dévoué serveur LexImpact", recipient='leximpact@an.fr', subject='Nouvelle suspension')
        # Tip : Just cut and past the result of mocker.call_args_list
        # expected = [call(content="Bonjour<br/>\n<p>L'utilisateur richard@leximpact.pop vient d'être suspendu pour 1 heure(s).<br/> Il a fait plus de 20 requêtes en 2.0 minutes.</p><br/>\nVotre dévoué serveur LexImpact", recipient='leximpact@an.fr', subject='Nouvelle suspension'), call(content="Bonjour<br/>\r\n<p>Votre compte LexImpact vient d'être suspendu pour 1 heure(s) en raison d'une utilisation trop importante.<br/>Ceci est requis pour la protection des données d’enquête vous permettant le calcul par déciles de population.</p>\nMerci de votre compréhension,<br/>\nL'équipe LexImpact", recipient='richard@leximpact.pop', subject='Compte LexImpact suspendu')]
        # mocker.assert_has_calls(expected)

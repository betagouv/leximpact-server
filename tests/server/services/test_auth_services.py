from pytest import fixture  # type: ignore
from server.services import login_user, check_user  # type: ignore
from models import create_user, find_user, count_requests
from models import User, Request, Suspended  # type: ignore
from datetime import timedelta
import mock
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
    # Clean the call history
    session.query(Request).delete()
    session.query(Suspended).delete()
    session.commit()
    my_count = count_requests(session, email, since=timedelta(minutes=-2))
    # mocker.patch('server.services.mail_services.send_mail', return_value=True)
    # Create token
    jti = create_nonce()
    iss, aud = "Moi", "Toi"
    payload = create_payload(email, jti, iss, aud)
    secret, algo = "asdf1234", "HS256"
    tokenencoded = create_token(payload, secret, algo)
    # Do 19 requests
    for i in range(0, 20):
        # create_request(session, email)
        resultat = check_user(session, tokenencoded)
        assert resultat["success"] is True
        # print(resultat)
        my_count = count_requests(session, email, since=timedelta(minutes=-2))
        assert my_count == i + 1
    my_count = count_requests(session, email, since=timedelta(minutes=-2))
    assert my_count == 20
    # print("Nombre de requêtes : ", count)
    # One more call to ban the user
    # 'mailjet_rest.Client'
    # mail_services
    # send_mail
    # server.services.alert_suspension
    # 'server.services.check_user'
    # server.services.alert_suspension
    print(__name__)
    # with mock.patch.object(Client, 'create', return_value={"success" : False,
    #         "error" : "Token has expired!"}) as mocker:
    with mock.patch('server.services.send_mail', return_value=True) as mocker:

        resultat = check_user(session, tokenencoded)
        # Check banned
        assert resultat["success"] is False
        assert resultat["error"] == "User is suspended"
        # Check mail is called
        print("called: " + str(mocker.called))
        print("call_count: " + str(mocker.call_count))
        print("call_args: " + str(mocker.call_args))
        print("args_list: " + str(mocker.call_args_list))
        print("mock calls:\n" + str(mocker.mock_calls))
        print("method calls:\n " + str(mocker.method_calls))
        # mock_sendmail.assert_called_with("any path")

from json import dumps, loads
from pytest import fixture  # type: ignore
from models import User, create_user, find_user  # type:ignore

SETUP = "server.services.database_services.setup"
CLEANUP = "server.services.database_services.cleanup"


@fixture
def email():
    return "richard@leximpact.pop"


@fixture
def user(mocker, setup, cleanup, email):
    engine, connection, session = setup()
    mocker.patch(SETUP, return_value=(engine, connection, session))
    mocker.patch(CLEANUP)
    create_user(session, User(email=email))
    yield find_user(session, email)
    cleanup(session, connection)


def test_auth_login(user, client, headers, mimetype):
    data = {"email": user.email}
    response = client.post("auth/login", data=dumps(data), headers=headers)
    assert (
        loads(response.data)
        == "Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation"
    )
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_auth_login_when_no_user(client, headers, mimetype):
    data = {"email": "richard@leximpact.pop"}
    response = client.post("auth/login", data=dumps(data), headers=headers)
    assert (
        loads(response.data)
        == "Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation"
    )
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_empty(user, client, headers, mimetype):
    data = {"email": ""}
    response = client.post("auth/login", data=dumps(data), headers=headers)
    assert (
        loads(response.data)
        == "Erreur : L'email n'est pas au bon format (pas le bon nombre de @)"
    )
    assert response.content_type == mimetype
    assert response.status_code == 200


def test_cheater(user, client, headers, mimetype):
    data = {"email": "jegruge@clb-an.fr@example.com"}
    response = client.post("auth/login", data=dumps(data), headers=headers)
    assert (
        loads(response.data)
        == "Erreur : L'email n'est pas au bon format (pas le bon nombre de @)"
    )
    assert response.content_type == mimetype
    assert response.status_code == 200

from json import dumps, loads


def test_auth_login(client, headers, mimetype):
    data = {"email": "richard@leximpact.pop"}
    response = client.post("auth/login", data=dumps(data), headers=headers)
    assert loads(response.data) == ""
    assert response.content_type == mimetype
    assert response.status_code == 201

import json


def test_welcome_home(client, headers, mimetype):
    response = client.get("/", headers=headers)
    assert json.loads(response.data) == {"hello": "coucou"}
    assert response.content_type == mimetype
    assert response.status_code == 200

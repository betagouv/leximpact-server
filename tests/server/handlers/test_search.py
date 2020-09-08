from functools import partial
import json


def test_missing_param(client, headers):
    response_function = partial(client.get, "search?oupsjemetrompe=dijon", headers=headers)
    response = response_function()

    assert response.status_code == 400
    assert "Missing query parameter 'commune'" in json.loads(response.data)['detail']


def test_ok(client, headers):
    response_function = partial(client.get, "search?commune=paris", headers=headers)
    response = response_function()

    assert response.status_code == 200
    response_list = json.loads(response.data)
    assert len(response_list) > 0


def test_empty(client, headers):
    response_function = partial(client.get, "search?commune=", headers=headers)
    response = response_function()

    assert response.status_code == 400
    assert "Error" in json.loads(response.data)

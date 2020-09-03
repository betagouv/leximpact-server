from functools import partial
import json


def test_missing_param(client, headers):
    request = {
        "oupsjemetrompe": "dijon"
    }

    response_function = partial(client.post, "recherche_commune", headers=headers)
    response = response_function(data=json.dumps(request))

    assert response.status_code == 400
    assert "Error" in json.loads(response.data)


def test_empty(client, headers):
    request = {
        "extraitNomCommune": ""
    }

    response_function = partial(client.post, "recherche_commune", headers=headers)
    response = response_function(data=json.dumps(request))

    assert response.status_code == 400
    assert "Error" in json.loads(response.data)

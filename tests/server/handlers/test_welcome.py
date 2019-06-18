# -*- coding: utf-8 -*-

import json


def test_welcome_home(client, headers, mimetype):
    response = client.get("/", headers=headers)
    assert response.content_type == mimetype
    assert response.status_code == 200
    assert json.loads(response.data) == {"hello": "coucou"}

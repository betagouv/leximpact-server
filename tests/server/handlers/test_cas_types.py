# -*- coding: utf-8 -*-

import pytest
import json

from server.app import create_app


@pytest.fixture
def client():
    app = create_app()
    client = app.app.test_client()
    return client


@pytest.fixture
def mimetype() -> str:
    return "application/json"


@pytest.fixture
def headers(mimetype: str) -> dict:
    return {"Content-Type": mimetype, "Accept": mimetype}


@pytest.fixture
def data() -> str:
    return {
        "reform": {"variable": "name", "operation": "+", "times": "3"},
        "cas_types": [{"name": "Dorine"}],
    }


def test_calculate(client, data, headers, mimetype):
    response = client.post(
        "/calculate/cas_types", data=json.dumps(data), headers=headers
    )
    assert response.content_type == mimetype
    assert response.status_code == 201
    assert json.loads(response.data) == [{"name": "DorineDorineDorine"}]

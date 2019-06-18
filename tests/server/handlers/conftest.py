# -*- coding: utf-8 -*-

import pytest

from server.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    return client


@pytest.fixture
def mimetype() -> str:
    return "application/json"


@pytest.fixture
def headers(mimetype: str) -> dict:
    return {"Content-Type": mimetype, "Accept": mimetype}

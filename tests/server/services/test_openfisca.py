# -*- coding: utf-8 -*-

from typing import Callable, List

import pytest

from server.services import OpenFisca


@pytest.fixture
def reform() -> Callable:
    return lambda x: x * 2


@pytest.fixture
def cas_types() -> List[dict]:
    return [{"name": "Augustin"}]


def test_cas_type(reform, cas_types):
    impact = OpenFisca.cas_type(reform=reform, cas_types=cas_types)
    assert {"name": "AugustinAugustin"} in impact

from typing import List

import pytest

from server.services import OpenFisca


@pytest.fixture
def reform() -> dict:
    return {"variable": "name", "operation": "*", "times": "2"}


@pytest.fixture
def cas_types() -> List[dict]:
    return [{"name": "Augustin"}]


def test_cas_types(reform, cas_types):
    impact = OpenFisca.cas_types(reform=reform, cas_types=cas_types)
    assert {"name": "AugustinAugustin"} in impact

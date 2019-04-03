# -*- coding: utf-8 -*-

import pytest

from interface_reform.components import GraphCasType


@pytest.fixture
def index() -> int:
    return 0


def test_render(index):
    assert str(index) in str(GraphCasType.render(index=index))

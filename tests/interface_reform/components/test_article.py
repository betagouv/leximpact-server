# -*- coding: utf-8 -*-

import pytest

from interface_reform.components import Article


@pytest.fixture
def arguments() -> dict:
    return {
        "sizev": 1,
        "sizeperc": 1,
        "seuil0": 9964,
        "taux0": 14,
        "seuil1": 27519,
        "taux1": 30,
        "seuil2": 73779,
        "taux2": 41,
        "seuil3": 156244,
        "taux3": 45,
    }


def test_render(arguments):
    article = Article.render(**arguments)

    for _key, value in arguments.items():
        assert str(value) in str(article)

# -*- coding: utf-8 -*-

from Simulation_engine.simulate_pop_from_reform import (
    adjustment,
    adjust_total,
    adjust_deciles,
)


def test_adjustement():
    assert adjustment(4, 2) == 2


def test_adjust_total():
    actual = adjust_total(2, {"avant": 2, "apres": 4})
    expected = {"avant": 4, "apres": 8}

    assert actual == expected


def test_adjust_deciles():
    actual = adjust_deciles(2, [{"poids": 1, "avant": 2, "apres": 3}])
    expected = [{"poids": 2, "avant": 4, "apres": 6}]

    assert actual == expected

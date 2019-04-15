# -*- coding: utf-8 -*-

from interface_reform.components import Header


def test_render():
    assert "LexImpact" in str(Header.render())

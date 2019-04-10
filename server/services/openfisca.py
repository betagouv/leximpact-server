# -*- coding: utf-8 -*-

from typing import Callable, List


class OpenFisca(object):
    def cas_type(reform: Callable, cas_types: List[dict]) -> List[dict]:
        """Calcule l'impact d'une réforme par cas types"""
        return [{"name": reform(cas_type["name"])} for cas_type in cas_types]

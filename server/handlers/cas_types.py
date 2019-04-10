# -*- coding: utf-8 -*-

from server.services import OpenFiscaTest
from Simulation_engine.simulate_pop_from_reform import foyertosomethingelse

class CasTypes(object):
    def calculate(**params: dict) -> tuple:
        """Pour gérer les requêtes et envoyer de résultats"""
        return OpenFiscaTest.cas_types(**params["body"]), 201
    def totext(**params: dict) -> tuple:
        return [{"surlefoyer":foyertosomethingelse(**params["body"])}],201


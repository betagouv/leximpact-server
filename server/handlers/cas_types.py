# -*- coding: utf-8 -*-

from server.services import OpenFiscaTest
from Simulation_engine.simulate_pop_from_reform import foyertosomethingelse,CompareOldNew

class CasTypes(object):
    def calculate(**params: dict) -> tuple:
        """Pour gérer les requêtes et envoyer de résultats"""
        return OpenFiscaTest.cas_types(**params["body"]), 201
    def totext(**params: dict) -> tuple:
        return [{"surlefoyer":foyertosomethingelse(**params["body"])}],201

class SimulationRunner(object):
    def compare(**params: dict) -> tuple:
        dbod=params["body"]
        return [CompareOldNew(dbod["bareme_ir"]["seuils"]+dbod["bareme_ir"]["taux"],dbod["deciles"])],201
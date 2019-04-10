# -*- coding: utf-8 -*-

from server.services import OpenFisca


class CasTypes(object):
    def calculate(**params: dict) -> dict:
        """Pour gérer les requêtes et envoyer de résultats"""
        return OpenFisca.cas_types(**params["body"]), 201

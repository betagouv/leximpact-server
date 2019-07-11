from server.services import OpenFisca
from Simulation_engine.simulate_pop_from_reform import (
    desc_cas_types,
    CompareOldNew,
    revenus_cas_types,
)


class CasTypes(object):
    def calculate(**params: dict) -> tuple:
        """Pour gérer les requêtes et envoyer de résultats"""
        return OpenFisca.cas_types(**params["body"]), 201

    def revenus(**params: dict) -> tuple:
        rct = revenus_cas_types()
        return {int(k): int(v) for k, v in rct.items()}, 201

    def description_cas_types(**params: dict) -> tuple:
        rct = desc_cas_types()
        return rct, 201


class SimulationRunner(object):
    def compare(**params: dict) -> tuple:
        dbod = params["body"]
        return (
            [
                CompareOldNew(
                    dbod["bareme_ir"]["seuils"] + dbod["bareme_ir"]["taux"],
                    dbod["deciles"],
                )
            ],
            201,
        )

    def simulereforme(**params: dict) -> tuple:
        dbod = params["body"]
        dct = None
        if "description_cas_types" in dbod:
            isdecile = False
            dct = dbod["description_cas_types"]
        else:
            isdecile = dbod["deciles"]
        return (
            CompareOldNew(
                taux=None,
                isdecile=isdecile,
                dictreform=dbod["reforme"],
                castypedesc=dct,
            ),
            201,
        )

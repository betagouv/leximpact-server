from Simulation_engine.simulate_pop_from_reform import (
    desc_cas_types,
    CompareOldNew,
    revenus_cas_types,
)
from server.services import check_user, with_session
from datetime import datetime


def error_as_dict(errormessage):
    return {"Error": errormessage}


class CasTypes(object):
    def revenus(**params: dict) -> tuple:
        rct = revenus_cas_types()
        return {int(k): int(v) for k, v in rct.items()}, 201

    def description_cas_types(**params: dict) -> tuple:
        rct = desc_cas_types()
        return rct, 201


class SimulationRunner(object):
    def simulereforme(**params: dict) -> tuple:
        timestamprequest = datetime.now()
        dbod = params["body"]
        dct = None
        if "description_cas_types" in dbod:
            dct = dbod["description_cas_types"]
        if "reforme" not in dbod:
            return error_as_dict("missing 'reforme' field in body of your request"),200
        dic_resultat = CompareOldNew(
            taux=None, isdecile=False, dictreform=dbod["reforme"], castypedesc=dct
        )
        dic_resultat["timestamp"] = timestamprequest
        return (dic_resultat, 201)

    @with_session
    def simuledeciles(session, **params: dict) -> tuple:
        timestamprequest = datetime.now()
        dbod = params["body"]
        if "reforme" not in dbod:
            return error_as_dict("missing 'reforme' field in body of your request"),200
        if "token" not in dbod:
            return error_as_dict("missing token : necessary for this request"), 200
        CU = check_user(session, dbod["token"])
        if CU["success"] is False:
            return error_as_dict(CU["error"]), 200
        if "description_cas_types" in dbod:
            return (
                error_as_dict("bad request, no description_cas_types should appear"),
                200,
            )

        dic_resultat = CompareOldNew(
            taux=None, isdecile=True, dictreform=dbod["reforme"], castypedesc=None
        )
        dic_resultat["timestamp"] = timestamprequest
        return (dic_resultat, 200)

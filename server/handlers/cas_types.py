from Simulation_engine.simulate_pop_from_reform import (
    desc_cas_types,
    CompareOldNew,
    revenus_cas_types,
)
from server.services import check_user, with_session
import json
from flask import Response

from Simulation_engine.lexception import LexCeption

def error_as_dict(errormessage):
    return {"Error": errormessage}


def simpop_stream(dbod):
    yield "\n"
    dic_resultat = CompareOldNew(
        taux=None, isdecile=True, dictreform=dbod["reforme"], castypedesc=None
    )
    if "timestamp" in dbod:
        dic_resultat["timestamp"] = dbod["timestamp"]
    yield json.dumps(dic_resultat)


class CasTypes(object):
    def revenus(**params: dict) -> tuple:
        rct = revenus_cas_types()
        return {int(k): int(v) for k, v in rct.items()}, 201

    def description_cas_types(**params: dict) -> tuple:
        rct = desc_cas_types()
        return rct, 201


class SimulationRunner(object):
    def simulereforme(**params: dict) -> tuple:
        dbod = params["body"]
        dct = None
        if "description_cas_types" in dbod:
            dct = dbod["description_cas_types"]
            if not len(dct):
                return error_as_dict("Empty list of cas types received"), 200
        if "reforme" not in dbod:
            return error_as_dict("missing 'reforme' field in body of your request"), 200
        try:
            dic_resultat = CompareOldNew(
                taux=None, isdecile=False, dictreform=dbod["reforme"], castypedesc=dct
            )
        except LexCeption as exc:
            return error_as_dict("Threw an Exception : " + str(exc)), 200

        if "timestamp" in dbod:
            dic_resultat["timestamp"] = dbod["timestamp"]
        return (dic_resultat, 201)

    @with_session
    def simuledeciles(session, **params: dict) -> Response:
        dbod = params["body"]
        if "reforme" not in dbod:
            return Response(
                json.dumps(
                    error_as_dict("missing 'reforme' field in body of your request")
                ),
                status=200,
            )
        if "token" not in dbod:
            return Response(
                json.dumps(error_as_dict("missing token: necessary for this request")),
                status=200,
            )
        CU = check_user(session, dbod["token"])
        if CU["success"] is False:
            return Response(json.dumps(error_as_dict(CU["error"])), status=200)
        if "description_cas_types" in dbod:
            return Response(
                json.dumps(
                    error_as_dict("bad request, no description_cas_types should appear")
                ),
                status=200,
            )
        return Response(
            simpop_stream(dbod), status=200, content_type="application/json"
        )

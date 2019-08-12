from Simulation_engine.simulate_pop_from_reform import (
    desc_cas_types,
    CompareOldNew,
    revenus_cas_types,
)
from server.services import check_user, with_session
from models.request import create_request


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

    @with_session
    def simuledeciles(session, **params: dict) -> tuple:
        dbod = params["body"]
        if "token" not in dbod:
            return error_as_dict("missing token : necessary for this request"), 200
        CU = check_user(session, dbod["token"])
        if CU["success"] is False:
            return error_as_dict(CU["error"]), 200
        email = CU["email"]
        create_request(session, email)
        if "description_cas_types" in dbod:
            return (
                error_as_dict("bad request, no description_cas_types should appear"),
                200,
            )

        return (
            error_as_dict(
                "Request was valid, but population comparison not yet implemented on server side"
            ),
            200,
        )
        return (
            CompareOldNew(
                taux=None, isdecile=True, dictreform=dbod["reforme"], castypedesc=None
            ),
            200,
        )

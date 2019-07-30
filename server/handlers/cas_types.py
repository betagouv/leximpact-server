from Simulation_engine.simulate_pop_from_reform import (
    desc_cas_types,
    CompareOldNew,
    revenus_cas_types,
)
from server.services import login_user, check_user,with_session,send_mail, create_request


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
    def simuledeciles(session,**params: dict) -> tuple:
        dbod = params["body"]
        email=check_user(session,dbod["token"]) if "token" in dbod else None
        if "token" in dbod and email is not None:
            dct = None
            if "description_cas_types" in dbod:
                return "bad request, no description_cas_types should be there",401
            return (
                CompareOldNew(
                    taux=None,
                    isdecile=True,
                    dictreform=dbod["reforme"],
                    castypedesc=None,
                ),
                201,
            )
        return "error with the token",401
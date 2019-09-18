from openfisca_france import FranceTaxBenefitSystem  # type: ignore

class WarmUp(object):
    def load_taxbenefits_system(**params: dict) -> tuple:
        TBS = FranceTaxBenefitSystem()
        return {"Status": "A chargé en mémoire OpenFisca-France vX"}, 200

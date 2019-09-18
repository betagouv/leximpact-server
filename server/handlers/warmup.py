from openfisca_france import FranceTaxBenefitSystem  # type: ignore


class WarmUp(object):
    def load_tax_benefits_system(**params: dict) -> tuple:
        tax_benefits_system = FranceTaxBenefitSystem()
        version = tax_benefits_system.get_package_metadata()['version']

        return {"status": f"A chargé en mémoire OpenFisca-France v{version}"}, 200

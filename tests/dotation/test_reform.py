from dotation.reform import DotationReform  # type: ignore
from openfisca_france_dotations_locales import CountryTaxBenefitSystem  # type: ignore


def test_correct_reform_applied():
    tbs = CountryTaxBenefitSystem()
    value_to_set = 793
    description_reforme = {
        "dgf": {
            "dotation_solidarite_rurale": {
                "cible": {
                    "eligibilite": {
                        "seuil_classement" : value_to_set
                    }
                }
            }
        }
    }
    tbs_modified = DotationReform(tbs, description_reforme)

    print(tbs_modified.get_parameters_at_instant("2020-01-01")["dotation_solidarite_rurale"]["cible"]["eligibilite"]["seuil_classement"] == value_to_set)

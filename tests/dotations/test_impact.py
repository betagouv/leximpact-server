from Simulation_engine.simulate_dotations import format_reforme_openfisca


def test_format_reforme_openfisca():
    request_body = {
        "reforme": {
            "dotations": {
                "montants": {},
                "communes" : {
                    "dsr" : {
                        "cible": {
                            "eligibilite": {
                                "premieresCommunes": 23
                            }
                        }
                    }
                }
            }
        }
    }

    expected_openfisca_request = {
        "dgf": {
            "dotation_solidarite_rurale": {
                "cible": {
                    "eligibilite": {
                        "seuil_classement": 23
                    }
                }
            }
        }
    }

    assert format_reforme_openfisca(request_body["reforme"]) == expected_openfisca_request

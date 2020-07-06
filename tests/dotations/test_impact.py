from dotations.impact import format_reforme_openfisca


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
    # print(impacts_reforme_dotation(format_reforme_openfisca(request_body["reforme"])))

    expected_openfisca_request = reforme_example = {
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

from dotations.impact import BORNES_STRATES, format_reforme_openfisca, impacts_reforme_dotation  # type: ignore


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


def test_impacts_reforme_dotation():
    reforme_example = {
        "reforme": {
            "dotations": {
                "montants": {
                    "dgf": 31
                },
                "communes": {
                    "dsr": {
                        "eligibilite": {
                            "popMax": 500  # de 10 000 à 500
                        }
                    }
                }
            }
        }
    }
    # avant réforme : +11 000 communes éligibles à la DSR (toutes fractions comprises)
    expected_reform_impact = {
        "amendement": {
            "dotations": {
                "communes": {
                    "dsr": {
                        "communes": [
                            {
                                "code": "76384",
                                "eligible": False
                            },
                            {
                                "code": "76214",
                                "eligible": True
                            }
                        ],
                        "eligibles": 17049,
                        "nouvellementEligibles": 0,
                        "plusEligibles": 16115,
                        "strates": [
                            {
                                "eligibles": 16924,
                                "habitants": 0,
                                "partPopTotale": 0.0603242951533041,
                                "potentielFinancierMoyenParHabitant": 761.7826724474608
                            },
                            {
                                "eligibles": 1,
                                "habitants": 500,
                                "partPopTotale": 0.16357006593471596,
                                "potentielFinancierMoyenParHabitant": 822.7862081792102
                            },
                            {
                                "eligibles": 27,
                                "habitants": 2000,
                                "partPopTotale": 0.1481666253006925,
                                "potentielFinancierMoyenParHabitant": 962.3232471567082
                            },
                            {
                                "eligibles": 47,
                                "habitants": 5000,
                                "partPopTotale": 0.12193926697939683,
                                "potentielFinancierMoyenParHabitant": 1061.3215646634023
                            },
                            {
                                "eligibles": 50,
                                "habitants": 10000,
                                "partPopTotale": 0.11254269030454657,
                                "potentielFinancierMoyenParHabitant": 1142.2386532655016
                            },
                            {
                                "eligibles": 0,
                                "habitants": 20000,
                                "partPopTotale": 0.15472973351983596,
                                "potentielFinancierMoyenParHabitant": 1212.5588966550042
                            },
                            {
                                "eligibles": 0,
                                "habitants": 50000,
                                "partPopTotale": 0.08756806900354432,
                                "potentielFinancierMoyenParHabitant": 1322.006448304583
                            },
                            {
                                "eligibles": 0,
                                "habitants": 100000,
                                "partPopTotale": 0.15115925380396375,
                                "potentielFinancierMoyenParHabitant": 1450.6968113217495
                            }
                        ]
                    }
                }
            }
        },
        "base": {
            "dotations": {
                "communes": {
                    "dsr": {
                        "communes": [
                            {
                                "code": "76384",
                                "eligible": False
                            },
                            {
                                "code": "76214",
                                "eligible": True
                            }
                        ],
                        "eligibles": 33164,
                        "strates": [
                            {
                                "eligibles": 17752,
                                "habitants": 0,
                                "partPopTotale": 0.0603242951533041,
                                "potentielFinancierMoyenParHabitant": 761.7826724474608
                            },
                            {
                                "eligibles": 11103,
                                "habitants": 500,
                                "partPopTotale": 0.16357006593471596,
                                "potentielFinancierMoyenParHabitant": 822.7862081792102
                            },
                            {
                                "eligibles": 3165,
                                "habitants": 2000,
                                "partPopTotale": 0.1481666253006925,
                                "potentielFinancierMoyenParHabitant": 962.3232471567082
                            },
                            {
                                "eligibles": 1089,
                                "habitants": 5000,
                                "partPopTotale": 0.12193926697939683,
                                "potentielFinancierMoyenParHabitant": 1061.3215646634023
                            },
                            {
                                "eligibles": 55,
                                "habitants": 10000,
                                "partPopTotale": 0.11254269030454657,
                                "potentielFinancierMoyenParHabitant": 1142.2386532655016
                            },
                            {
                                "eligibles": 0,
                                "habitants": 20000,
                                "partPopTotale": 0.15472973351983596,
                                "potentielFinancierMoyenParHabitant": 1212.5588966550042
                            },
                            {
                                "eligibles": 0,
                                "habitants": 50000,
                                "partPopTotale": 0.08756806900354432,
                                "potentielFinancierMoyenParHabitant": 1322.006448304583
                            },
                            {
                                "eligibles": 0,
                                "habitants": 100000,
                                "partPopTotale": 0.15115925380396375,
                                "potentielFinancierMoyenParHabitant": 1450.6968113217495
                            }
                        ]
                    }
                }
            }
        }
    }

    result = impacts_reforme_dotation(reforme_example)
    assert "base" in result
    assert "amendement" in result

    base_dsr = result["base"]["dotations"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["dotations"]["communes"]["dsr"]
    # même nombre de cas types en loi actuelle et amendement
    assert len(base_dsr["communes"]) == len(amendement_dsr["communes"])

    assert (len(BORNES_STRATES) - 1) == len(base_dsr["strates"]) == len(amendement_dsr["strates"])
    assert (BORNES_STRATES[:-1]
            == [description_strate["habitants"] for description_strate in base_dsr["strates"]]
            == [description_strate["habitants"] for description_strate in amendement_dsr["strates"]]
            )

    assert result == expected_reform_impact

from functools import partial
import json

from dotations.impact import BORNES_STRATES, get_cas_types_codes_insee  # type: ignore
from dotations.utils_dict import flattened_dict  # type: ignore


def test_dotations_request_body_error(client, headers):
    request = {}

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))

    assert response.status_code == 400
    assert "Error" in json.loads(response.data)


def test_dotations(client, headers):
    request = {
        "reforme": {
            "dotations": {
                "montants": {"dgf": 16},
                "communes": {}
            }
        }
    }

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))

    assert response.status_code == 200


def test_dsr_reform_popMax(client, headers):
    request = {
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

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))
    result = json.loads(response.data)

    assert "base" in result
    assert "amendement" in result

    base_dsr = result["base"]["dotations"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["dotations"]["communes"]["dsr"]
    # même nombre de cas types en loi actuelle et amendement
    # Les cas_types sont ceux attendus
    codes_communes = get_cas_types_codes_insee()
    assert (codes_communes
            == [cas_type["code"] for cas_type in base_dsr["communes"]]
            == [cas_type["code"] for cas_type in amendement_dsr["communes"]]
            )

    assert (len(BORNES_STRATES) - 1) == len(base_dsr["strates"]) == len(amendement_dsr["strates"])
    assert (BORNES_STRATES[:-1]
            == [description_strate["habitants"] for description_strate in base_dsr["strates"]]
            == [description_strate["habitants"] for description_strate in amendement_dsr["strates"]]
            )

    # Vérification des clefs du dictionnaire (sauf celles inclues dans un array)
    flattened_result_keys = set(flattened_dict(result).keys())
    flattened_expected_keys = set(flattened_dict(expected_reform_impact).keys())
    assert flattened_result_keys == flattened_expected_keys

    assert result == expected_reform_impact

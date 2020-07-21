from functools import partial
import json

from dotations.impact import BORNES_STRATES_DEFAULT, get_cas_types_codes_insee  # type: ignore
from dotations.utils_dict import flattened_dict  # type: ignore


def request_strates_from_bornes_strates(bornes_strates):
    bornes_strates[-1] = -1
    return [{"habitants": borne} for borne in bornes_strates[1:]]


def _distance_listes(a, b):
    return max([abs(x - y) for (x, y) in zip(a, b)])


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
            },
        },
        "descriptionCasTypes": [],
        "strates": request_strates_from_bornes_strates(BORNES_STRATES_DEFAULT),
    }

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))

    assert response.status_code == 200


def test_dsr_reform_eligibilite_montants(client, headers):
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
        },
        "descriptionCasTypes": [],
        "strates": request_strates_from_bornes_strates(BORNES_STRATES_DEFAULT),

    }
    # avant réforme : +11 000 communes éligibles à la DSR (toutes fractions comprises)
    expected_reform_impact = {
        "amendement": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 17049,
                    "strates": []
                }
            }
        },
        "base": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 33164,
                    "strates": []
                }
            }
        },
        "baseToAmendement": {
            "communes": {
                "dsr" : {
                    "nouvellementEligibles": 0,
                    "plusEligibles": 16115,
                    "toujoursEligibles": 17049,
                }
            }
        }
    }

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))
    result = json.loads(response.data)

    # Vérification des clefs du dictionnaire (sauf celles inclues dans un array)
    flattened_result_keys = set(flattened_dict(result).keys())
    flattened_expected_keys = set(flattened_dict(expected_reform_impact).keys())
    assert flattened_result_keys == flattened_expected_keys

    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]

    # Vérification des valeurs connues :

    # Les nombres de communes éligibles de base sont ceux attendus
    expected_strates_eligibilite_base = [17752, 11103, 3165, 1089, 55, 0, 0, 0]
    assert expected_strates_eligibilite_base == [strate["eligibles"] for strate in base_dsr["strates"]]

    # Moins de communes éligibles après que avant.
    assert (base_dsr["eligibles"] > amendement_dsr["eligibles"])
    # Les nombres affichés dans l'amendement sont cohérents avec la base
    base_to_amendement = result["baseToAmendement"]["communes"]["dsr"]
    assert(amendement_dsr["eligibles"] == base_to_amendement["toujoursEligibles"] + base_to_amendement["nouvellementEligibles"])
    assert(base_dsr["eligibles"] == amendement_dsr["eligibles"] - base_to_amendement["nouvellementEligibles"] + base_to_amendement["plusEligibles"])

    # Montants : cohérence : les strates ont une dotation non nulle si et seulement si elles sont éligibles
    for scenario_strates in [base_dsr["strates"], amendement_dsr["strates"]]:
        for strate in scenario_strates:
            assert((strate["dotationMoyenneParHab"] > 0) == (strate["eligibles"] > 0))


def test_dsr_reform_cas_types(client, headers):
    codes_communes = get_cas_types_codes_insee()
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
        },
        "descriptionCasTypes": [
            {"code": code_insee_cas_type}
            for code_insee_cas_type in codes_communes
        ],
        "strates": request_strates_from_bornes_strates(BORNES_STRATES_DEFAULT),
    }
    # avant réforme : +11 000 communes éligibles à la DSR (toutes fractions comprises)
    expected_reform_impact = {
        "amendement": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 17049,
                    "strates": []
                }
            }
        },
        "base": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 33164,
                    "strates": []
                }
            }
        },
        "baseToAmendement": {
            "communes": {
                "dsr" : {
                    "nouvellementEligibles": 0,
                    "plusEligibles": 16115,
                    "toujoursEligibles": 17049,
                }
            }
        }
    }

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))
    result = json.loads(response.data)

    # Vérification des clefs du dictionnaire (sauf celles inclues dans un array)
    flattened_result_keys = set(flattened_dict(result).keys())
    flattened_expected_keys = set(flattened_dict(expected_reform_impact).keys())
    assert flattened_result_keys == flattened_expected_keys

    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]

    # même nombre de cas types en loi actuelle et amendement
    # Les cas_types sont ceux attendus
    assert (codes_communes
            == [cas_type["code"] for cas_type in base_dsr["communes"]]
            == [cas_type["code"] for cas_type in amendement_dsr["communes"]]
            )

    # Vérification des clefs du dictionnaire contenues dans un array :
    # cas-types
    expected_cas_type_keys = set(["code", "eligible", "dotationParHab"])
    for cas_type in base_dsr["communes"] + amendement_dsr["communes"]:
        assert set(cas_type.keys()) == expected_cas_type_keys

    # Les deux cas types ont une éligibilité différente avec la loi actuelle (sinon on s'ennuye)
    assert (len(set([cas_type["eligible"] for cas_type in base_dsr["communes"]])) > 1)

    # Montants : cohérence : les cas_types ont une dotation non nulle si et seulement si elles sont éligibles
    for scenario_cas_types in [base_dsr["communes"], amendement_dsr["communes"]]:
        for cas_type in scenario_cas_types:
            assert((cas_type["dotationParHab"] > 0) == cas_type["eligible"])


def test_dsr_reform_strates(client, headers):
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
        },
        "descriptionCasTypes": [],
        "strates": request_strates_from_bornes_strates(BORNES_STRATES_DEFAULT),
    }
    # avant réforme : +11 000 communes éligibles à la DSR (toutes fractions comprises)
    expected_reform_impact = {
        "amendement": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 17049,
                    "strates": []
                }
            }
        },
        "base": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 33164,
                    "strates": []
                }
            }
        },
        "baseToAmendement": {
            "communes": {
                "dsr" : {
                    "nouvellementEligibles": 0,
                    "plusEligibles": 16115,
                    "toujoursEligibles": 17049,
                }
            }
        }
    }

    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request))
    result = json.loads(response.data)

    # Vérification des clefs du dictionnaire (sauf celles inclues dans un array)
    flattened_result_keys = set(flattened_dict(result).keys())
    flattened_expected_keys = set(flattened_dict(expected_reform_impact).keys())
    assert flattened_result_keys == flattened_expected_keys

    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]

    assert (len(BORNES_STRATES_DEFAULT) - 1) == len(base_dsr["strates"]) == len(amendement_dsr["strates"])
    assert (BORNES_STRATES_DEFAULT[:-1]
            == [description_strate["habitants"] for description_strate in base_dsr["strates"]]
            == [description_strate["habitants"] for description_strate in amendement_dsr["strates"]]
            )
    # Vérification des clefs du dictionnaire contenues dans un array :
    # strates
    expected_strates_keys = set(["eligibles", "habitants", "partPopTotale", "potentielFinancierMoyenParHabitant", "dotationMoyenneParHab", "partDotationTotale"])
    for strate in base_dsr["strates"] + amendement_dsr["strates"]:
        assert set(strate.keys()) == expected_strates_keys

    # Vérification des valeurs connues :
    # part des populations des strates
    expected_strates_part_pop = [0.060324, 0.16357, 0.14816, 0.12193, 0.112542, 0.15472, 0.087568, 0.151159]
    expected_strates_potentiel_financier = [761.7826724474608, 822.7862081792102, 962.3232471567082, 1061.3215646634023, 1142.2386532655016, 1212.5588966550042, 1322.006448304583, 1450.6968113217495]
    allowed_error = 0.0001
    for resultat_strates in [base_dsr["strates"], amendement_dsr["strates"]]:
        assert(_distance_listes(expected_strates_part_pop, [strate["partPopTotale"] for strate in resultat_strates]) < allowed_error)
        assert(_distance_listes(expected_strates_potentiel_financier, [strate["potentielFinancierMoyenParHabitant"] for strate in resultat_strates]) < allowed_error)

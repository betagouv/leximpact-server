from functools import partial
import json

from dotations.impact import BORNES_STRATES, get_cas_types_codes_insee  # type: ignore
from dotations.utils_dict import flattened_dict  # type: ignore


def distance_listes(a, b):
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
                        "communes": [],
                        "eligibles": 17049,
                        "nouvellementEligibles": 0,
                        "plusEligibles": 16115,
                        "strates": []
                    }
                }
            }
        },
        "base": {
            "dotations": {
                "communes": {
                    "dsr": {
                        "communes": [],
                        "eligibles": 33164,
                        "strates": []
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

    # Vérification des clefs du dictionnaire contenues dans un array :
    # cas-types
    expected_cas_type_keys = set(["code", "eligible", "dotationParHab"])
    for cas_type in base_dsr["communes"] + amendement_dsr["communes"]:
        assert set(cas_type.keys()) == expected_cas_type_keys
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
        assert(distance_listes(expected_strates_part_pop, [strate["partPopTotale"] for strate in resultat_strates]) < allowed_error)
        assert(distance_listes(expected_strates_potentiel_financier, [strate["potentielFinancierMoyenParHabitant"] for strate in resultat_strates]) < allowed_error)

    # Les nombres de communes éligibles de base sont ceux attendus
    expected_strates_eligibilite_base = [17752, 11103, 3165, 1089, 55, 0, 0, 0]
    assert expected_strates_eligibilite_base == [strate["eligibles"] for strate in base_dsr["strates"]]

    # Moins de communes éligibles après que avant.
    assert (base_dsr["eligibles"] > amendement_dsr["eligibles"])
    # Les nombres affichés dans l'amendement sont cohérents avec la base
    assert(base_dsr["eligibles"] == amendement_dsr["eligibles"] - amendement_dsr["nouvellementEligibles"] + amendement_dsr["plusEligibles"])

    # Les deux cas types ont une éligibilité différente avec la loi actuelle (sinon on s'ennuye)
    assert (len(set([cas_type["eligible"] for cas_type in base_dsr["communes"]])) > 1)

    # Montants : cohérence : les cas_types ont une dotation non nulle si et seulement si elles sont éligibles
    for scenario_cas_types in [base_dsr["communes"], amendement_dsr["communes"]]:
        for cas_type in scenario_cas_types:
            assert((cas_type["dotationParHab"] > 0) == cas_type["eligible"])
    # Montants : cohérence : les strates ont une dotation non nulle si et seulement si elles sont éligibles
    for scenario_strates in [base_dsr["strates"], amendement_dsr["strates"]]:
        for strate in scenario_strates:
            assert((strate["dotationMoyenneParHab"] > 0) == (strate["eligibles"] > 0))

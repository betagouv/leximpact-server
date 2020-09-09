from functools import partial
import json
from pytest import fixture

from dotations.impact import BORNES_STRATES_DEFAULT, get_cas_types_codes_insee  # type: ignore
from utils.utils_dict import flattened_dict  # type: ignore


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


def test_dotations(client, headers, request_dotations):
    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request_dotations))

    assert response.status_code == 200


@fixture(scope="module")
def codes_communes_examples():
    return get_cas_types_codes_insee()


@fixture(scope="module")
def request_dotations(codes_communes_examples):
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
                    },
                    "dsu": {
                        "eligibilite": {
                            "popMinSeuilBas": 500  # de 5 000 à 500
                        }
                    }
                }
            }
        },
        "descriptionCasTypes": [
            {"code": code_insee_cas_type}
            for code_insee_cas_type in codes_communes_examples
        ],
        "strates": request_strates_from_bornes_strates(BORNES_STRATES_DEFAULT),
    }
    return request


@fixture(scope="module")
def response_dotations(client, headers, request_dotations):
    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request_dotations))
    return json.loads(response.data)


@fixture(scope="module")
def request_dotations_2(codes_communes_examples):
    request = {
        "reforme": {
            "dotations": {
                "montants": {
                    "dgf": 31
                },
                "communes": {
                    "dsu": {
                        "eligibilite": {
                            "popMinSeuilHaut": 8000  # de 10 000 à 8 000
                        }
                    }
                }
            }
        },
        "descriptionCasTypes": [
            {"code": code_insee_cas_type}
            for code_insee_cas_type in codes_communes_examples
        ],
        "strates": request_strates_from_bornes_strates(BORNES_STRATES_DEFAULT),
    }
    return request


@fixture(scope="module")
def response_dotations_2(client, headers, request_dotations_2):
    response_function = partial(client.post, "dotations", headers=headers)
    response = response_function(data=json.dumps(request_dotations_2))
    return json.loads(response.data)


def test_fields_response(response_dotations):
    expected_response_structure = {
        "amendement": {
            "communes": {
                "dsr": {
                    "communes": [],
                    "eligibles": 17049,
                    "strates": []
                },
                "dsu": {
                    "communes": [],
                    "eligibles": 812,
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
                },
                "dsu": {
                    "communes": [],
                    "eligibles": 812,
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
                },
                "dsu" : {
                    "nouvellementEligibles": 0,
                    "plusEligibles": 0,
                    "toujoursEligibles": 812,
                }
            }
        }
    }

    result = response_dotations

    # Vérification des clefs du dictionnaire (sauf celles incluses dans un array)
    flattened_result_keys = set(flattened_dict(result).keys())
    flattened_expected_keys = set(flattened_dict(expected_response_structure).keys())
    assert flattened_result_keys == flattened_expected_keys


def test_dsr_reform_eligibilite_montants(response_dotations):
    result = response_dotations
    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]

    # Moins de communes éligibles après que avant.
    assert (base_dsr["eligibles"] > amendement_dsr["eligibles"])
    # Les nombres affichés dans l'amendement sont cohérents avec la base
    base_to_amendement = result["baseToAmendement"]["communes"]["dsr"]
    assert(amendement_dsr["eligibles"] == base_to_amendement["toujoursEligibles"] + base_to_amendement["nouvellementEligibles"])
    assert(base_dsr["eligibles"] == amendement_dsr["eligibles"] - base_to_amendement["nouvellementEligibles"] + base_to_amendement["plusEligibles"])

    # Montants : cohérence : les strates ont une dotation non nulle si et seulement si elles sont éligibles
    for scenario_strates in [base_dsr["strates"], amendement_dsr["strates"]]:
        for strate in scenario_strates:
            assert((strate["dotationMoyenneParHab"] > 0) == (strate["proportionEligibles"] > 0))


def test_dsr_reform_cas_types(response_dotations, codes_communes_examples):
    result = response_dotations
    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]

    # même nombre de cas types en loi actuelle et amendement
    # Les cas_types sont ceux attendus
    assert (codes_communes_examples
            == [cas_type["code"] for cas_type in base_dsr["communes"]]
            == [cas_type["code"] for cas_type in amendement_dsr["communes"]]
            )

    # Vérification des clefs du dictionnaire contenues dans un array :
    # cas-types
    expected_cas_type_keys = set(["code", "eligible", "dotationParHab", "dureeAvantTerme", "dotationParHabAnneeSuivante"])
    for cas_type in base_dsr["communes"] + amendement_dsr["communes"]:
        assert set(cas_type.keys()) == expected_cas_type_keys

    # Les deux cas types ont une éligibilité différente avec la loi actuelle (sinon on s'ennuye)
    assert (len(set([cas_type["eligible"] for cas_type in base_dsr["communes"]])) > 1)

    # Montants : cohérence : les cas_types ont une dotation non nulle si et seulement si elles sont éligibles
    for scenario_cas_types in [base_dsr["communes"], amendement_dsr["communes"]]:
        for cas_type in scenario_cas_types:
            assert((cas_type["dotationParHab"] > 0) == cas_type["eligible"])


def test_dsr_reform_strates(response_dotations):
    result = response_dotations
    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]

    assert (len(BORNES_STRATES_DEFAULT) - 1) == len(base_dsr["strates"]) == len(amendement_dsr["strates"])
    assert (BORNES_STRATES_DEFAULT[:-1]
            == [description_strate["habitants"] for description_strate in base_dsr["strates"]]
            == [description_strate["habitants"] for description_strate in amendement_dsr["strates"]]
            )
    # Vérification des clefs du dictionnaire contenues dans un array :
    # strates
    expected_strates_keys = set(["proportionEligibles", "habitants", "partPopTotale", "potentielFinancierMoyenParHabitant", "dotationMoyenneParHab", "partDotationTotale"])
    for strate in base_dsr["strates"] + amendement_dsr["strates"]:
        assert set(strate.keys()) == expected_strates_keys

    # Vérification des valeurs connues :
    # part des populations des strates
    expected_strates_part_pop = [0.060324, 0.16357, 0.14816, 0.12193, 0.112542, 0.15472, 0.087568, 0.151159]
    expected_strates_potentiel_financier = [761.7836834665056, 822.7860597827515, 962.3235824743155, 1061.3211556705785, 1142.238354342724, 1212.5592073916914, 1322.0061701137156, 1450.696890744485]  # d'après critères de répartition 2019 loadés
    allowed_error = 0.0001
    for resultat_strates in [base_dsr["strates"], amendement_dsr["strates"]]:
        assert(_distance_listes(expected_strates_part_pop, [strate["partPopTotale"] for strate in resultat_strates]) < allowed_error)
        assert(_distance_listes(expected_strates_potentiel_financier, [strate["potentielFinancierMoyenParHabitant"] for strate in resultat_strates]) < allowed_error)


def test_dsu_reform_strates(response_dotations):
    result = response_dotations
    base_dsu = result["base"]["communes"]["dsu"]
    amendement_dsu = result["amendement"]["communes"]["dsu"]

    assert (len(BORNES_STRATES_DEFAULT) - 1) == len(base_dsu["strates"]) == len(amendement_dsu["strates"])
    assert (BORNES_STRATES_DEFAULT[:-1]
            == [description_strate["habitants"] for description_strate in base_dsu["strates"]]
            == [description_strate["habitants"] for description_strate in amendement_dsu["strates"]]
            )
    # Vérification des clefs du dictionnaire contenues dans un array :
    # strates
    expected_strates_keys = set(["proportionEligibles", "habitants", "partPopTotale", "potentielFinancierMoyenParHabitant", "dotationMoyenneParHab", "partDotationTotale"])
    for strate in base_dsu["strates"] + amendement_dsu["strates"]:
        assert set(strate.keys()) == expected_strates_keys

    # Vérification des valeurs connues :
    # part des populations des strates
    expected_strates_part_pop = [0.060324, 0.16357, 0.14816, 0.12193, 0.112542, 0.15472, 0.087568, 0.151159]
    expected_strates_potentiel_financier = [761.7836834665056, 822.7860597827515, 962.3235824743155, 1061.3211556705785, 1142.238354342724, 1212.5592073916914, 1322.0061701137156, 1450.696890744485]  # d'après critères de répartition 2019 loadés
    allowed_error = 0.0001
    for resultat_strates in [base_dsu["strates"], amendement_dsu["strates"]]:
        assert(_distance_listes(expected_strates_part_pop, [strate["partPopTotale"] for strate in resultat_strates]) < allowed_error)
        assert(_distance_listes(expected_strates_potentiel_financier, [strate["potentielFinancierMoyenParHabitant"] for strate in resultat_strates]) < allowed_error)


def test_dsr_dsu_reform_eligibles(response_dotations):
    result = response_dotations
    base_dsr = result["base"]["communes"]["dsr"]
    amendement_dsr = result["amendement"]["communes"]["dsr"]
    # Verifie que le nombre de communes éligibles à la dsr a été réduit
    # par l'amendement (qui réduit le maximum d'habitants de 10000 à 500)
    assert base_dsr["eligibles"] > amendement_dsr["eligibles"]

    base_dsu = result["base"]["communes"]["dsu"]
    amendement_dsu = result["amendement"]["communes"]["dsu"]
    # Verifie que le nombre de communes éligibles à la dsu a été accru
    # par l'amendement (qui réduit le minimum d'habitants de 5000 à 500)
    assert base_dsu["eligibles"] < amendement_dsu["eligibles"]


def test_dsu_dotation_positive(response_dotations_2):
    result = response_dotations_2
    amendement_dsu = result["amendement"]["communes"]["dsu"]
    # Verifie que le montant de DSU par habitant des strates n'est pas négatif
    for strate in amendement_dsu["strates"]:
        assert strate["dotationMoyenneParHab"] >= 0

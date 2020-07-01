import pytest  # type: ignore
import dpath  # type: ignore
import json

from functools import partial
from datetime import datetime
from http.client import CREATED


@pytest.fixture
def payload() -> dict:
    return {
        "reforme": {
            "impot_revenu": {
                "bareme": {
                    "seuils": [9964, 27519, 73779, 156244],
                    "taux": [0.12, 0.30, 0.41, 0.45],
                },
                "decote": {"seuil_celib": 1196, "seuil_couple": 1970, "taux": 50},
                "plafond_qf": {
                    "abat_dom": {
                        "taux_GuadMarReu": 0.3,
                        "plaf_GuadMarReu": 2450,
                        "taux_GuyMay": 0.4,
                        "plaf_GuyMay": 4050,
                    },
                    "mariesOuPacses": 1551,
                    "celib_enf": 3660,
                    "celib": 927,
                    "reduc_postplafond": 1547,
                    "reduc_postplafond_veuf": 1728,
                    "reduction_ss_condition_revenus": {
                        "seuil_maj_enf": 3797,
                        "seuil1": 18984,
                        "seuil2": 21036,
                        "taux": 0.20,
                    },
                },
                "abattements_rni": {
                    "personne_agee_ou_invalide": {
                        "montant_1": 1,
                        "montant_2": 2,
                        "plafond_1": 3,
                        "plafond_2": 4,
                    }
                },
            }
        },
        "deciles": False,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
    }


def test_calculate_compare_with_cas_types(client, payload, headers):
    # Vérifie qu'une simulation qui ne contient pas les cas types renvoie les mêmes résultats
    # qu'une simulation avec les cas-types par défaut
    cas_types = json.loads(client.post("metadata/description_cas_types").data)
    response = partial(client.post, "calculate/compare", headers=headers)
    payload_full = dict({**payload, "description_cas_types": cas_types})

    actual = json.loads(response(data=json.dumps(payload)).data)
    expected = json.loads(response(data=json.dumps(payload_full)).data)

    assert actual.keys() == expected.keys()

    assert actual["res_brut"] == expected["res_brut"]
    assert actual["total"] == expected["total"]
    assert actual["timestamp"] == expected["timestamp"]


def test_calculate_compare_presence_cas_types(client, payload, headers):
    # Vérifie que les cas types des résultats apparaissent tous dans tous les champs
    response = partial(client.post, "calculate/compare", headers=headers)
    actual = json.loads(response(data=json.dumps(payload)).data)
    first_simulation_cas_type_ids = None
    for simulation_name in actual["res_brut"].keys():
        if first_simulation_cas_type_ids is None:
            first_simulation_cas_type_ids = set(actual["res_brut"][simulation_name].keys())
        assert first_simulation_cas_type_ids == set(
            actual["res_brut"][simulation_name].keys()
        )


def test_calculate_compare_success(client, headers):
    payload2 = {
        "reforme": {
            "impot_revenu": {
                "bareme": {
                    "seuils": [10064, 25659, 73369, 157806],
                    "taux": [0.11, 0.3, 0.41, 0.45],
                },
                "decote": {"seuil_celib": 777, "seuil_couple": 1286, "taux": 0.4525},
                "plafond_qf": {
                    "abat_dom": {
                        "plaf_GuadMarReu": 2450,
                        "plaf_GuyMay": 4050,
                        "taux_GuadMarReu": 0.3,
                        "taux_GuyMay": 0.4,
                    },
                    "celib": 936,
                    "celib_enf": 3697,
                    "mariesOuPacses": 1567,
                    "reduc_postplafond": 1562,
                    "reduc_postplafond_veuf": 1745,
                    "reduction_ss_condition_revenus": {
                        "seuil1": 18984,
                        "seuil2": 21036,
                        "seuil_maj_enf": 3797,
                        "taux": 0,
                    },
                },
                "calculNombreParts": {
                    "partsSelonNombrePAC": [
                        {
                            "veuf": 1,
                            "mariesOuPacses": 2,
                            "celibataire": 1,
                            "divorce": 1,
                        },
                        {
                            "veuf": 2.5,
                            "mariesOuPacses": 2.5,
                            "celibataire": 1.5,
                            "divorce": 1.5,
                        },
                        {
                            "veuf": 3,
                            "mariesOuPacses": 3,
                            "celibataire": 2,
                            "divorce": 2,
                        },
                        {
                            "veuf": 4,
                            "mariesOuPacses": 4,
                            "celibataire": 3,
                            "divorce": 3,
                        },
                        {
                            "veuf": 5,
                            "mariesOuPacses": 5,
                            "celibataire": 4,
                            "divorce": 4,
                        },
                        {
                            "veuf": 6,
                            "mariesOuPacses": 6,
                            "celibataire": 5,
                            "divorce": 5,
                        },
                        {
                            "veuf": 7,
                            "mariesOuPacses": 7,
                            "celibataire": 6,
                            "divorce": 6,
                        },
                    ],
                    "partsParPACAuDela": 1,  # LE "Et ainsi de suite..."
                    "partsParPACChargePartagee": {  # On a maintenant 12 cas différents en fonction du nobre d'enfants.
                        "zeroChargePrincipale": {"deuxPremiers": 0.25, "suivants": 0.5},
                        "unChargePrincipale": {"premier": 0.25, "suivants": 0.5},
                        "deuxOuPlusChargePrincipale": {"suivants": 0.5},
                    },
                    "bonusParentIsole": {
                        "auMoinsUnChargePrincipale": 0.5,
                        "zeroChargePrincipaleUnPartage": 0.25,
                        "zeroChargeprincipaleDeuxOuPlusPartage": 0.5,
                    },
                },
            }
        }
    }
    # Vérifie que les cas types des résultats apparaissent tous dans tous les champs
    response_function = partial(client.post, "calculate/compare", headers=headers)
    response = response_function(data=json.dumps(payload2))
    assert response.status_code == 201


def test_calculate_compare_lexception(client, headers):
    requete = {
        "reforme": {
            "impot_revenu": {
                "bareme": {
                    "seuils": [10064, 25659, 73369, 157806],
                    "taux": [0.11, 0.3, 0.41, 0.45],
                },
                "decote": {"seuil_celib": 777, "seuil_couple": 1286, "taux": 0.4525},
                "plafond_qf": {
                    "abat_dom": {
                        "plaf_GuadMarReu": 2450,
                        "plaf_GuyMay": 4050,
                        "taux_GuadMarReu": 0.3,
                        "taux_GuyMay": 0.4,
                    },
                    "celib": 936,
                    "celib_enf": 3697,
                    "mariesOuPacses": 1567,
                    "reduc_postplafond": 1562,
                    "reduc_postplafond_veuf": 1745,
                    "reduction_ss_condition_revenus": {
                        "seuil1": 18984,
                        "seuil2": 21036,
                        "seuil_maj_enf": 3797,
                        "taux": 0,
                    },
                },
                "calculNombreParts": {"nimportequoi": "salut"},
            }
        }
    }
    response_function = partial(client.post, "calculate/compare", headers=headers)
    response = response_function(data=json.dumps(requete))
    assert response.status_code == 400
    assert json.loads(response.data) == {
        "Error": "Error in request : the field 'partsSelonNombrePAC' is missing from 'calculNombreParts'. You can refer to the README to check valid format."
    }


def test_calculate_compare_response(client, headers, payload):
    # Par défaut, la réponse contient l'impôt et le nombre de parts par cas type
    request_data = json.dumps(payload)
    response = client.post("calculate/compare", data=request_data, headers=headers)

    assert response.status_code == CREATED  # 201
    response_json = json.loads(response.data.decode('utf-8'))

    res_brut = dpath.get(response_json, 'res_brut')
    assert res_brut is not None
    assert list(res_brut.keys()) == ['apres', 'avant']

    res_brut_apres = dpath.get(response_json, 'res_brut/apres')
    assert list(res_brut_apres.keys()) == ['0', '1', '2', '3', '4', '5']  # 6 cas types par défaut

    nbreParts = dpath.get(response_json, 'nbreParts')
    assert nbreParts is not None
    assert list(nbreParts.keys()) == ['apres', 'avant']

    nbreParts_apres = dpath.get(response_json, 'nbreParts/apres')
    assert list(nbreParts_apres.keys()) == ['0', '1', '2', '3', '4', '5']  # 6 cas types par défaut


def test_calculate_compare_response_on_nbptr(client, headers, payload):
    request_data = json.dumps(payload)
    response = client.post("calculate/compare", data=request_data, headers=headers)

    assert response.status_code == CREATED  # 201

    response_json = json.loads(response.data.decode('utf-8'))
    nombre_parts_cas_types_2020 = {"0": 1.0, "1": 1.5, "2": 2.0, "3": 2.0, "4": 3.0, "5": 3.0}
    assert dpath.get(response_json, 'nbreParts/avant') == nombre_parts_cas_types_2020

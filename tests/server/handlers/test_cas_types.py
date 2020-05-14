from functools import partial
import json
from datetime import datetime
import pytest  # type: ignore


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
                    "maries_ou_pacses": 1551,
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


def test_calculate_compare_weights(client, payload, headers):
    # Vérifie que les cas types des résultats apparaissent tous dans tous les champs
    response = partial(client.post, "calculate/compare", headers=headers)
    actual = json.loads(response(data=json.dumps(payload)).data)

    for var_in_res_brut in actual["res_brut"].keys():
        assert set(actual["res_brut"]["wprm"].keys()) == set(
            actual["res_brut"][var_in_res_brut].keys()
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
                    "maries_ou_pacses": 1567,
                    "reduc_postplafond": 1562,
                    "reduc_postplafond_veuf": 1745,
                    "reduction_ss_condition_revenus": {
                        "seuil1": 18984,
                        "seuil2": 21036,
                        "seuil_maj_enf": 3797,
                        "taux": 0,
                    },
                },
                "calcul_nombre_parts": {
                    "parts_selon_nombre_personnes_a_charge": [
                        {"veuf": 1, "maries_ou_pacses": 2, "celibataire": 1, "divorce": 1},
                        {"veuf": 2.5, "maries_ou_pacses": 2.5, "celibataire": 1.5, "divorce": 1.5},
                        {"veuf": 3, "maries_ou_pacses": 3, "celibataire": 2, "divorce": 2},
                        {"veuf": 4, "maries_ou_pacses": 4, "celibataire": 3, "divorce": 3},
                        {"veuf": 5, "maries_ou_pacses": 5, "celibataire": 4, "divorce": 4},
                        {"veuf": 6, "maries_ou_pacses": 6, "celibataire": 5, "divorce": 5},
                        {"veuf": 7, "maries_ou_pacses": 7, "celibataire": 6, "divorce": 6},
                    ],
                    "parts_par_pac_au_dela": 1,  # LE "Et ainsi de suite..."
                    "nombre_de_parts_charge_partagee": {  # On a maintenant 12 cas différents en fonction du nobre d'enfants.
                        "zero_charge_principale": {
                            "deux_premiers": 0.25,
                            "suivants": 0.5,
                        },
                        "un_charge_principale": {"premier": 0.25, "suivants": 0.5},
                        "deux_ou_plus_charge_principale": {"suivants": 0.5},
                    },
                    "bonus_parent_isole": {
                        "au_moins_un_charge_principale": 0.5,
                        "zero_principal_un_partage": 0.25,
                        "zero_principal_deux_ou_plus_partages": 0.5,
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
                    "maries_ou_pacses": 1567,
                    "reduc_postplafond": 1562,
                    "reduc_postplafond_veuf": 1745,
                    "reduction_ss_condition_revenus": {
                        "seuil1": 18984,
                        "seuil2": 21036,
                        "seuil_maj_enf": 3797,
                        "taux": 0,
                    },
                },
                "calcul_nombre_parts": {"nimportequoi": "salut"},
            }
        }
    }
    response_function = partial(client.post, "calculate/compare", headers=headers)
    response = response_function(data=json.dumps(requete))
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "Error": "Threw an Exception : the field 'parts_selon_nombre_personnes_a_charge' is missing from 'calcul_nombre_parts'. You can refer to the README to check valid format."
    }

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

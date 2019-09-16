from datetime import datetime
from functools import partial
from http.client import OK, BAD_REQUEST

from dotenv import load_dotenv
from os import getenv

import pytest  # type: ignore
import dpath
import json


load_dotenv(dotenv_path=".env")
TEST_TOKEN = getenv("TEST_TOKEN")

reform_payload = {
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

reform_payload_empty_token = dict(reform_payload, token='')
reform_payload_with_token = dict(reform_payload, token=TEST_TOKEN)

# /calculate/simpop_async
# server.handlers.SimulationRunner.simuledeciles_async

# /calculate/get_async_result
# server.handlers.SimulationRunner.get_async_results

# si client envoie une requête, il récupère son id
# si client demande une réponse à requête d'id X, il obtient la réponse à X
# si client demande plusieurs requêtes, il obtient la réponse correspondant à l'id de la requête
# quand la réponse a été transmise au client, le thread de calcul est tué


def post_request(client, endpoint, headers):
    partial_response = partial(client.post, endpoint, headers=headers)
    return partial_response


def check_response(actual_result, expected_status_code, content_path_to_check, content_to_check):
    if 'status' in actual_result:
        assert actual_result['status'] == expected_status_code
    
    if content_path_to_check:
        content = dpath.util.get(actual_result, content_path_to_check)
        if content_to_check:
            assert content_to_check in content


@pytest.mark.parametrize("payload, expected_status_code, content_path_to_check, content_to_check", [
    (None, BAD_REQUEST, 'detail', 'Request body is not valid JSON'),
    (reform_payload, OK, 'Error', 'missing token: necessary for this request'),  # Token signature was invalid
    (reform_payload_empty_token, BAD_REQUEST, 'Error', 'Token invalid : not Decodable'),
    (reform_payload_with_token, OK, 'id_requete', None)
    ])
def test_calculate_simpop_async(client, payload, headers, expected_status_code, content_path_to_check, content_to_check):
    partial_response = post_request(client, "calculate/simpop_async", headers)
    actual_result = json.loads(partial_response(data=json.dumps(payload)).data)
    
    check_response(actual_result, expected_status_code, content_path_to_check, content_to_check)

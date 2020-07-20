from http.client import OK, BAD_REQUEST

from dotations.impact import build_response_dsr  # type: ignore
from Simulation_engine.simulate_dotations import simulate

# Checks whether all dictionnaries in the model exist in the target dict.
# Returns True or False, and the problematic field


def request_error_from_error_message(error_message):
    return {"Error" : error_message}, BAD_REQUEST


def check_keys_dict(dict_to_check, model):
    for k, v in model.items():
        if k not in dict_to_check:  # key does not exist
            return False, k
        if isinstance(v, dict):
            if not isinstance(dict_to_check[k], dict):  # should be a dict but is not
                return False, k
            res_child, node_err = check_keys_dict(dict_to_check[k], v)
            if not res_child:
                return False, ".".join([k, node_err])

    return True, "All required keys are in the checked dictionary"


def check_request_body(request_body):
    required_dict = {"reforme": {"dotations": {"montants": {"dgf": None}, "communes": None}}, "descriptionCasTypes": None}
    result, errorfield = check_keys_dict(request_body, required_dict)
    if not result:
        return request_error_from_error_message("Missing required '{}' field in request body.".format(errorfield))


class Dotations(object):

    def simule_dotations(**params: dict) -> tuple:
        request_body = params["body"]

        # vérifier le format de la requête
        check_result = check_request_body(request_body)
        if check_result is not None:
            return check_result

        # calculer
        prefix_dsr_eligible = "dsr_eligible_"
        prefix_dsr_montant = "dsr_montant_"
        df_results = simulate(request_body, prefix_dsr_eligible, prefix_dsr_montant)

        # constuire la réponse
        simulation_result = {
            "amendement": {
                "dotations": {
                    "communes": {
                        "dsr": build_response_dsr("amendement", df_results, prefix_dsr_eligible, prefix_dsr_montant)
                    }
                }
            },
            "base": {
                "dotations": {
                    "communes": {
                        "dsr": build_response_dsr("base", df_results, prefix_dsr_eligible, prefix_dsr_montant)
                    }
                }
            }
        }

        return simulation_result, OK

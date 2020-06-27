from Simulation_engine.simulate_dotations import simulate

# Checks whether all dictionnaries in the model exist in the target dict.
# Returns True or False, and the problematic field


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
    required_dict = {"reforme": {"dotations": {"montants": {"dgf": None}, "communes": None}}}
    result, errorfield = check_keys_dict(request_body, required_dict)
    if not result:
        return {"Error": "Missing required '{}' field in request body.".format(errorfield)}, 400


class Dotations(object):

    def simule_dotations(**params: dict) -> tuple:
        request_body = params["body"]

        # vérifier le format
        check_result = check_request_body(request_body)
        if check_result is not None:
            return check_result

        # calculer
        simulation_result = simulate(request_body)

        # constuire la réponse
        return simulation_result, 200

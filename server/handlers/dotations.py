from Simulation_engine.simulate_dotations import simulate

class Dotations(object):

    def simule_dotations(**params: dict) -> tuple:
        request_body = params["body"]

        # vérifier le format
        if "dotations" not in request_body:
            return {"Error": "Missing 'dotations' field in request body."}, 400

        # calculer
        simulation_result = simulate(request_body)

        # constuire la réponse
        return simulation_result, 200

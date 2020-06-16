class Dotations(object):

    def home(**params: dict) -> tuple:
        request_body = params["body"]

        # vérifier le format
        if "dotations" not in request_body:
            return {"Error": "Missing 'dotations' field in request body."}, 400

        # calculer

        # constuire la réponse
        return {"hello": "coucou"}, 200

from http.client import OK, BAD_REQUEST
from dotations.search import search  # type: ignore


class SearchCommune(object):
    def recherche_commune(**params: dict) -> tuple:
        request_body = params["body"]
        if "extraitNomCommune" not in request_body:
            return {"Error" : "Missing parameter extraitNomCommune"}, BAD_REQUEST
        extraitNomCommune = request_body["extraitNomCommune"]
        if extraitNomCommune == "":
            return {"Error" : "parameter extraitNomCommune cannot be empty"}, BAD_REQUEST
        return search(extraitNomCommune), OK

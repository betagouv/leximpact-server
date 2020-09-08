from http.client import OK, BAD_REQUEST
from dotations.search import search_commune_by_name  # type: ignore


class SearchCommune(object):

    def search_commune(**params: dict) -> tuple:
        commune = params['commune']
        if commune == "":
            return {"Error" : "query parameter '?commune=' cannot be empty"}, BAD_REQUEST
        return search_commune_by_name(commune), OK

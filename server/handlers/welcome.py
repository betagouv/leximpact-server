class Welcome(object):
    def home(**params: dict) -> tuple:
        return {"hello": "coucou"}, 200

from openfisca_core import periods
from openfisca_core.reforms import Reform  # type: ignore
from openfisca_core.parameters import ParameterNode  # type: ignore
from functools import reduce

# Retourne un dictionnaire flattened à partir d'un nested dictionnaire
def flattened_dict(dict_to_traverse, prechain="", delimiter="."):
    res = {}
    pc = [prechain] if len(prechain) else []
    for k, v in dict_to_traverse.items():
        if isinstance(v, dict):
            res = {**res, **flattened_dict(v, prechain=delimiter.join(pc + [k]))}
        else:
            res[delimiter.join(pc + [k])] = v
    return res


def test_flattened_dict():
    a = {"a": {"b": {"c": 3, "d": {"e": 4, "f": "chaton"}}}}
    b = {"a.b.c": 3, "a.b.d.e": 4, "a.b.d.f": "chaton"}
    assert(flattened_dict(a) == b)


class DotationReform(Reform):

    def __init__(self, tbs, payload: dict) -> None:
        self.payload = payload.get("dgf", {})
        self.period = periods.period("year:1900:200")
        super().__init__(tbs)

    def modifier(self, parameters: ParameterNode) -> ParameterNode:
        # passe en revue tous les champs du dictionnaire de réforme de payload.
        # Ceux qui ne sont pas des dictionnaires seront mis à ce niveau dans ofdl
        flatpayload = flattened_dict(self.payload)
        for field_to_update, value in flatpayload.items():
            reduce(getattr, field_to_update.split("."), parameters).update(period=self.period, value=value)
        # Quand des champs complexes entreront en compte, un traitement ad hoc sera nécessaire pour ces champs
        # et pour éviter qu'ils passent dans la moulinette ci-dessus

        return parameters

    def apply(self) -> None:
        self.modify_parameters(modifier_function=self.modifier)


if __name__ == "__main__":
    test_flattened_dict()

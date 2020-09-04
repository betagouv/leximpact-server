from openfisca_core import periods  # type: ignore
from openfisca_core.reforms import Reform  # type: ignore
from openfisca_core.parameters import ParameterNode, Bracket  # type: ignore
from functools import reduce

from utils.utils_dict import flattened_dict  # type: ignore


def set_brackets(brackets, target):
    # target est un array donné sous la forme [{"threshold": threshold[0], "amount": amount[0]), ... , {"threshold": threshold[-1], "amount": amount[-1]}]
    while brackets:
        del brackets[0]
    for params_bracket in target:
        new_bracket = Bracket(
            data={
                key: {'1900-01-01': {'value': value}} for key, value in params_bracket.items()
            },
        )
        brackets.append(new_bracket)


class DotationReform(Reform):

    def __init__(self, tbs, payload: dict, period: str) -> None:
        self.payload = payload.get("dgf", {})
        self.period = periods.period("year:{}:200".format(period))  # les réformes sont toujours sur 200 ans, mais
        # commencent à la période choisie
        super().__init__(tbs)

    def modifier(self, parameters: ParameterNode) -> ParameterNode:
        # passe en revue tous les champs du dictionnaire de réforme de payload.
        # Ceux qui ne sont pas des dictionnaires seront mis à ce niveau dans ofdl
        flatpayload = flattened_dict(self.payload)

        # Quand des champs complexes entrent en compte, un traitement ad hoc est nécessaire pour ces champs
        # pour éviter qu'ils passent dans la moulinette d'en bas.
        # Schéma pour les variables qui ne correspondent pas à un chemin OFDL
        # par exemple les brackets ou les variables où des calculs sont nécessaires :
        # Une fonction ad hoc de modification des paramètres est créée et la clef est retirée pour éviter
        # de soulever une erreur à l'étape suivante
        if "population.plafond_dgf" in flatpayload:
            set_brackets(parameters.population.plafond_dgf.brackets, flatpayload["population.plafond_dgf"])
            del flatpayload["population.plafond_dgf"]

        # Variables correspondant à un chemin OFDL : Tous les éléments de la réforme qui n'ont
        # pas été retirés précédemment  vont être directement fixés à un niveau dans les parametres
        # Ca raisera les mêmes erreurs que parameters.mon.chemin.qui.nexiste.pas.update(valeur) si le
        # chemin n'existe pas

        for field_to_update, value in flatpayload.items():
            reduce(getattr, field_to_update.split("."), parameters).update(period=self.period, value=value)

        return parameters

    def apply(self) -> None:
        self.modify_parameters(modifier_function=self.modifier)

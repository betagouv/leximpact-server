from typing import Callable, NamedTuple, TypeVar

from toolz.functoolz import compose  # type: ignore

from openfisca_core.parameters import ParameterNode  # type: ignore
from openfisca_core import periods  # type: ignore

T = TypeVar("T", bound="ParametricReform")


class ParametricReform(NamedTuple):
    """Une réforme fiscale"""

    parameters: ParameterNode
    payload: dict
    instant: periods.Instant
    period: periods.Period

    def __call__(self: T, function: Callable[[T], T]) -> T:
        return function(self)


def reforms(payload: dict) -> tuple:
    mapping = {
        "decote": decote,
        "bareme": bareme,
        "abattements_rni": abattements_rni,
        "plafond_qf": compose(plafond_qf, abat_dom, reduction_ss_condition_revenus),
    }

    return tuple(mapping[reform] for reform in tuple(payload) if reform in mapping)


def update(items, keys, node, period):
    for (key, value) in items:
        if key in keys:
            parameter = getattr(node, key)
            parameter.update(period=period, value=float(value))


def bareme(reform: T) -> T:
    seuils = reform.payload.get("bareme", {}).get("seuils")
    taux = reform.payload.get("bareme", {}).get("taux")
    node = reform.parameters.impot_revenu.bareme.brackets

    if seuils:
        for i in range(len(seuils)):
            node[i].threshold.update(period=reform.period, value=seuils[i])

        for i in range(len(seuils), len(node) - 1):
            node[i].threshold.update(period=reform.period, value=seuils[-1] + i)

    if taux:
        for i in range(len(taux)):
            node[i].rate.update(period=reform.period, value=taux[i] * 0.01)

        for i in range(len(taux), len(node) - 1):
            node[i].rate.update(period=reform.period, value=taux[-1] * 0.01)

    return type(reform)(*reform)


def decote(reform: T) -> T:
    seuil_couple = reform.payload.get("decote", {}).get("seuil_couple")
    seuil_celib = reform.payload.get("decote", {}).get("seuil_celib")
    taux = reform.payload.get("decote", {}).get("taux")
    node = reform.parameters.impot_revenu.decote

    if seuil_couple:
        node.seuil_couple.update(period=reform.period, value=float(seuil_couple))

    if seuil_celib:
        node.seuil_celib.update(period=reform.period, value=float(seuil_celib))

    if taux:
        node.seuil_celib.update(period=reform.period, value=float(taux))

    return type(reform)(*reform)


def abattements_rni(reform: T) -> T:
    abattements_rni = reform.payload.get("abattements_rni", {})
    payload = abattements_rni.get("personne_agee_ou_invalide", {})
    node = reform.parameters.impot_revenu.abattements_rni.personne_agee_ou_invalide
    keys = ["montant_1", "montant_2", "plafond_1", "plafond_2"]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)


def plafond_qf(reform: T) -> T:
    payload = reform.payload.get("plafond_qf", {})
    node = reform.parameters.impot_revenu.plafond_qf
    keys = [
        "maries_ou_pacses",
        "celib_enf",
        "celib",
        "reduc_postplafond",
        "reduc_postplafond_veuf",
    ]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)


def abat_dom(reform: T) -> T:
    plafond_qf = reform.payload.get("plafond_qf", {})
    payload = plafond_qf.get("abat_dom", {})
    node = reform.parameters.impot_revenu.plafond_qf.abat_dom
    keys = ["taux_GuadMarReu", "plaf_GuadMarReu", "taux_GuyMay", "plaf_GuyMay"]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)


def reduction_ss_condition_revenus(reform: T) -> T:
    plafond_qf = reform.payload.get("plafond_qf", {})
    payload = plafond_qf.get("reduction_ss_condition_revenus", {})
    node = reform.parameters.impot_revenu.plafond_qf.reduction_ss_condition_revenus
    keys = ["seuil_maj_enf", "seuil1", "seuil2", "taux"]
    update(payload.items(), keys, node, reform.period)
    return type(reform)(*reform)

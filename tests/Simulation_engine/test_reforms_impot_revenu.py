# -*- coding: utf-8 -*-

from functools import lru_cache

from pytest import fixture  # type: ignore

from openfisca_core import periods  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore

from Simulation_engine.simulate_pop_from_reform import (
    dataframe_from_cas_types_description,
    simulation
)

from Simulation_engine.reforms import (  # type: ignore
    IncomeTaxReform,
    ParametricReform,
    bareme,
    decote,
    abattements_rni,
    plafond_qf,
    abat_dom,
    reduction_ss_condition_revenus,
)

TBS = lru_cache()(FranceTaxBenefitSystem)


@fixture
def parameters():
    return TBS().parameters


@fixture
def instant():
    return periods.instant("2018")


@fixture
def period():
    # On s'assure que la réforme sera valide jusqu'en 2100.
    return periods.period("year:1900:200")


def test_bareme_taux(parameters, instant, period, mocker):
    taux = 0.1
    payload = {"bareme": {"taux": [taux]}}
    node = parameters.impot_revenu.bareme.brackets[0].rate

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(bareme)
        node.update.assert_called_once_with(period=period, value=taux)


def test_bareme_seuil(parameters, instant, period, mocker):
    seuil = 10000
    payload = {"bareme": {"seuils": [seuil]}}
    node = parameters.impot_revenu.bareme.brackets[0].threshold

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(bareme)
        node.update.assert_called_once_with(period=period, value=seuil)


def test_decote_seuil_couple(parameters, instant, period, mocker):
    seuil_couple = 10000
    payload = {"decote": {"seuil_couple": seuil_couple}}
    node = parameters.impot_revenu.decote.seuil_couple

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(decote)
        node.update.assert_called_once_with(period=period, value=seuil_couple)


def test_decote_seuil_celib(parameters, instant, period, mocker):
    seuil_celib = 10000
    payload = {"decote": {"seuil_celib": seuil_celib}}
    node = parameters.impot_revenu.decote.seuil_celib

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(decote)
        node.update.assert_called_once_with(period=period, value=seuil_celib)


def test_abattement_rni(parameters, instant, period, mocker):
    montant_1 = 10000
    payload = {
        "abattements_rni": {"personne_agee_ou_invalide": {"montant_1": montant_1}}
    }
    node = parameters.impot_revenu.abattements_rni.personne_agee_ou_invalide.montant_1

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(abattements_rni)
        node.update.assert_called_once_with(period=period, value=montant_1)


def test_plafond_qf(parameters, instant, period, mocker):
    maries_ou_pacses = 10000
    payload = {"plafond_qf": {"maries_ou_pacses": maries_ou_pacses}}
    node = parameters.impot_revenu.plafond_qf.maries_ou_pacses

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(plafond_qf)
        node.update.assert_called_once_with(period=period, value=maries_ou_pacses)


def test_abat_dom(parameters, instant, period, mocker):
    taux_GuadMarReu = 10000
    payload = {"plafond_qf": {"abat_dom": {"taux_GuadMarReu": taux_GuadMarReu}}}
    node = parameters.impot_revenu.plafond_qf.abat_dom.taux_GuadMarReu

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(abat_dom)
        node.update.assert_called_once_with(period=period, value=taux_GuadMarReu)


def test_reduction_ss_condition_revenus(parameters, instant, period, mocker):
    taux = 10000
    payload = {"plafond_qf": {"reduction_ss_condition_revenus": {"taux": taux}}}
    node = parameters.impot_revenu.plafond_qf.reduction_ss_condition_revenus.taux

    with mocker.patch.object(node, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(reduction_ss_condition_revenus)
        node.update.assert_called_once_with(period=period, value=taux)



@fixture
def reform_config_2019():
    return {
    "impot_revenu": {
        "bareme": {
            "seuils": [0, 9964, 27159, 73779, 156244],
            "taux": [0, 0.14, 0.30, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 1196, "seuil_couple": 1970, "taux": 0.75},
        "plafond_qf": {
            "abat_dom": {
                "taux_GuadMarReu": 0.3,
                "plaf_GuadMarReu": 2450,
                "taux_GuyMay": 0.4,
                "plaf_GuyMay": 4050,
            },
            "maries_ou_pacses": 1551,
            "celib_enf": 3660,
            "celib": 927,
            "reduc_postplafond": 1547,
            "reduc_postplafond_veuf": 1728,
            "reduction_ss_condition_revenus": {
                "seuil_maj_enf": 3797,
                "seuil1": 18985,
                "seuil2": 21037,
                "taux": 0.20,
            },
        },
    }
}


def test_veuf_deux_enfants(reform_config_2019):
    # données
    veuf = { 
        "nb_anciens_combattants": 0,
        "nb_decl_invalides": 0,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf":  1,
        "nb_pac_charge_partagee":  0,
        "nb_pac_invalides":  0,
        "nombre_declarants":  1,
        "nombre_declarants_retraites":  0,
        "nombre_personnes_a_charge":  2,
        "outre_mer":  0,
        "revenu":  120000,
    }
    data = dataframe_from_cas_types_description([veuf])
    period = '2020'

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(FranceTaxBenefitSystem(), reform_config_2019, period)
    built_simulation, dict_data_by_entity = simulation(period, data, tbs_reforme_impot_revenu)

    nbptr = built_simulation.calculate('nbptr', period)
    assert nbptr == [3]

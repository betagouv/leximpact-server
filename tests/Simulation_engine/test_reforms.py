# -*- coding: utf-8 -*-

from functools import lru_cache

from pytest import fixture  # type: ignore

from openfisca_core import periods  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore

from Simulation_engine.reforms import (  # type: ignore
    ParametricReform,
    bareme,
    decote,
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
    return periods.period("year:1900:200")


def test_bareme_taux(parameters, instant, period, mocker):
    taux = 10
    payload = {"bareme": {"taux": [taux]}}
    parameter = parameters.impot_revenu.bareme.brackets[0].rate

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(bareme)
        parameter.update.assert_called_once_with(period=period, value=taux * 0.01)


def test_bareme_seuil(parameters, instant, period, mocker):
    seuil = 10000
    payload = {"bareme": {"seuils": [seuil]}}
    parameter = parameters.impot_revenu.bareme.brackets[0].threshold

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(bareme)
        parameter.update.assert_called_once_with(period=period, value=seuil)


def test_decote_seuil_couple(parameters, instant, period, mocker):
    seuil_couple = 10000
    payload = {"decote": {"seuil_couple": seuil_couple}}
    parameter = parameters.impot_revenu.decote.seuil_couple

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(decote)
        parameter.update.assert_called_once_with(period=period, value=seuil_couple)


def test_decote_seuil_celib(parameters, instant, period, mocker):
    seuil_celib = 10000
    payload = {"decote": {"seuil_celib": seuil_celib}}
    parameter = parameters.impot_revenu.decote.seuil_celib

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(decote)
        parameter.update.assert_called_once_with(period=period, value=seuil_celib)


def test_plafond_qf(parameters, instant, period, mocker):
    maries_ou_pacses = 10000
    payload = {"plafond_qf": {"maries_ou_pacses": maries_ou_pacses}}
    parameter = parameters.impot_revenu.plafond_qf.maries_ou_pacses

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(plafond_qf)
        parameter.update.assert_called_once_with(period=period, value=maries_ou_pacses)


def test_abat_dom(parameters, instant, period, mocker):
    taux_GuadMarReu = 10000
    payload = {"plafond_qf": {"abat_dom": {"taux_GuadMarReu": taux_GuadMarReu}}}
    parameter = parameters.impot_revenu.plafond_qf.abat_dom.taux_GuadMarReu

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(abat_dom)
        parameter.update.assert_called_once_with(period=period, value=taux_GuadMarReu)


def test_reduction_ss_condition_revenus(parameters, instant, period, mocker):
    taux = 10000
    payload = {"plafond_qf": {"reduction_ss_condition_revenus": {"taux": taux}}}
    parameter = parameters.impot_revenu.plafond_qf.reduction_ss_condition_revenus.taux

    with mocker.patch.object(parameter, "update"):
        reform = ParametricReform(parameters, payload, instant, period)
        reform(reduction_ss_condition_revenus)
        parameter.update.assert_called_once_with(period=period, value=taux)

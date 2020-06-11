# -*- coding: utf-8 -*-

from functools import lru_cache

from pytest import fixture  # type: ignore

from openfisca_core import periods  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore

from Simulation_engine.simulate_pop_from_reform import (
    dataframe_from_cas_types_description,
    simulation,
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

from numpy import array_equal  # type: ignore

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
def various_cas_types():
    """
        Génère plein de cas types différents utilisés pour les tests de cohérence.
    """
    all_cas_types_to_test = []
    for situf in ["veuf", "marie", "celib", "divorce"]:
        for nbpac in range(3):
            for parentisole in (
                [0, 1] if nbpac else [0]
            ):  # Dans notre paramétrisation des cas-types, le "parent"
                # isolé de la caseT est le seul impacté, puisqu'on ne modifie que l'article 194
                # et non le 195 qui décrit les parents isolés de la caseT (i.e. plus d'enfant à charge)
                for charge_part in range(min(nbpac, 2) + 1):
                    dicobase = {
                        "nb_anciens_combattants": 0,
                        "nb_decl_invalides": 0,
                        "nb_decl_parent_isole": 0,
                        "nb_decl_veuf": 0,
                        "nb_pac_charge_partagee": 0,
                        "nb_pac_invalides": 0,
                        "nombre_declarants": 0,
                        "nombre_declarants_retraites": 0,
                        "nombre_personnes_a_charge": 0,
                        "outre_mer": 0,
                        "revenu": 120000,
                    }
                    dicobase["nombre_declarants"] = 1 if situf != "marie" else 2
                    dicobase["nombre_personnes_a_charge"] = nbpac
                    dicobase["nb_decl_parent_isole"] = parentisole
                    dicobase["nb_pac_charge_partagee"] = charge_part
                    all_cas_types_to_test += [dicobase]
    return all_cas_types_to_test


@fixture
def reform_config_base_2020():
    return {
        "impot_revenu": {
            "bareme": {
                "seuils": [0, 10064, 25659, 73369, 157806],
                "taux": [0, 0.11, 0.30, 0.41, 0.45],
            },
            "decote": {"seuil_celib": 777, "seuil_couple": 1286, "taux": 0.4525},
            "plafond_qf": {
                "abat_dom": {
                    "taux_GuadMarReu": 0.3,
                    "plaf_GuadMarReu": 2450,
                    "taux_GuyMay": 0.4,
                    "plaf_GuyMay": 4050,
                },
                "maries_ou_pacses": 1567,
                "celib_enf": 3697,
                "celib": 936,
                "reduc_postplafond": 1562,
                "reduc_postplafond_veuf": 1745,
            },
        }
    }


@fixture
def nbptr_parametres_par_defaut():
    return {
        "calculNombreParts": {
            "partsSelonNombrePAC": [
                {"veuf": 1, "mariesOuPacses": 2, "celibataire": 1, "divorce": 1},
                {
                    "veuf": 2.5,
                    "mariesOuPacses": 2.5,
                    "celibataire": 1.5,
                    "divorce": 1.5,
                },
                {"veuf": 3, "mariesOuPacses": 3, "celibataire": 2, "divorce": 2},
                {"veuf": 4, "mariesOuPacses": 4, "celibataire": 3, "divorce": 3},
                {"veuf": 5, "mariesOuPacses": 5, "celibataire": 4, "divorce": 4},
                {"veuf": 6, "mariesOuPacses": 6, "celibataire": 5, "divorce": 5},
                {"veuf": 7, "mariesOuPacses": 7, "celibataire": 6, "divorce": 6},
            ],
            "partsParPACAuDela": 1,
            "partsParPACChargePartagee": {
                "zeroChargePrincipale": {"deuxPremiers": 0.25, "suivants": 0.5},
                "unChargePrincipale": {"premier": 0.25, "suivants": 0.5},
                "deuxOuPlusChargePrincipale": {"suivants": 0.5},
            },
            "bonusParentIsole": {
                "auMoinsUnChargePrincipale": 0.5,
                "zeroChargePrincipaleUnPartage": 0.25,
                "zeroChargeprincipaleDeuxOuPlusPartage": 0.5,
            },
        }
    }


@fixture
def nbptr_zero():
    return {
        "calculNombreParts": {
            "partsSelonNombrePAC": [
                {"veuf": 0, "mariesOuPacses": 0, "celibataire": 0, "divorce": 0}
            ],
            "partsParPACAuDela": 0,
            "partsParPACChargePartagee": {
                "zeroChargePrincipale": {"deuxPremiers": 0, "suivants": 0},
                "unChargePrincipale": {"premier": 0, "suivants": 0},
                "deuxOuPlusChargePrincipale": {"suivants": 0},
            },
            "bonusParentIsole": {
                "auMoinsUnChargePrincipale": 0,
                "zeroChargePrincipaleUnPartage": 0,
                "zeroChargeprincipaleDeuxOuPlusPartage": 0,
            },
        }
    }


def test_veuf_deux_enfants(reform_config_base_2020):
    # données
    veuf = {
        "nb_anciens_combattants": 0,
        "nb_decl_invalides": 0,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 1,
        "nb_pac_charge_partagee": 0,
        "nb_pac_invalides": 0,
        "nombre_declarants": 1,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 2,
        "outre_mer": 0,
        "revenu": 120000,
    }
    data = dataframe_from_cas_types_description([veuf])
    period = "2020"

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    built_simulation, _dict_data_by_entity = simulation(
        period, data, tbs_reforme_impot_revenu
    )

    nbptr = built_simulation.calculate("nbptr", period)
    assert nbptr == [3]


def test_deux_adultes_dont_invalide_deux_enfants(reform_config_base_2020):
    # données
    foyer = {
        "nb_anciens_combattants": 0,
        "nb_decl_invalides": 1,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 0,
        "nb_pac_charge_partagee": 0,
        "nb_pac_invalides": 0,
        "nombre_declarants": 2,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 2,
        "outre_mer": 0,
        "revenu": 120000,
    }
    data = dataframe_from_cas_types_description([foyer])
    period = "2020"

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    built_simulation, _dict_data_by_entity = simulation(
        period, data, tbs_reforme_impot_revenu
    )

    nbptr = built_simulation.calculate("nbptr", period)
    assert nbptr == [3.5]


def test_deux_adultes_invalides_deux_enfants(reform_config_base_2020):
    # données
    foyer = {
        "nb_anciens_combattants": 0,
        "nb_decl_invalides": 2,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 0,
        "nb_pac_charge_partagee": 0,
        "nb_pac_invalides": 0,
        "nombre_declarants": 2,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 2,
        "outre_mer": 0,
        "revenu": 120000,
    }
    data = dataframe_from_cas_types_description([foyer])
    period = "2020"

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    built_simulation, _dict_data_by_entity = simulation(
        period, data, tbs_reforme_impot_revenu
    )

    nbptr = built_simulation.calculate("nbptr", period)
    assert nbptr == [4]


def test_deux_adultes_deux_enfants_dont_invalide(reform_config_base_2020):
    # données
    foyer = {
        "nb_anciens_combattants": 0,
        "nb_decl_invalides": 0,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 0,
        "nb_pac_charge_partagee": 0,
        "nb_pac_invalides": 1,
        "nombre_declarants": 2,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 2,
        "outre_mer": 0,
        "revenu": 120000,
    }
    data = dataframe_from_cas_types_description([foyer])
    period = "2020"

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    built_simulation, _dict_data_by_entity = simulation(
        period, data, tbs_reforme_impot_revenu
    )

    nbptr = built_simulation.calculate("nbptr", period)
    assert nbptr == [3.5]


def test_deux_adultes_deux_enfants_charge_partagee(reform_config_base_2020):
    # données
    foyer = {
        "nb_anciens_combattants": 0,
        "nb_decl_invalides": 0,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 0,
        "nb_pac_charge_partagee": 2,
        "nb_pac_invalides": 0,
        "nombre_declarants": 2,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 2,
        "outre_mer": 0,
        "revenu": 120000,
    }
    data = dataframe_from_cas_types_description([foyer])
    period = "2020"

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    built_simulation, _dict_data_by_entity = simulation(
        period, data, tbs_reforme_impot_revenu
    )

    nbptr = built_simulation.calculate("nbptr", period)
    assert nbptr == [2.5]


def test_deux_adultes_ancien_combattants_deux_enfants(reform_config_base_2020):
    # données
    foyer = {
        "nb_anciens_combattants": 2,
        "nb_decl_invalides": 0,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 0,
        "nb_pac_charge_partagee": 0,
        "nb_pac_invalides": 0,
        "nombre_declarants": 2,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 2,
        "outre_mer": 0,
        "revenu": 120000,
    }
    data = dataframe_from_cas_types_description([foyer])
    period = "2020"

    # loi française + réforme IR
    tbs_reforme_impot_revenu = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    built_simulation, _dict_data_by_entity = simulation(
        period, data, tbs_reforme_impot_revenu
    )

    nbptr = built_simulation.calculate("nbptr", period)
    assert nbptr == [3.5]


def test_homemade_nbptr_function(
    reform_config_base_2020, nbptr_parametres_par_defaut, various_cas_types
):
    # Verifie que les resultats de nbptr et irpp sont les mêmes avec la fonction par defaut
    period = "2020"
    data = dataframe_from_cas_types_description(various_cas_types)
    tbs_reforme_sans_nbptr = IncomeTaxReform(
        FranceTaxBenefitSystem(), reform_config_base_2020, period
    )
    tbs_reforme_avec_nbptr = IncomeTaxReform(
        FranceTaxBenefitSystem(),
        {
            "impot_revenu": {
                **(reform_config_base_2020["impot_revenu"]),
                **nbptr_parametres_par_defaut,
            }
        },
        period,
    )

    sim_sans_nbptr, _ = simulation(period, data, tbs_reforme_sans_nbptr)
    sim_avec_nbptr, _ = simulation(period, data, tbs_reforme_avec_nbptr)

    print("sans", sim_sans_nbptr.calculate("nbptr", period))
    print("avec", sim_avec_nbptr.calculate("nbptr", period))

    assert array_equal(
        sim_sans_nbptr.calculate("nbptr", period),
        sim_avec_nbptr.calculate("nbptr", period),
    )
    assert array_equal(
        sim_sans_nbptr.calculate("irpp", period),
        sim_avec_nbptr.calculate("irpp", period),
    )


def test_zero_nbptr(reform_config_base_2020, nbptr_zero, various_cas_types):
    # Verifie que les resultats de nbptr sont bien zero pour tout le monde si tous les param
    # sont à zéro
    period = "2020"
    data = dataframe_from_cas_types_description(various_cas_types)
    tbs_reforme_avec_nbptr = IncomeTaxReform(
        FranceTaxBenefitSystem(),
        {"impot_revenu": {**(reform_config_base_2020["impot_revenu"]), **nbptr_zero}},
        period,
    )

    sim_avec_nbptr, _ = simulation(period, data, tbs_reforme_avec_nbptr)

    resultats_nbptr = sim_avec_nbptr.calculate("nbptr", period)

    assert not resultats_nbptr.any()

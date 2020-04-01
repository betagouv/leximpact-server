from pytest import fixture  # type: ignore

import pandas  # type: ignore
from pandas.util.testing import assert_frame_equal  # type: ignore

import numpy as np  # type: ignore

from Simulation_engine.simulate_pop_from_reform import (  # type: ignore
    load_data,
    adjustment,
    adjust_total,
    adjust_deciles,
    calcule_maillage_intervalle,
    CAS_TYPE,
    compare,
    dataframe_from_cas_types_description,
    DUMMY_DATA,
    IncomeTaxReform,
    PERIOD,
    simulation,
    simulations_reformes_par_defaut_castypes,
    CompareOldNew,
    simulation_from_cas_types,
    TBS,
    TBS_DEFAULT,
)


def test_load_data_when_h5(mocker):
    with mocker.patch.object(pandas, "read_hdf"):
        filename = "data.h5"
        load_data(filename)
        pandas.read_hdf.assert_called_once()


def test_load_data_when_not_h5(mocker):
    with mocker.patch.object(pandas, "read_csv"):
        filename = "data.zip"
        load_data(filename)
        pandas.read_csv.assert_called_once()


def test_adjustment():
    empiric = 73 * 10 ** 9  # recettes état estimée 2019

    equalizing_rate = 0.9
    recettes_brutes_data = 93 * 10 ** 9  # recettes brutes obtenue via données insee
    equalizing_threshold = equalizing_rate * recettes_brutes_data

    recettes_brutes_sup_facteur = 186 * 10 ** 9  # >= 95% de recettes_brutes_data
    recettes_brutes_inf_facteur = 2  # < 95% de recettes_brutes_data

    brute_result = {
        "avant": recettes_brutes_data,
        "apres": recettes_brutes_sup_facteur,
        "plf": recettes_brutes_inf_facteur,
    }
    actual_adjustement_factors = adjustment(empiric, brute_result)

    assert actual_adjustement_factors["avant"] == empiric / brute_result["avant"]

    assert recettes_brutes_sup_facteur >= equalizing_threshold
    assert (
        actual_adjustement_factors["apres"]
        == (recettes_brutes_sup_facteur - recettes_brutes_data + empiric)
        / recettes_brutes_sup_facteur
    )

    assert recettes_brutes_inf_facteur < equalizing_threshold
    assert round(actual_adjustement_factors["plf"], 2) == 0.76


def test_adjust_total():
    factor = {"avant": 2, "apres": 2}
    total = {"avant": 2, "apres": 4}

    actual = adjust_total(factor, total)
    expected = {"avant": 4, "apres": 8}

    assert actual == expected


def test_adjust_deciles():
    factor = {"avant": 2, "apres": 2}
    decile_1 = {"poids": 1, "avant": 2, "apres": 3}

    actual = adjust_deciles(factor, [decile_1])
    expected = [{"poids": 1, "avant": factor["avant"] * decile_1["avant"], "apres": 6}]

    assert actual == expected


def test_dataframe_from_cas_types_description():
    cas_types_description = {}  # Cf. desc_cas_types()

    expected_data_columns = [
        "index",
        "activite",
        "age",
        "categorie_salarie",
        "chomage_brut",
        "chomage_imposable",
        "contrat_de_travail",
        "date_naissance",
        "effectif_entreprise",
        "idfam",
        "idfoy",
        "idmen",
        "pensions_alimentaires_percues",
        "quifam",
        "quifoy",
        "quimen",
        "rag",
        "retraite_brute",
        "ric",
        "rnc",
        "statut_marital",
        "salaire_de_base",
        "taux_csg_remplacement",
        "f4ba",
        "loyer",
        "statut_occupation_logement",
        "taxe_habitation",
        "wprm",
        "zone_apl",
        "quimenof",
        "residence_fiscale_guadeloupe",
        "residence_fiscale_guyane",
        "quifoyof",
        "quifamof",
        "caseL",
        "caseT",
        "caseW",
        "garde_alternee",
        "invalidite",
    ]
    expected_simulation_data = pandas.DataFrame(
        columns=expected_data_columns,
        index=pandas.RangeIndex(start=0, stop=0, step=1),
        dtype="float64",
    )

    simulation_data = dataframe_from_cas_types_description(cas_types_description)
    print("expected_simulation_data", expected_simulation_data)
    print("simulation_data", simulation_data)
    assert_frame_equal(simulation_data, expected_simulation_data)


def test_calcule_maillage_intervalle():
    nom_colonne = "salaire_de_base"
    min_value_colonne = 15600

    expected_data_columns = [nom_colonne]
    expected_data = np.array(
        [min_value_colonne, 17160, 18876, 20763.600, 22839.960, 25123.956],
        dtype="float64",
    )
    expected = pandas.DataFrame(
        [[x] for x in expected_data], columns=expected_data_columns
    )
    for name in ["idfam", "idfoy", "idmen"]:
        expected[name] = range(0, 6)
    for name in ["quifam", "quifoy", "quimen"]:
        expected[name] = 0

    max_value_colonne = 25405
    pourcentage_hausse = 0.1
    valeur_hausse = pourcentage_hausse * min_value_colonne
    revenus_bruts = calcule_maillage_intervalle(
        nom_colonne,
        min_value_colonne,
        max_value_colonne,
        pourcentage_hausse,
        valeur_hausse,
    )

    assert_frame_equal(revenus_bruts, expected, check_dtype=False)


dictreform = {
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


# Bon je veux :  calculer l'inverse de quelques revenu_imposable : 10000, 20000, 30000
# Check que le salaire_imposable est bien le même à l'arrivée qu'au début


def dict_cas_type_unipersonne_from_revenu(revenu_imposable):
    return {
        "nombre_declarants": 1,
        "nombre_declarants_retraites": 0,
        "nombre_personnes_a_charge": 0,
        "outre_mer": 0,
        "revenu": revenu_imposable,
        "nb_decl_parent_isole": 0,
        "nb_decl_veuf": 0,
        "nb_decl_invalides": 0,
        "nb_pac_invalides": 0,
        "nb_anciens_combattants": 0,
        "nb_pac_charge_partagee": 0,
    }


def test_inversion_variable():
    revenus_a_tester = [10000, 20000, 100000, 500000]
    for revenu in revenus_a_tester:
        _df_description, simulations = simulation_from_cas_types(
            [dict_cas_type_unipersonne_from_revenu(revenu)]
        )
        sim_base, _data_frames_base = simulations["avant"]
        revenu_post_calcul = sim_base.calculate_add("salaire_imposable", PERIOD)[0]
        assert round(revenu_post_calcul) == round(revenu)


@fixture
def reform():
    return IncomeTaxReform(TBS, dictreform, PERIOD)


@fixture
def requested_simulations():
    # list of keys that are supposed to appear in the results. should be ["avant",  "plf", "apres"]
    # or ["avant", "apres"]
    return sorted(list(TBS_DEFAULT.keys())) + ["apres"]


def test_sim_pop_dict_content(reform, requested_simulations):
    simulation_reform = simulation(PERIOD, DUMMY_DATA, reform)
    comp_result = compare(PERIOD, {"apres": simulation_reform})
    assert "total" in comp_result
    assert "deciles" in comp_result
    assert "frontieres_deciles" in comp_result
    assert len(comp_result["frontieres_deciles"]) == len(comp_result["deciles"])
    assert "foyers_fiscaux_touches" in comp_result
    # assert len(comp_result["deciles"])==10 Removed cause with the cas type description
    for key in requested_simulations:
        assert key in comp_result["total"]
        assert key in comp_result["deciles"][0]
    for index_key_1 in range(len(requested_simulations)):
        for index_key_2 in range(index_key_1 + 1, len(requested_simulations)):
            key = (
                requested_simulations[index_key_1]
                + "_to_"
                + requested_simulations[index_key_2]
            )
            # list of keys checked can be for example ["avant_to_apres", "avant_to_plf", "plf_to_apres"]
            assert key in comp_result["foyers_fiscaux_touches"]
            for type_touche, nb_people in comp_result["foyers_fiscaux_touches"][
                key
            ].items():
                assert type_touche in [
                    "gagnant",
                    "neutre",
                    "perdant",
                    "perdant_zero",
                    "neutre_zero",
                ]
                assert isinstance(nb_people, int)


def test_sim_base_cas_types_dict_content_ok(reform, requested_simulations):
    simulation_reform = simulation(PERIOD, CAS_TYPE, reform)
    simulations_cas_types = simulations_reformes_par_defaut_castypes
    simulations_cas_types["apres"] = simulation_reform
    comp_result = compare(PERIOD, simulations_cas_types, compute_deciles=False)
    assert "total" in comp_result
    assert "res_brut" in comp_result
    # assert len(comp_result["deciles"])==10 Removed cause with the cas type description
    for key in requested_simulations:
        assert key in comp_result["total"]
        assert key in comp_result["res_brut"]
        assert len(comp_result["res_brut"][key]) == 6


def test_sim_custom_cas_types_dict_content_ok(requested_simulations):
    dict_cas = [
        {
            "nombre_declarants": 1,
            "nombre_declarants_retraites": 0,
            "nombre_personnes_a_charge": 1,
            "outre_mer": 0,
            "revenu": 31200,
            "nb_decl_parent_isole": 0,
            "nb_decl_veuf": 0,
            "nb_decl_invalides": 0,
            "nb_pac_invalides": 0,
            "nb_anciens_combattants": 0,
            "nb_pac_charge_partagee": 0,
        },
        {
            "nombre_declarants": 2,
            "nombre_declarants_retraites": 0,
            "nombre_personnes_a_charge": 2,
            "outre_mer": 0,
            "revenu": 31200,
            "nb_decl_parent_isole": 0,
            "nb_decl_veuf": 0,
            "nb_decl_invalides": 0,
            "nb_pac_invalides": 0,
            "nb_anciens_combattants": 1,
            "nb_pac_charge_partagee": 0,
        },
    ]
    comp_result = CompareOldNew(
        isdecile=False, dictreform=dictreform, castypedesc=dict_cas
    )
    assert "total" in comp_result
    assert "res_brut" in comp_result
    # assert len(comp_result["deciles"])==10 Removed cause with the cas type description
    for key in requested_simulations:
        assert key in comp_result["total"]
        assert key in comp_result["res_brut"]
        assert len(comp_result["res_brut"][key]) == len(dict_cas)

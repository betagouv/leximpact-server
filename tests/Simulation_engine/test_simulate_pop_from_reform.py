import pandas  # type: ignore
from pandas.util.testing import assert_frame_equal

from Simulation_engine.simulate_pop_from_reform import (  # type: ignore
    load_data,
    adjustment,
    adjust_total,
    adjust_deciles,
    dataframe_from_cas_types_description,
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
    empiric = 4
    baseline = 2
    assert adjustment(empiric, baseline) == 2


def test_adjust_total():
    actual = adjust_total(2, {"avant": 2, "apres": 4})
    expected = {"avant": 4, "apres": 8}

    assert actual == expected


def test_adjust_deciles():
    actual = adjust_deciles(2, [{"poids": 1, "avant": 2, "apres": 3}])
    expected = [{"poids": 2, "avant": 4, "apres": 6}]

    assert actual == expected


def test_dataframe_from_cas_types_description():
    cas_types_description = {}

    expected_data_columns = ["index", "activite", "age", "categorie_salarie", "chomage_brut", "chomage_imposable", 
        "contrat_de_travail", "date_naissance", "effectif_entreprise", "heures_remunerees_volume", 
        "idfam", "idfoy", "idmen", "pensions_alimentaires_percues", "quifam", "quifoy", "quimen", "rag", 
        "retraite_brute", "ric", "rnc", "statut_marital", "salaire_de_base", "taux_csg_remplacement", 
        "f4ba", "loyer", "statut_occupation_logement", "taxe_habitation", "wprm", "zone_apl", "quimenof", 
        "residence_fiscale_guadeloupe", "residence_fiscale_guyane", "quifoyof", "quifamof", 
        "caseL", "caseT", "caseW", "garde_alternee", "invalidite"]
    expected_simulation_data = pandas.DataFrame(
        columns = expected_data_columns, 
        index = pandas.RangeIndex(start=0, stop=0, step=1),
        dtype = 'float64') 

    simulation_data = dataframe_from_cas_types_description(cas_types_description)
    print("expected_simulation_data", expected_simulation_data)
    print("simulation_data", simulation_data)
    assert_frame_equal(simulation_data, expected_simulation_data)

import pandas
from dotations.simulation import resultfromreforms


def test_resultfromreforms_default_inputs():
    reformes = None
    openfisca_variables_to_compute = (
        "dsr_eligible_fraction_bourg_centre",
        "dsr_eligible_fraction_perequation",
        "dsr_eligible_fraction_cible"
        )
    result = resultfromreforms(dict_ref=reformes, to_compute_res=openfisca_variables_to_compute)
    assert isinstance(result, pandas.DataFrame)


def test_resultfromreforms():
    openfisca_variables_to_compute = ("dsr_eligible_fraction_perequation",)
    scenario_name = "apres"
    reforme_as_openfisca = {} 

    result = resultfromreforms({scenario_name : reforme_as_openfisca}, openfisca_variables_to_compute)

    assert isinstance(result, pandas.DataFrame)
    assert "dsr_eligible_fraction_perequation_avant" in result.columns
    assert "dsr_eligible_fraction_perequation" + "_" + scenario_name in result.columns

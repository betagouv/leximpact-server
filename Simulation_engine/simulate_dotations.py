from dotations.simulation import resultfromreforms  # type: ignore
from dotations.impact import (
    format_reforme_openfisca,
    build_response_dsr_cas_types,
    build_response_dsr_eligibilites,
    build_response_dsr_strates
    )  # type: ignore


# def simulate(request_body):
#     simulation_result = impacts_reforme_dotation(format_reforme_openfisca(request_body["reforme"]))
#     return simulation_result


def build_response_dsr(scenario, df_results, prefix_dsr_eligible):
    eligibilites = build_response_dsr_eligibilites(scenario, df_results, prefix_dsr_eligible)
    return {
        "communes": build_response_dsr_cas_types(scenario, df_results, prefix_dsr_eligible),
        **eligibilites,
        "strates": build_response_dsr_strates(scenario, df_results, prefix_dsr_eligible)
    }

def simulate(request_body):
    variables_nombre_communes = [
        "dsr_eligible_fraction_bourg_centre",
        "dsr_eligible_fraction_perequation",
        "dsr_eligible_fraction_cible"
    ]
    variables_aggregations = ["potentiel_financier"]
    to_compute = variables_nombre_communes + variables_aggregations

    reforme = format_reforme_openfisca(request_body["reforme"])
    df_results: DataFrame = resultfromreforms({"amendement" : reforme}, to_compute)

    prefix_dsr_eligible = "dsr_eligible_"
    for scenario in ["base", "amendement"]:
        df_results[prefix_dsr_eligible + scenario] = (
            df_results["dsr_eligible_fraction_bourg_centre" + "_" + scenario]
            | df_results["dsr_eligible_fraction_perequation" + "_" + scenario]
            | df_results["dsr_eligible_fraction_cible" + "_" + scenario]
        )

    return {
        "amendement": {
            "dotations": {
                "communes": {
                    "dsr": build_response_dsr("amendement", df_results, prefix_dsr_eligible)
                }
            }
        },
        "base": {
            "dotations": {
                "communes": {
                    "dsr": build_response_dsr("base", df_results, prefix_dsr_eligible)
                }
            }
        }
    }

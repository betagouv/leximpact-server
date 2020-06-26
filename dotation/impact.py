from simulation import resultfromreforms


def impacts_reforme_dotation(reforme):
    variables_nombre_communes = ["dsr_eligible_fraction_bourg_centre", "dsr_eligible_fraction_perequation", "dsr_eligible_fraction_cible"]
    to_compute = variables_nombre_communes
    df_results = resultfromreforms({"apres" : reforme}, to_compute)
    res = {}
    for scenario in ["avant", "apres"]:
        res[scenario] = {}
        for col in variables_nombre_communes:
            res[scenario]["nombre_communes_" + col] = df_results[col + "_" + scenario].sum()
    return res


if __name__ == "__main__":
    reforme_example = {
        "dgf": {
            "dotation_solidarite_rurale": {
                "cible": {
                    "eligibilite": {
                        "seuil_classement": 23
                    }
                }
            }
        }
    }
    print(impacts_reforme_dotation(reforme_example))

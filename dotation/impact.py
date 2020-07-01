from simulation import resultfromreforms
from utils_dict import translate_dict


table_transcription_leximpact_ofdl = {"communes.dsr.eligibilite.popMax": "dotation_solidarite_rurale.seuil_nombre_habitants",
                                      "communes.dsr.eligibilite.popChefLieuMax": "dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_nombre_habitants_chef_lieu",
                                      "communes.dsr.bourgcentre.eligibilite.partPopCantonMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_part_population_canton",
                                      "communes.dsr.bourgcentre.eligibilite.exclusion.agglomeration.partPopDepartementMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_part_population_dgf_agglomeration_departement",
                                      "communes.dsr.bourgcentre.eligibilite.exclusion.agglomeration.popMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_agglomeration",
                                      "communes.dsr.bourgcentre.eligibilite.exclusion.agglomeration.popCommuneMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_maximum_commune_agglomeration",
                                      "communes.dsr.bourgcentre.eligibilite.exclusion.canton.popChefLieuMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_chef_lieu_de_canton",
                                      "communes.dsr.bourgcentre.eligibilite.exclusion.potentielFinancierParHab.rapportPotentielFinancierMoyenParHab": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_rapport_pfi_10000",
                                      "communes.dsr.bourgcentre.attribution.plafonnementPopulation": "population.plafond_dgf",
                                      "communes.dsr.cible.eligibilite.premieresCommunes": "dotation_solidarite_rurale.cible.eligibilite.seuil_classement",
                                      "communes.dsr.cible.eligibilite.indiceSynthetique.ponderationPotentielFinancier": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_potentiel_financier",
                                      "communes.dsr.cible.eligibilite.indiceSynthetique.ponderationRevenuParHab": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_revenu", }


def format_reforme_openfisca(reforme_a_traduire):
    return translate_dict(reforme_a_traduire, table_transcription_leximpact_ofdl)


def impacts_reforme_dotation(reforme):
    variables_nombre_communes = ["dsr_eligible_fraction_bourg_centre", "dsr_eligible_fraction_perequation", "dsr_eligible_fraction_cible"]
    variables_aggregations = ["potentiel_financier"]
    to_compute = variables_nombre_communes + variables_aggregations
    df_results = resultfromreforms({"apres" : reforme}, to_compute)
    res = {}
    scenario_names = {"avant": "base", "apres": "amendement", "plf": "plf"}

    prefix_dsr_eligible = "dsr_eligible_"
    for scenario in ["avant", "apres"]:
        df_results[prefix_dsr_eligible + scenario] = df_results["dsr_eligible_fraction_bourg_centre" + "_" + scenario] | df_results["dsr_eligible_fraction_perequation" + "_" + scenario] | df_results["dsr_eligible_fraction_cible" + "_" + scenario]

    for scenario in ["avant", "apres"]:
        scenario_api = scenario_names[scenario]
        res[scenario_api] = {
            "dotations": {
                "communes": {
                    "dsr": {

                    }
                }
            }
        }
        res[scenario_api]["dotations"]["communes"]["dsr"]["eligibles"] = df_results[prefix_dsr_eligible + scenario].sum()
        if scenario != "avant":
            res[scenario_api]["dotations"]["communes"]["dsr"]["nouvellementEligibles"] = len(df_results[(df_results[prefix_dsr_eligible + scenario]) & (~df_results[prefix_dsr_eligible + "avant"])])
            res[scenario_api]["dotations"]["communes"]["dsr"]["plusEligibles"] = len(df_results[(~df_results[prefix_dsr_eligible + scenario]) & (df_results[prefix_dsr_eligible + "avant"])])
        # tableau nombre de communes éligibles par strate
        bornes_inf = [0, 500, 2000, 5000, 10000, 20000, 50000, 100000, 1000000000000]  # bornes inf des strates en terme de POP INSEE
        resultats_agreges_bornes = [{} for borne in bornes_inf]
        for id_borne in range(len(bornes_inf)):  # id borne : the borne identity
            borne = bornes_inf[id_borne]
            df_strate = df_results[df_results["population_insee"] >= borne]
            resultats_agreges_bornes[id_borne]["population_insee"] = df_strate["population_insee"].sum()
            resultats_agreges_bornes[id_borne]["potentiel_financier"] = df_strate["potentiel_financier" + "_" + scenario].sum()
            resultats_agreges_bornes[id_borne]["eligibles_dsr"] = df_strate[prefix_dsr_eligible + scenario].sum()
        res_strates = [{} for borne in bornes_inf[:-1]]
        for id_borne in range(len(bornes_inf) - 1):
            res_strates[id_borne]["habitants"] = bornes_inf[id_borne]
            pop_strate = resultats_agreges_bornes[id_borne]["population_insee"] - resultats_agreges_bornes[id_borne + 1]["population_insee"]
            res_strates[id_borne]["partPopTotale"] = pop_strate / resultats_agreges_bornes[0]["population_insee"]
            pot_strate = resultats_agreges_bornes[id_borne]["potentiel_financier"] - resultats_agreges_bornes[id_borne + 1]["potentiel_financier"]
            res_strates[id_borne]["potentielFinancierMoyenParHabitant"] = pot_strate / pop_strate
            nb_elig_strate = resultats_agreges_bornes[id_borne]["eligibles_dsr"] - resultats_agreges_bornes[id_borne + 1]["eligibles_dsr"]
            res_strates[id_borne]["eligibles"] = nb_elig_strate
        res[scenario_api]["dotations"]["communes"]["dsr"]["strates"] = res_strates
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

    reforme_example_api = {
        "communes" : {
            "dsr" : {
                "cible": {
                    "eligibilie": {
                        "premieresCommunes": 23
                    }
                }
            }
        }
    }
    print(impacts_reforme_dotation(format_reforme_openfisca(reforme_example_api)))

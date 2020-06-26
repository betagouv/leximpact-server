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
                                      "communes.dsr.cible.eligibilite.indiceSynthetique.ponderationPotentielFinancier": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_pot_fin",
                                      "communes.dsr.cible.eligibilite.indiceSynthetique.ponderationRevenuParHab": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_revenu", }


def format_reforme_openfisca(reforme_a_traduire):
    return translate_dict(reforme_a_traduire, table_transcription_leximpact_ofdl)


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

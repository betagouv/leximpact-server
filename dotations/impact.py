from pandas import DataFrame  # type: ignore
from copy import deepcopy

from dotations.simulation import resultfromreforms  # type: ignore
from dotations.utils_dict import translate_dict  # type: ignore


BORNES_STRATES = [0, 500, 2000, 5000, 10000, 20000, 50000, 100000, 1000000000000]  # bornes inf des strates en terme de POP INSEE

table_transcription_leximpact_ofdl = {"dotations.communes.dsr.eligibilite.popMax": "dotation_solidarite_rurale.seuil_nombre_habitants",
                                      "dotations.communes.dsr.eligibilite.popChefLieuMax": "dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_nombre_habitants_chef_lieu",
                                      "dotations.communes.dsr.bourgcentre.eligibilite.partPopCantonMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_part_population_canton",
                                      "dotations.communes.dsr.bourgcentre.eligibilite.exclusion.agglomeration.partPopDepartementMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_part_population_dgf_agglomeration_departement",
                                      "dotations.communes.dsr.bourgcentre.eligibilite.exclusion.agglomeration.popMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_agglomeration",
                                      "dotations.communes.dsr.bourgcentre.eligibilite.exclusion.agglomeration.popCommuneMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_maximum_commune_agglomeration",
                                      "dotations.communes.dsr.bourgcentre.eligibilite.exclusion.canton.popChefLieuMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_chef_lieu_de_canton",
                                      "dotations.communes.dsr.bourgcentre.eligibilite.exclusion.potentielFinancierParHab.rapportPotentielFinancierMoyenParHab": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_rapport_pfi_10000",
                                      "dotations.communes.dsr.bourgCentre.attribution.plafonnementPopulation": "population.plafond_dgf",
                                      "dotations.communes.dsr.cible.eligibilite.premieresCommunes": "dotation_solidarite_rurale.cible.eligibilite.seuil_classement",
                                      "dotations.communes.dsr.cible.eligibilite.indiceSynthetique.ponderationPotentielFinancier": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_potentiel_financier",
                                      "dotations.communes.dsr.cible.eligibilite.indiceSynthetique.ponderationRevenuParHab": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_revenu", }


def format_reforme_openfisca(reforme_a_traduire):
    # passage des dictionnaires avec nombre de clefs variables au format
    # list de dictionnaire : evite de se retrouver avec des champs qui ne correspondent pas
    # à des hiérarchies de variables openfisca)
    # et qui seront consommés par les parsers ad hoc de la réforme
    ref = deepcopy(reforme_a_traduire)
    del ref["dotations"]["montants"]  # not implemented in ofdl yet
    try:
        dictionnaire_a_tableautiser = deepcopy(ref["communes"]["dsr"]["bourgCentre"]["attribution"]["plafonnementPopulation"])
        ref["communes"]["dsr"]["bourgCentre"]["attribution"]["plafonnementPopulation"] = sorted([{"threshold": seuil, "amount": plafond} for seuil, plafond in dictionnaire_a_tableautiser.items()],
                                                                                                key=lambda x: x["threshold"])
    except KeyError:
        # on choisit de ne rien soulever si ce champ n'est pas présent dans la réforme.
        # Ca fait qu'une absence de ce paramètre ne fera pas échouer la requête.
        pass
    return {"dgf": translate_dict(ref, table_transcription_leximpact_ofdl)}


def get_cas_types_codes_insee():
    return ["76384", "76214"]


def impacts_reforme_dotation(reforme):
    variables_nombre_communes = [
        "dsr_eligible_fraction_bourg_centre",
        "dsr_eligible_fraction_perequation",
        "dsr_eligible_fraction_cible"
    ]
    variables_aggregations = ["potentiel_financier"]
    to_compute = variables_nombre_communes + variables_aggregations

    df_results: DataFrame = resultfromreforms({"apres" : reforme}, to_compute)

    res = {}
    scenario_names = {"avant": "base", "apres": "amendement", "plf": "plf"}

    prefix_dsr_eligible = "dsr_eligible_"
    for scenario in ["avant", "apres"]:
        df_results[prefix_dsr_eligible + scenario] = (
            df_results["dsr_eligible_fraction_bourg_centre" + "_" + scenario]
            | df_results["dsr_eligible_fraction_perequation" + "_" + scenario]
            | df_results["dsr_eligible_fraction_cible" + "_" + scenario]
        )

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

        res[scenario_api]["dotations"]["communes"]["dsr"]["communes"] = []
        code_comm = "Informations générales - Code INSEE de la commune"
        communes_cas_types = get_cas_types_codes_insee()
        for cas_type in communes_cas_types:
            cas_type_eligible = bool(df_results[df_results[code_comm].astype(str) == cas_type][prefix_dsr_eligible + scenario].values[0])
            res[scenario_api]["dotations"]["communes"]["dsr"]["communes"] += [{"code" : cas_type, "eligible": cas_type_eligible}]
        res[scenario_api]["dotations"]["communes"]["dsr"]["eligibles"] = int(df_results[prefix_dsr_eligible + scenario].sum())
        if scenario != "avant":
            res[scenario_api]["dotations"]["communes"]["dsr"]["nouvellementEligibles"] = len(df_results[(df_results[prefix_dsr_eligible + scenario]) & (~df_results[prefix_dsr_eligible + "avant"])])
            res[scenario_api]["dotations"]["communes"]["dsr"]["plusEligibles"] = len(df_results[(~df_results[prefix_dsr_eligible + scenario]) & (df_results[prefix_dsr_eligible + "avant"])])
        # tableau nombre de communes éligibles par strate
        resultats_agreges_bornes = [{} for borne in BORNES_STRATES]

        # pour une borne, aggrège les résultats de toute la population située au niveau supérieur ou égal à la borne
        for id_borne in range(len(BORNES_STRATES)):  # id borne : the borne identity
            borne = BORNES_STRATES[id_borne]
            df_strate = df_results[df_results["population_insee"] >= borne]
            resultats_agreges_bornes[id_borne]["population_insee"] = int(df_strate["population_insee"].sum())
            resultats_agreges_bornes[id_borne]["potentiel_financier"] = float(df_strate["potentiel_financier" + "_" + scenario].sum())
            resultats_agreges_bornes[id_borne]["eligibles_dsr"] = int(df_strate[prefix_dsr_eligible + scenario].sum())
        res_strates = [{} for borne in BORNES_STRATES[:-1]]
        for id_borne in range(len(BORNES_STRATES) - 1):
            res_strates[id_borne]["habitants"] = BORNES_STRATES[id_borne]
            pop_strate = resultats_agreges_bornes[id_borne]["population_insee"] - resultats_agreges_bornes[id_borne + 1]["population_insee"]
            res_strates[id_borne]["partPopTotale"] = pop_strate / resultats_agreges_bornes[0]["population_insee"]
            pot_strate = resultats_agreges_bornes[id_borne]["potentiel_financier"] - resultats_agreges_bornes[id_borne + 1]["potentiel_financier"]
            res_strates[id_borne]["potentielFinancierMoyenParHabitant"] = pot_strate / pop_strate
            nb_elig_strate = resultats_agreges_bornes[id_borne]["eligibles_dsr"] - resultats_agreges_bornes[id_borne + 1]["eligibles_dsr"]
            res_strates[id_borne]["eligibles"] = nb_elig_strate
        res[scenario_api]["dotations"]["communes"]["dsr"]["strates"] = res_strates

    return res

from copy import deepcopy
from pandas import DataFrame  # type: ignore

from dotations.utils_dict import translate_dict  # type: ignore
from dotations.simulation import resultfromreforms  # type: ignore


TABLE_LEXIMPACT_TO_OFDL = {
    "dotations.communes.dsr.eligibilite.popMax": "dotation_solidarite_rurale.seuil_nombre_habitants",
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
    "dotations.communes.dsr.cible.eligibilite.indiceSynthetique.ponderationRevenuParHab": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_revenu"
}


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
    return {"dgf": translate_dict(ref, TABLE_LEXIMPACT_TO_OFDL)}


def simulate(request_body, prefix_dsr_eligible):
    variables_nombre_communes = [
        "dsr_eligible_fraction_bourg_centre",
        "dsr_eligible_fraction_perequation",
        "dsr_eligible_fraction_cible"
    ]
    variables_aggregations = ["potentiel_financier"]
    variables_montants = ["dsr_montant_hors_garanties_fraction_bourg_centre"]
    to_compute = variables_nombre_communes + variables_aggregations + variables_montants

    reforme = format_reforme_openfisca(request_body["reforme"])
    df_results: DataFrame = resultfromreforms({"amendement" : reforme}, to_compute)

    for scenario in ["base", "amendement"]:
        df_results[prefix_dsr_eligible + scenario] = (
            df_results["dsr_eligible_fraction_bourg_centre" + "_" + scenario]
            | df_results["dsr_eligible_fraction_perequation" + "_" + scenario]
            | df_results["dsr_eligible_fraction_cible" + "_" + scenario]
        )

    return df_results

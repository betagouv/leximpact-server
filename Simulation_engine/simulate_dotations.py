from copy import deepcopy
from pandas import DataFrame  # type: ignore

from dotations.utils_dict import translate_dict  # type: ignore
from dotations.simulation import resultfromreforms  # type: ignore


TABLE_LEXIMPACT_TO_OFDL = {
    "dotations.communes.dsr.eligibilite.popMax": "dotation_solidarite_rurale.seuil_nombre_habitants",
    "dotations.communes.dsr.eligibilite.popChefLieuMax": "dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_nombre_habitants_chef_lieu",
    "dotations.communes.dsr.bourgCentre.eligibilite.partPopCantonMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.seuil_part_population_canton",
    "dotations.communes.dsr.bourgCentre.eligibilite.exclusion.agglomeration.partPopDepartementMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_part_population_dgf_agglomeration_departement",
    "dotations.communes.dsr.bourgCentre.eligibilite.exclusion.agglomeration.popMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_agglomeration",
    "dotations.communes.dsr.bourgCentre.eligibilite.exclusion.agglomeration.popCommuneMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_maximum_commune_agglomeration",
    "dotations.communes.dsr.bourgCentre.eligibilite.exclusion.canton.popChefLieuMin": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_population_dgf_chef_lieu_de_canton",
    "dotations.communes.dsr.bourgCentre.eligibilite.exclusion.potentielFinancier.rapportPotentielFinancierMoyen": "dotation_solidarite_rurale.bourg_centre.eligibilite.exclusion.seuil_rapport_pfi_10000",
    "dotations.communes.dsr.bourgCentre.attribution.popLimite": "dotation_solidarite_rurale.bourg_centre.attribution.plafond_population",
    "dotations.communes.dsr.bourgCentre.attribution.effortFiscalLimite": "dotation_solidarite_rurale.bourg_centre.attribution.plafond_effort_fiscal",
    "dotations.communes.dsr.bourgCentre.attribution.coefMultiplicateurRevitalisationRurale": "dotation_solidarite_rurale.bourg_centre.attribution.coefficient_zrr",
    "dotations.communes.dsr.bourgCentre.attribution.plafonnementPopulation": "population.plafond_dgf",
    "dotations.communes.dsr.perequation.eligibilite.rapportPotentielFinancier": "dotation_solidarite_rurale.perequation.seuil_rapport_potentiel_financier",
    "dotations.communes.dsr.perequation.attribution.repartition.ponderationPotentielFinancier": "dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_habitant",
    "dotations.communes.dsr.perequation.attribution.repartition.ponderationLongueurVoirie": "dotation_solidarite_rurale.attribution.poids_longueur_voirie",
    "dotations.communes.dsr.perequation.attribution.repartition.ponderationNbreEnfants": "dotation_solidarite_rurale.attribution.poids_enfants",
    "dotations.communes.dsr.perequation.attribution.repartition.ponderationPotentielFinancierParHectare": "dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_hectare",
    "dotations.communes.dsr.perequation.attribution.effortFiscalLimite": "dotation_solidarite_rurale.attribution.plafond_effort_fiscal",
    "dotations.communes.dsr.cible.eligibilite.premieresCommunes": "dotation_solidarite_rurale.cible.eligibilite.seuil_classement",
    "dotations.communes.dsu.eligibilite.popMinSeuilBas": "dotation_solidarite_urbaine.eligibilite.seuil_bas_nombre_habitants",
    "dotations.communes.dsu.eligibilite.popMinSeuilHaut": "dotation_solidarite_urbaine.eligibilite.seuil_haut_nombre_habitants",
    "dotations.communes.dsu.eligibilite.rapportPotentielFinancier": "dotation_solidarite_urbaine.eligibilite.seuil_rapport_potentiel_financier",
    "dotations.communes.dsu.eligibilite.pourcentageRangSeuilBas": "dotation_solidarite_urbaine.eligibilite.part_eligible_seuil_bas",
    "dotations.communes.dsu.eligibilite.pourcentageRangSeuilHaut": "dotation_solidarite_urbaine.eligibilite.part_eligible_seuil_haut",
    "dotations.communes.dsu.eligibilite.indiceSynthetique.ponderationPotentielFinancier": "dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_potentiel_financier",
    "dotations.communes.dsu.eligibilite.indiceSynthetique.ponderationLogementsSociaux": "dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_logements_sociaux",
    "dotations.communes.dsu.eligibilite.indiceSynthetique.ponderationAideAuLogement": "dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_aides_au_logement",
    "dotations.communes.dsu.eligibilite.indiceSynthetique.ponderationRevenu": "dotation_solidarite_urbaine.eligibilite.indice_synthetique.poids_revenu",
    "dotations.communes.dsu.attribution.effortFiscalLimite": "dotation_solidarite_urbaine.attribution.plafond_effort_fiscal",
    "dotations.communes.dsu.attribution.facteurClassementMax": "dotation_solidarite_urbaine.attribution.facteur_classement_max",
    "dotations.communes.dsu.attribution.facteurClassementMin": "dotation_solidarite_urbaine.attribution.facteur_classement_min",
    "dotations.communes.dsu.attribution.poidsSupplementaireZoneUrbaineSensible": "dotation_solidarite_urbaine.attribution.poids_quartiers_prioritaires_ville",
    "dotations.communes.dsu.attribution.poidsSupplementaireZoneFrancheUrbaine": "dotation_solidarite_urbaine.attribution.poids_zone_franche_urbaine",
    "dotations.communes.dsu.attribution.augmentationMax": "dotation_solidarite_urbaine.attribution.augmentation_max",
    "dotations.communes.dsr.cible.eligibilite.indiceSynthetique.ponderationPotentielFinancier": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_potentiel_financier",
    "dotations.communes.dsr.cible.eligibilite.indiceSynthetique.ponderationRevenu": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_revenu",
    "dotations.communes.dsr.perequation.attribution.pourcentageAttributionMin": "dotation_solidarite_rurale.perequation.attribution.plancher_ratio_progression",
    "dotations.communes.dsr.perequation.attribution.pourcentageAttributionMax": "dotation_solidarite_rurale.perequation.attribution.plancher_ratio_progression",
    "dotations.communes.dsr.bourgCentre.attribution.pourcentageAttributionMin": "dotation_solidarite_rurale.bourg_centre.attribution.plancher_ratio_progression",
    "dotations.communes.dsr.bourgCentre.attribution.pourcentageAttributionMax": "dotation_solidarite_rurale.bourg_centre.attribution.plafond_ratio_progression",
    "dotations.montants.dsu.variation": "dotation_solidarite_urbaine.augmentation_montant",
    "dotations.montants.dsr.variation": "dotation_solidarite_rurale.augmentation_montant",
}


def format_reforme_openfisca(reforme_a_traduire):
    # passage des dictionnaires avec nombre de clefs variables au format
    # list de dictionnaire : evite de se retrouver avec des champs qui ne correspondent pas
    # à des hiérarchies de variables openfisca)
    # et qui seront consommés par les parsers ad hoc de la réforme
    ref = deepcopy(reforme_a_traduire)

    if "dgf" in ref["dotations"]["montants"]:
        del ref["dotations"]["montants"]["dgf"]  # not implemented in ofdl yet
    try:
        dictionnaire_a_tableautiser = deepcopy(ref["dotations"]["communes"]["dsr"]["bourgCentre"]["attribution"]["plafonnementPopulation"])
        ref["dotations"]["communes"]["dsr"]["bourgCentre"]["attribution"]["plafonnementPopulation"] = sorted(
            [{"threshold": int(seuil), "amount": plafond} for seuil, plafond in dictionnaire_a_tableautiser.items()],
            key=lambda x: x["threshold"])
    except KeyError:
        # on choisit de ne rien soulever si ce champ n'est pas présent dans la réforme.
        # Ca fait qu'une absence de ce paramètre ne fera pas échouer la requête.
        pass
    return {"dgf": translate_dict(ref, TABLE_LEXIMPACT_TO_OFDL, leave_not_found=False)}


def simulate(request_body, prefix_dsr_eligible, prefix_dsr_montant, prefix_dsr_montant_annee_suivante):
    variables_nombre_communes = [
        "dsr_eligible_fraction_bourg_centre",
        "dsr_eligible_fraction_perequation",
        "dsr_eligible_fraction_cible",
        "dsu_eligible",
        "dsu_montant"
    ]
    variables_aggregations = ["potentiel_financier"]
    fractions_dsr = ["bourg_centre", "perequation", "cible"]
    variables_montants_fractions_dsr = ["dsr_montant_hors_garanties_fraction_" + nom_fraction for nom_fraction in fractions_dsr]
    variables_montants_next_year_dsr = ["dsr_montant_eligible_fraction_bourg_centre", "dsr_montant_eligible_fraction_perequation"]
    to_compute = variables_nombre_communes + variables_aggregations + variables_montants_fractions_dsr + variables_montants_next_year_dsr
    reforme = format_reforme_openfisca(request_body["reforme"])
    df_results: DataFrame = resultfromreforms({"amendement" : reforme}, to_compute)

    for scenario in ["base", "amendement"]:
        df_results[prefix_dsr_eligible + scenario] = (
            df_results["dsr_eligible_fraction_bourg_centre" + "_" + scenario]
            | df_results["dsr_eligible_fraction_perequation" + "_" + scenario]
            | df_results["dsr_eligible_fraction_cible" + "_" + scenario]
        )
        df_results[prefix_dsr_montant + scenario] = df_results[[nom_variable + "_" + scenario for nom_variable in variables_montants_fractions_dsr]].sum(axis="columns")
        df_results[prefix_dsr_montant_annee_suivante + scenario] = df_results[[nom_variable + "_" + scenario for nom_variable in variables_montants_next_year_dsr + ["dsr_montant_hors_garanties_fraction_cible"]]].sum(axis="columns")

    return df_results

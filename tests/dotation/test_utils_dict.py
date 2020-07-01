from dotation.utils_dict import translate_dict, flattened_dict, unflattened_dict  # type: ignore


def test_translate_conditions_reelles():
    table_transcription = {"communes.dsr.eligibilite.popMax": "dotation_solidarite_rurale.seuil_nombre_habitants",
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

    dict_example = {
        "communes" : {
            "dsr" : {
                "cible": {
                    "eligibilite": {
                        "premieresCommunes": 10000
                    }
                }
            }
        }
    }
    dict_cible = {
        "dotation_solidarite_rurale": {
            "cible": {
                "eligibilite": {
                    "seuil_classement" : 10000
                }
            }
        }
    }
    translated = translate_dict(dict_example, table_transcription)
    assert(translated == dict_cible)


def test_flattened_dict():
    a = {"a": {"b": {"c": 3, "d": {"e": 4, "f": "chaton"}}}}
    b = {"a.b.c": 3, "a.b.d.e": 4, "a.b.d.f": "chaton"}
    assert(flattened_dict(a) == b)
    assert(unflattened_dict(b) == a)


def test_translate_unchanged():
    dict_trans = {"a": "A", "b": "B"}
    before_translation = {"a": {"b" : 3}}
    after_translation = {"a": {"b" : 3}}
    assert(translate_dict(before_translation, dict_trans) == after_translation)


def test_translate_basic():
    dict_trans = {"a": "A", "b": "B", "d.e": "D.E"}
    before_translation = {"a" : 1, "b" : 2, "c": 3, "d": {"e": 4, "f": 5}}
    after_translation = {"A" : 1, "B" : 2, "c": 3, "D": {"E": 4}, "d": {"f": 5}}
    assert(translate_dict(before_translation, dict_trans) == after_translation)

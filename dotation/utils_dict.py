
# Retourne un dictionnaire flattened à partir d'un nested dictionnaire


def flattened_dict(dict_to_traverse, prechain="", delimiter="."):
    res = {}
    pc = [prechain] if len(prechain) else []
    for k, v in dict_to_traverse.items():
        if isinstance(v, dict):
            res = {**res, **flattened_dict(v, prechain=delimiter.join(pc + [k]))}
        else:
            res[delimiter.join(pc + [k])] = v
    return res


# Retourne un nested dictionnaireà partir d'un dictionnaire flattened
def unflattened_dict(dict_to_traverse, delimiter="."):
    res = {}
    for k, v in dict_to_traverse.items():
        chemin = k.split(delimiter)
        cur = res
        for i in chemin[:-1]:
            if i not in cur:
                cur[i] = {}
            cur = cur[i]
        cur[chemin[-1]] = v
    return res


def test_flattened_dict():
    a = {"a": {"b": {"c": 3, "d": {"e": 4, "f": "chaton"}}}}
    b = {"a.b.c": 3, "a.b.d.e": 4, "a.b.d.f": "chaton"}
    assert(flattened_dict(a) == b)
    assert(unflattened_dict(b) == a)


def translate_dict(dict_to_translate, table_transcription):
    flattened_dict_pretranslation = flattened_dict(dict_to_translate)
    flattened_dict_posttranslation = {}
    for k, v in flattened_dict_pretranslation.items():
        if k in table_transcription:
            new_key = table_transcription[k]
        else:
            new_key = k
        flattened_dict_posttranslation[new_key] = v
    return unflattened_dict(flattened_dict_posttranslation)


def test_translate():
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
                           "communes.dsr.cible.eligibilite.indiceSynthetique.ponderationPotentielFinancier": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_pot_fin",
                           "communes.dsr.cible.eligibilite.indiceSynthetique.ponderationRevenuParHab": "dotation_solidarite_rurale.cible.eligibilite.indice_synthetique.poids_revenu", }

    dict_example = {
        "communes" : {
            "dsr" : {
                "cible": {
                    "eligibilie": {
                        "premieresCommunes": 10000
                    }
                }
            }
        }
    }
    dict_cible = {
        "dotation_solidarite_rurale": {
            "bourg_centre": {
                "eligibilite": {
                    "seuil_classement" : 10000
                }
            }
        }
    }
    assert(translate_dict(dict_example, table_transcription) == dict_cible)


if __name__ == "__main__":
    test_flattened_dict()
    test_translate()

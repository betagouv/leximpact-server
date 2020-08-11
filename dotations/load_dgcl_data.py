import pandas  # type: ignore
import os

# Quelques noms de colonne utiles:
elig_bc_dgcl = "Eligible fraction bourg-centre selon DGCL"
elig_pq_dgcl = "Eligible fraction péréquation selon DGCL"
elig_cible_dgcl = "Eligible fraction cible selon DGCL"
code_comm = "Informations générales - Code INSEE de la commune"
nom_comm = "Informations générales - Nom de la commune"
chef_lieu_de_canton_dgcl = "Dotation de solidarité rurale Bourg-centre - Code commune chef-lieu de canton au 1er janvier 2014"

# Variables openfisca-france-dotations-locales présentes à l'état brut dans le fichier avec le nom de colonne DGCL correspondant.

variables_openfisca_presentes_fichier = {
    'bureau_centralisateur': 'Dotation de solidarité rurale Bourg-centre - Bureaux centralisateurs',
    'chef_lieu_arrondissement': "Dotation de solidarité rurale Bourg-centre - Chef-lieu d'arrondissement au 31 décembre 2014",
    'chef_lieu_de_canton': 'Dotation de solidarité rurale Bourg-centre - Code commune chef-lieu de canton au 1er janvier 2014',
    'chef_lieu_departement_dans_agglomeration': 'Dotation de solidarité rurale Bourg-centre - Chef-lieu de département agglo',
    'part_population_canton': 'Dotation de solidarité rurale Bourg-centre - Pourcentage de la population communale dans le canton',
    'population_dgf': "Informations générales - Population DGF Année N'",
    'population_dgf_agglomeration': "Dotation de solidarité rurale Bourg-centre - Population DGF des communes de l'agglomération",
    'population_dgf_departement_agglomeration': "Dotation de solidarité rurale Bourg-centre - Population départementale de référence de l'agglomération",
    'population_insee': 'Informations générales - Population INSEE Année N ',
    'potentiel_financier': 'Potentiel fiscal et financier des communes - Potentiel financier',
    'potentiel_financier_par_habitant': 'Potentiel fiscal et financier des communes - Potentiel financier par habitant',
    'revenu_total': 'Dotation de solidarité urbaine - Revenu imposable des habitants de la commune',
    'strate_demographique': 'Informations générales - Strate démographique Année N',
    'zrr': 'Dotation de solidarité rurale - Bourg-centre - Commune située en ZRR',
    'effort_fiscal': 'Effort fiscal - Effort fiscal',
    'longueur_voirie': 'Dotation de solidarité rurale - Péréquation - Longueur de voirie en mètres',
    'zone_de_montagne': 'Dotation de solidarité rurale - Péréquation - Commune située en zone de montagne',
    'insulaire': 'Dotation de solidarité rurale - Péréquation - Commune insulaire',
    'superficie': 'Informations générales - Superficie 2019',
    'population_enfants': 'Dotation de solidarité rurale - Péréquation - Population 3 à 16 ans',
    'nombre_logements': 'Dotation de solidarité urbaine - Nombre de logements TH de la commune',
    'nombre_logements_sociaux': 'Dotation de solidarité urbaine - Nombre de logements sociaux de la commune',
    'nombre_beneficiaires_aides_au_logement': 'Dotation de solidarité urbaine - Nombre de bénéficiaires des aides au logement de la commune',
    'population_qpv': 'Dotation de solidarité urbaine - Population QPV',
    'population_zfu': 'Dotation de solidarité urbaine - Population ZFU',
}

# Présente les colonnes du fichier qui représentent des variables openfisca
# résultat telles que calculées par la DGCL

variables_calculees_presentes = {
    'Dotation de solidarité rurale - Péréquation - Part Pfi (avant garantie CN)': 'dsr_fraction_perequation_part_potentiel_financier_par_habitant',
    'Dotation de solidarité rurale - Péréquation - Part VOIRIE (avant garantie CN)': 'dsr_fraction_perequation_part_longueur_voirie',
    'Dotation de solidarité rurale - Péréquation - Part ENFANTS (avant garantie CN)': 'dsr_fraction_perequation_part_enfants',
    'Dotation de solidarité rurale - Péréquation - Part Pfi/hectare (avant garantie CN)': 'dsr_fraction_perequation_part_potentiel_financier_par_hectare',
    'Dotation de solidarité rurale - Cible - Indice synthétique': 'indice_synthetique_dsr_cible',
    'Dotation de solidarité rurale - Cible - Rang DSR Cible': 'rang_indice_synthetique_dsr_cible',
    'Dotation de solidarité rurale - Cible - Part Pfi (avant garantie CN)': 'dsr_fraction_cible_part_potentiel_financier_par_habitant',
    'Dotation de solidarité rurale - Cible - Part VOIRIE (avant garantie CN)': 'dsr_fraction_cible_part_longueur_voirie',
    'Dotation de solidarité rurale - Cible - Part ENFANTS (avant garantie CN)': 'dsr_fraction_cible_part_enfants',
    'Dotation de solidarité rurale - Cible - Part Pfi/hectare (Pfis) (avant garantie CN)': 'dsr_fraction_cible_part_potentiel_financier_par_hectare',
    'Dotation de solidarité rurale Bourg-centre - Montant de la commune éligible': 'dsr_montant_hors_garanties_fraction_bourg_centre',
    "Dotation de solidarité urbaine - Valeur de l'indice synthétique de classement de la commune à la DSU": 'indice_synthetique_dsu',
    'Dotation de solidarité urbaine - Rang de classement à la DSU des communes mét de plus de 10000 habitants': 'rang_indice_synthetique_dsu_seuil_haut',
    'Dotation de solidarité urbaine - Rang de classement à la DSU des communes mét de 5000 à 9999 habitants': 'rang_indice_synthetique_dsu_seuil_bas',
    'Dotation de solidarité urbaine - Montant de la garantie effectivement appliquée à la commune': 'dsu_montant_garantie_non_eligible',
    'Dotation de solidarité urbaine - Montant attribution spontanée DSU': 'dsu_part_spontanee',
    'Dotation de solidarité urbaine - Montant progression de la DSU': 'dsu_part_augmentation',
    'Dotation de solidarité urbaine - Montant total réparti': 'dsu_montant',
}


# Présente les colonnes du fichier qui représentent des variables openfisca
variables_calculees_an_dernier = {
    'Dotation de solidarité rurale Bourg-centre - Montant de la commune éligible': 'dsr_montant_hors_garanties_fraction_bourg_centre',
    'Dotation de solidarité urbaine - Montant attribution spontanée DSU': 'dsu_part_spontanee',
    'Dotation de solidarité urbaine - Montant progression de la DSU': 'dsu_part_augmentation',
    'Dotation de solidarité urbaine - Montant total réparti': 'dsu_montant',
}


# A partir de l'adresse du tableau publié par la DGCL, produit un tableau contenant toutes les colonnes nécessaires
# au calcul des dotations.
# il a deux sources de données :
# - des colonnes déjà présentes dans le fichier (qu'il suffit de renommer), leur nom
# est présent dans le dictionnaire variables_openfisca_presentes_fichier. On
# met aussi tout ce qui apparait dans autres_cols_interessantes (pour qu'un export)
# de data soit sympa;
# - des colonnes qu'il faut construire, et qui sont ajoutées petit à petit
# La fonction outputte un dataframe qui contient des variables openfisca
# et d'autres colonnes sympas. On fait la différence super facilement car toutes
# les colonnes non-openfisca contiennent un espace. Je sais, c'est propre.


# Fichiers disponibles sur https://www.data.gouv.fr/fr/datasets/criteres-de-repartition-des-dotations-versees-par-letat-aux-collectivites-territoriales/
def load_dgcl_file(path="assets/data/2019-communes-criteres-repartition.csv"):
    try:
        data = pandas.read_csv(path, decimal=",", dtype={code_comm: str, chef_lieu_de_canton_dgcl: str})
    except FileNotFoundError:
        print("file", path, "was not found")
        print("ls :", os.listdir("."))
        print("cwd :", os.getcwd())
        raise
    return data


def ajoute_population_plus_grande_commune_agglomeration(
        variables_openfisca_presentes_fichier, data, plus_grosse_commune):
    '''
    Identifie la plus grande commune d'une agglomération en terme de nombre d'habitants
    et l'ajoute au dataframe 'data' fourni en entrée à la colonne 'plus_grosse_commune'.

    Le fichier DGCL ne contient pas d'identifiant d'agglomération par commune.
    Les agglomérations sont donc reconstituées comme suit :

    1. Nous avons par commune le total de la population de l'agglomération à laquelle elle appartient.
    Nous regroupons les communes ayant ce même nombre de population d'agglomération.

    2. Ensuite, par groupe de commune ainsi organisé, nous vérifions qu'en sommant la population
    spécifique à chaque commune, nous ne dépassons pas la population de l'agglomération.
    Ainsi, nous nous assurons que nous n'avons pas créé de groupe de plusieurs agglomérations
    qui, par hasard, auraient eu la même taille de population.
    Ce cas survient sur quelques données DGCL 2019.

    3. On nettoie les agglomérations mal reconstituées.
    En particulier, on neutralise la population de la plus grande commune de ces agglomérations.
    '''
    # 1.
    # Niveau ceinture blanche : on groupe by la taille totale de l'agglo (c'est ce qu'on fait icis)
    # À venir : Niveau ceinture orange : en plus de ce critère, utiliser des critères géographiques pour localiser les agglos.
    # À venir : Ceinture rouge : on trouve des données sur les agglos de référence de chaque commune
    pop_agglo = variables_openfisca_presentes_fichier["population_dgf_agglomeration"]
    pop_dgf = variables_openfisca_presentes_fichier["population_dgf"]
    max_pop_plus_grosse_commune = data.groupby(pop_agglo)[[pop_dgf]].max()  # index = pop_agglo / lignes en agglo à vérifier

    # 2.
    # Ca marche car le plus haut nombre d'habitants à être partagé par 2 agglo est 23222
    # print(somme_pop_plus_grosse_commune[somme_pop_plus_grosse_commune.index!=somme_pop_plus_grosse_commune[somme_pop_plus_grosse_commune.columns[0]]])

    # 3.
    max_pop_plus_grosse_commune.columns = [plus_grosse_commune]
    max_pop_plus_grosse_commune.loc[max_pop_plus_grosse_commune.index == 0, plus_grosse_commune] = 0
    return data.merge(max_pop_plus_grosse_commune, left_on=pop_agglo, right_index=True).sort_index()


def ajuste_part_communes_canton(variables_openfisca_presentes_fichier, data, code_comm):
    part_population_canton = variables_openfisca_presentes_fichier["part_population_canton"]
    data.loc[(data[code_comm] == "57163") | (data[code_comm] == "87116"), part_population_canton] -= 0.0001
    return data


def ajoute_appartenance_outre_mer(data, outre_mer_dgcl):
    '''
    Pour chaque commune, détermine son appartenance à l'outre-mer d'après son département
    et l'ajoute au dataframe 'data' à la colonne de nom désigné par 'outre_mer_dgcl'.
    '''
    departement = "Informations générales - Code département de la commune"
    data[departement] = data[departement].astype(str)
    data[outre_mer_dgcl] = (data[departement].str.len() > 2) & (~data[departement].str.contains("A")) & (~data[departement].str.contains("B"))
    return data


def ajoute_est_chef_lieu_canton(data, is_chef_lieu_canton, code_comm):
    chef_lieu_de_canton_dgcl = "Dotation de solidarité rurale Bourg-centre - Code commune chef-lieu de canton au 1er janvier 2014"
    data[is_chef_lieu_canton] = (data[chef_lieu_de_canton_dgcl] == data[code_comm])
    return data


def ajoute_population_chef_lieu_canton(data, pop_dgf, pop_dgf_chef_lieu_canton, code_comm):
    chef_lieu_de_canton_dgcl = "Dotation de solidarité rurale Bourg-centre - Code commune chef-lieu de canton au 1er janvier 2014"

    table_chef_lieu_canton = data[[code_comm, pop_dgf]]
    table_chef_lieu_canton.columns = [code_comm, pop_dgf_chef_lieu_canton]

    data = data.merge(table_chef_lieu_canton, left_on=chef_lieu_de_canton_dgcl, right_on=code_comm, how="left", suffixes=("", "_Chef_lieu"))
    data[pop_dgf_chef_lieu_canton] = data[pop_dgf_chef_lieu_canton].fillna(0).astype(int)
    return data


def corrige_revenu_moyen_strate(data, variables_openfisca_presentes_fichier, revenu_moyen_strate, outre_mer_dgcl):
    # Certains revenus moyens de communes sont missing...
    # pour ceci, calculons le revenu moyen de chaque strate
    strate = variables_openfisca_presentes_fichier["strate_demographique"]
    revenu_total_dgcl = variables_openfisca_presentes_fichier["revenu_total"]
    pop_insee = variables_openfisca_presentes_fichier["population_insee"]

    tableau_donnees_par_strate = data[(~data[outre_mer_dgcl])].groupby(strate)[[pop_insee, revenu_total_dgcl]].sum()
    tableau_donnees_par_strate[revenu_moyen_strate] = tableau_donnees_par_strate[revenu_total_dgcl] / tableau_donnees_par_strate[pop_insee]

    # Avant de corriger les revenus, il nous faut calculer les revenus moyens par strate
    # Les revenus de certaines communes sont ignorés dans le calcul du revenu moyen de la strate, on sait pas pourquoi
    # (ptet la DGCL préserve le secret statistique dans ses metrics agrégées?)
    # La conséquence de la ligne de code qui suit est qu'on utilise la même méthodo que la DGCL
    # donc on a un classement cible plus proche de la vérité.
    # L'inconvénient est que les revenus moyens par strate ne sont pas reproductibles en l'état
    # On pourrait rajouter une variable dans Openfisca qui dirait "est ce que cette commune est
    # prise en compte dans la moyenne de revenu moyen par strate?" , mais le calcul de cette variable
    # n'est pas dans la loi.
    return data.merge(tableau_donnees_par_strate[[revenu_moyen_strate]], left_on=strate, right_index=True)


def corrige_revenu_total_commune(data, variables_openfisca_presentes_fichier, revenu_moyen_strate: str):
    # Corrige les infos sur le revenu _total_ de la commune quand il est à 0
    # et que l'indice synthétique est renseigné.
    # Certains revenus _moyens_ de communes sont missing alors qu'ils interviennent dans le calcul de l'indice synthétique...
    actual_indice_synthetique = "Dotation de solidarité rurale - Cible - Indice synthétique"
    pot_fin_strate = "Potentiel fiscal et financier des communes - Potentiel financier moyen de la strate"
    pot_fin_par_hab = "Potentiel fiscal et financier des communes - Potentiel financier par habitant"

    revenu_total_dgcl = variables_openfisca_presentes_fichier["revenu_total"]
    pop_insee = variables_openfisca_presentes_fichier["population_insee"]

    # On essaye de remplir les revenus moyens manquants grâce à notre super equation:
    # RT = pop_insee * (0.3*RMStrate)/(IS-0.7 * PF(strate)/PF)
    revenu_moyen_par_habitant_commune = (
        0.3 * data[revenu_moyen_strate] / (
            data[actual_indice_synthetique] - 0.7 * data[pot_fin_strate] / data[pot_fin_par_hab]
        )
    )
    data.loc[(data[revenu_total_dgcl] == 0) & (data[pop_insee] > 0) & (data[actual_indice_synthetique] > 0), revenu_total_dgcl] = revenu_moyen_par_habitant_commune * data[pop_insee]

    return data


def get_dgcl_results(data):
    # renvoie un DataFrame qui contient les colonnes :
    # code commune : avec le nom original car on n'a toujours pas de variable OFDL
    # des variables de RESULTATS tels que calculés par la DGCL.
    # Ces variables portent leur nom openfisca parce que bon on va pas se trimballer partout
    # les noms du fichier (à part pour leur code commune bien sûr)
    resultats_extraits = data[[code_comm]]

    # Ajout de variables qui n'existent pas à l'état brut dans le fichier :

    # L'éligibilité est déterminée en fonction de la présence ou non d'un versement non nul
    resultats_extraits["dsr_eligible_fraction_bourg_centre"] = (data["Dotation de solidarité rurale Bourg-centre - Montant de la commune éligible"] > 0)
    resultats_extraits["dsr_eligible_fraction_perequation"] = (data["Dotation de solidarité rurale - Péréquation - Part Pfi (avant garantie CN)"] > 0)

    # Pour le rang cible, on dispose du rang, qu'on utilise pour déterminer l'éligibilité au sens de la DGCL
    rang_indice_synthetique = "Dotation de solidarité rurale - Cible - Rang DSR Cible"
    resultats_extraits["dsr_eligible_fraction_cible"] = (data[rang_indice_synthetique] > 0) & (data[rang_indice_synthetique] <= 10000)

    # Eligibilité DSU
    resultats_extraits["dsu_eligible"] = (data["Dotation de solidarité urbaine - Montant attribution spontanée DSU"] > 0)

    # Calcul de la somme des quatre parts des fractions cibles et péréquation, qui
    # n'apparaissent pas à l'état brut dans le fichier DGCL
    resultats_extraits["dsr_montant_hors_garanties_fraction_perequation"] = data[
        [nom_colonne
         for nom_colonne in variables_calculees_presentes.keys()
         if 'Dotation de solidarité rurale - Péréquation - Part' in nom_colonne]
    ].sum(axis='columns')
    resultats_extraits["dsr_montant_hors_garanties_fraction_cible"] = data[
        [nom_colonne
         for nom_colonne in variables_calculees_presentes.keys()
         if 'Dotation de solidarité rurale - Cible - Part' in nom_colonne]
    ].sum(axis='columns')

    # Ajout des variables de résultat présentes à l'état brut dans le fichier
    for nom_dgcl, nom_ofdl in variables_calculees_presentes.items():
        resultats_extraits[nom_ofdl] = data[nom_dgcl]
    return resultats_extraits


def get_last_year_dotations(data):
    # renvoie un DataFrame qui contient les colonnes :
    # code commune : avec le nom original car on n'a toujours pas de variable OFDL
    # des variables de RESULTATS tels que calculés par la DGCL.
    # Ces variables portent leur nom openfisca parce que bon on va pas se trimballer partout
    # les noms du fichier (à part pour leur code commune bien sûr)
    resultats_extraits = data[[code_comm]]

    # Ajout de variables qui n'existent pas à l'état brut dans le fichier :

    # L'éligibilité est déterminée en fonction de la présence ou non d'un versement non nul
    # Ajout des variables de résultat présentes à l'état brut dans le fichier
    for nom_dgcl, nom_ofdl in variables_calculees_an_dernier.items():
        resultats_extraits[nom_ofdl] = data[nom_dgcl]
    resultats_extraits["dsu_montant_eligible"] = resultats_extraits["dsu_part_spontanee"] + resultats_extraits["dsu_part_augmentation"]
    return resultats_extraits


def insert_dsu_garanties(data, period="2019", filename="assets/data/garanties_dsu.csv"):
    data_garanties = pandas.read_csv(filename)
    data_garanties_period = data_garanties[[code_comm, period]]
    data_garanties_period.columns = [code_comm, "dsu_montant_garantie_pluriannuelle"]
    data = data.merge(data_garanties_period, how="left", on=code_comm)
    data["dsu_montant_garantie_pluriannuelle"] = data["dsu_montant_garantie_pluriannuelle"].fillna(0)
    return data


def adapt_dgcl_data(data):
    extracolumns = {}
    #
    # add plus grande commune agglo column
    #
    plus_grosse_commune = "Population plus grande commune de l'agglomération"
    data = ajoute_population_plus_grande_commune_agglomeration(variables_openfisca_presentes_fichier, data, plus_grosse_commune)
    extracolumns["population_dgf_maximum_commune_agglomeration"] = plus_grosse_commune

    #
    # deux communes ont une part qui apparait >= à 15% du canton mais en fait non.
    # On triche mais pas beaucoup, la part dans la population du canton
    # n'est pas une info facile à choper exactement.
    # Manquant : nombre d'habitants du canton mais nous avons la part population canton (malheureusement arrondie).
    #
    data = ajuste_part_communes_canton(variables_openfisca_presentes_fichier, data, code_comm)
    #
    # introduit la valeur d'outre mer
    #
    outre_mer_dgcl = "commune d'outre mer"
    data = ajoute_appartenance_outre_mer(data, outre_mer_dgcl)
    extracolumns["outre_mer"] = outre_mer_dgcl

    # Mise des chefs lieux de canton en une string de 5 caractères.
    data[chef_lieu_de_canton_dgcl] = data[chef_lieu_de_canton_dgcl].apply(lambda x: str(x).zfill(5))

    #
    # Chope les infos du chef-lieu de canton
    #
    is_chef_lieu_canton = "Chef-lieu de canton"
    data = ajoute_est_chef_lieu_canton(data, is_chef_lieu_canton, code_comm)
    extracolumns["chef_lieu_de_canton"] = is_chef_lieu_canton

    pop_dgf = variables_openfisca_presentes_fichier["population_dgf"]
    pop_dgf_chef_lieu_canton = pop_dgf + " du chef-lieu de canton"
    data = ajoute_population_chef_lieu_canton(data, pop_dgf, pop_dgf_chef_lieu_canton, code_comm)
    extracolumns["population_dgf_chef_lieu_de_canton"] = pop_dgf_chef_lieu_canton

    # Corrige les infos sur le revenu _total_ de la commune quand il est à 0
    # et que l'indice synthétique est renseigné. Certains revenus _moyens_ sont missing...
    # Avant de corriger les revenus, il nous faut calculer les revenus moyens par strate
    revenu_moyen_strate = " Revenu imposable moyen par habitant de la strate"
    data = corrige_revenu_moyen_strate(data, variables_openfisca_presentes_fichier, revenu_moyen_strate, outre_mer_dgcl)
    extracolumns["revenu_par_habitant_moyen"] = revenu_moyen_strate

    data = corrige_revenu_total_commune(data, variables_openfisca_presentes_fichier, revenu_moyen_strate)

    #
    # Génère le dataframe au format final :
    # Il contient toutes les variables qu'on rentrera dans openfisca au format openfisca
    # + Des variables utiles qu'on ne rentre pas dans openfisca
    #
    # colonnes = colonnes du fichier dgcl qui deviennent les inputs pour les calculs openfisca
    # lignes = 1 ligne par commune
    # Restriction aux colonnes intéressantes :
    rang_indice_synthetique = "Dotation de solidarité rurale - Cible - Rang DSR Cible"
    translation_cols = {**variables_openfisca_presentes_fichier, **extracolumns}
    data[elig_bc_dgcl] = (data["Dotation de solidarité rurale Bourg-centre - Montant de la commune éligible"] > 0)
    data[elig_pq_dgcl] = (data["Dotation de solidarité rurale - Péréquation - Part Pfi (avant garantie CN)"] > 0)
    data[elig_cible_dgcl] = (data[rang_indice_synthetique] > 0) & (data[rang_indice_synthetique] <= 10000)
    # Au delà des colonnes traduites, on garde ces colonnes dans le dataframe de sortie.
    # Pour garder des informations pour identifier la commune
    autres_cols_interessantes = [code_comm, nom_comm]
    data = data[autres_cols_interessantes + list(translation_cols.values())]

    # Renomme colonnes
    invert_dict = {name_dgcl: name_ofdl for name_ofdl, name_dgcl in translation_cols.items()}
    data.columns = [column if column not in invert_dict else invert_dict[column] for column in data.columns]

    # Passe les "booléens dgf" (oui/non) en booléens normaux
    liste_columns_to_real_bool = ["bureau_centralisateur", "chef_lieu_arrondissement", "zrr", "chef_lieu_departement_dans_agglomeration"]
    for col in liste_columns_to_real_bool:
        data[col] = (data[col].str.contains(pat="oui", case=False))

    return data.sort_index()


if __name__ == "__main__":
    print(adapt_dgcl_data(load_dgcl_file()))

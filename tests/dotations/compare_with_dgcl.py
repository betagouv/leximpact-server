from dotations.simulation import simulation_from_dgcl_csv  # type: ignore
from dotations.load_dgcl_data import load_dgcl_file, adapt_dgcl_data, get_dgcl_results  # type: ignore
from openfisca_france_dotations_locales import CountryTaxBenefitSystem  # type: ignore
from time import time
#
# Petit script auxiliaire pour comparer les résultats trouvés avec notre parser + OFDL
# aux résultats trouvés.
#
# On peut en faire des tests, mais il y a un tradeoff entre correspondre plus précisément
# aux résultats DGCL et obtenir des résultats cohérents plus tard.


# Quelques noms de colonne utiles:
code_comm = "Informations générales - Code INSEE de la commune"
nom_comm = "Informations générales - Nom de la commune"


# Columns to compare that contain a bool type
# A pivot table will be printed that counts the number of values that have the different combination
def compare_results_bool(data, nom_actual, nom_expected):
    return data.pivot_table(code_comm, index=nom_actual, columns=nom_expected, aggfunc="count", fill_value=0)


# Columns to compare that contain a number
# There will be great output, e.g. :
# Absolute differences : < 1 €, quantiles extrèmes, deciles de différence
# Différence relative (osef un peu)
# Erreur quadratique
# Norme L1, L2,
def compare_results_real(data, nom_actual, nom_expected):
    res = {}
    data_non_nul = data[(data[nom_actual] != 0) & data[nom_expected] != 0]
    data["calcul non nul"] = data[nom_actual] != 0
    data["precalc non nul"] = data[nom_expected] != 0
    res["boolean differences"] = compare_results_bool(data, "calcul non nul", "precalc non nul")

    diff = sorted((data_non_nul[nom_actual] - data_non_nul[nom_expected]).tolist())
    nb_non_nul = len(data_non_nul)
    avg_size = (sum(data_non_nul[nom_actual]) / nb_non_nul) if nb_non_nul else 0
    avg_size2 = sum([i * i for i in data_non_nul[nom_actual]]) / (nb_non_nul - 1)
    res["Moyenne base"] = avg_size
    res["variance"] = avg_size2 - avg_size * avg_size

    # Norme L1 : ecart absolu moyen
    res["L1"] = (sum([abs(dif) for dif in diff]) / nb_non_nul) if nb_non_nul else 0
    # Norme L2 (norme euclidienne) : utile pour l'estimation
    res["L2"] = ((sum([dif * dif for dif in diff]) / nb_non_nul)**0.5) if nb_non_nul else 0
    # Ah ben qu'est ce que je disais : la norme L2 permet de regarder
    # quelle part de variance de la variable est expliquée par notre
    # modèle
    res["pourcentage expliqué"] = (1 - res["L2"]**2 / res["variance"]) if res["variance"] else 0
    # Différence maximale. Sert pas à grand chose.
    res["L∞"] = max([0]+[abs(dif) for dif in diff])
    quantiles = [0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.98, 0.99]
    # Statistiques d'ordre sur les différences (min, max et quantiles)
    res["min"] = min(diff) if diff else "NA"
    res["max"] = max(diff) if diff else "NA"
    res["quantiles"] = {}
    for q in quantiles:
        rang = int(q * (nb_non_nul - 1) + 0.5)
        if rang<len(diff):
            res["quantiles"][q] = (rang, diff[rang])
    tolerance_difference = 1

    # nombre de résultats considérés comme égaux (en fonction de la tolérance acceptable)
    res["differents"] = len([d for d in diff if abs(d) > tolerance_difference])
    res["identiques"] = nb_non_nul - res["differents"]
    return res


def print_eligible_comparison():
    PERIOD = "2020"
    data_dgcl = load_dgcl_file()
    data_calc_dgcl = get_dgcl_results(data_dgcl)

    data_sim = adapt_dgcl_data(data_dgcl)
    TBS = CountryTaxBenefitSystem()
    sim = simulation_from_dgcl_csv(PERIOD, data_sim, TBS)

    # on va recalculer nous même toutes les colonnes (sauf le code commune)
    colonnes_to_compute = list(data_calc_dgcl.columns[1:])

    for variable_to_compute in colonnes_to_compute:
        data_sim[variable_to_compute] = sim.calculate(variable_to_compute, PERIOD)

    # Merge DGCL results with data_sim
    previous_length_data = len(data_sim)
    data_sim = data_sim.merge(data_calc_dgcl, how="inner", on=code_comm, suffixes=["", "_precalc"])
    assert(len(data_sim) == previous_length_data)

    summary_variables = {}  # récupère les R²

    BLEU_CLAIR = "\x1b[1;36;40m"
    STOP_COULEUR = "\033[0m"
    for nom_ofdl in colonnes_to_compute:
        print(f"{BLEU_CLAIR}Comparaison DGCL vs nous pour le calcul de", nom_ofdl, STOP_COULEUR)
        if data_sim[nom_ofdl].dtypes.name == 'bool':
            print(compare_results_bool(data_sim, nom_ofdl, nom_ofdl + "_precalc"))
        else:
            # On va printer de manière quelque peu désordonnées diverses métriques nous informant
            # sur la précision de notre calcul
            resultats_comparaison = compare_results_real(data_sim, nom_ofdl, nom_ofdl + "_precalc")
            print("***Différence de valeur nul/non nul***")
            print(resultats_comparaison["boolean differences"])
            print("***Statistiques de base (variable à prédire)***")
            print("Moyenne base", resultats_comparaison["Moyenne base"])
            print("Ecart-type", resultats_comparaison["variance"] ** 0.5)
            print("***R² : pourcentage de la variance expliqué***")
            print(f"{BLEU_CLAIR}", "{:.4f}%".format(resultats_comparaison["pourcentage expliqué"] * 100) , STOP_COULEUR, sep="")
            summary_variables[nom_ofdl] = resultats_comparaison["pourcentage expliqué"] * 100
            print("***Différence entre prédit et précalculé***")
            for cle in ["L1", "L2", "L∞"]:
                print(cle, ": ", resultats_comparaison[cle])
            print("***Différence entre prédit et précalculé : répartition des écarts***")
            for cle in ["min", "max"]:
                print("ecart", cle, resultats_comparaison[cle])
            print('***Différence entre prédit et précalculé : "identiques"***')
            for cle in ["differents", "identiques"]:
                print(cle, resultats_comparaison[cle])
            print("***Répartition des écarts ordonnés par quantiles d'erreur***")
            for quantile_borne in resultats_comparaison["quantiles"]:
                rang, valeur = resultats_comparaison["quantiles"][quantile_borne]
                # le rang représente la quantité de communes concernées
                print("{}% (rang {})\t {:.2f}".format(int(quantile_borne * 100), rang, valeur))
    erreur_totale = 100 * len(summary_variables) - sum(summary_variables.values())
    print(f"{BLEU_CLAIR}")
    print("Résumé des pourcentages expliqués :")
    largeur_justify_name = max([len(nom) for nom in summary_variables]) + 3
    for variable, pourcentage_explique_variable in summary_variables.items():
        print("{}{:>8.4f}".format(variable.ljust(largeur_justify_name, ' '), pourcentage_explique_variable))
    print("Total des erreurs qui a peu de sens mathématique :")
    print(erreur_totale)
    print(STOP_COULEUR)


if __name__ == "__main__":
    st = time()
    print_eligible_comparison()
    print("> Elapsed time: {:.2f}".format(time() - st))

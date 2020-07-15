from dotations.simulation import simulation_from_dgcl_csv  # type: ignore
from dotations.load_dgcl_data import load_dgcl_file, adapt_dgcl_data  # type: ignore
from openfisca_france_dotations_locales import CountryTaxBenefitSystem  # type: ignore
from time import time

#
# Petit script auxiliaire pour comparer les résultats trouvés avec notre parser + OFDL
# aux résultats trouvés.
#
# On peut en faire des tests, mais il y a un tradeoff entre correspondre plus précisément
# aux résultats DGCL et obtenir des résultats cohérents plus tard.


# Quelques noms de colonne utiles:
elig_bc_dgcl = "Eligible fraction bourg-centre selon DGCL"
elig_pq_dgcl = "Eligible fraction péréquation selon DGCL"
elig_cible_dgcl = "Eligible fraction cible selon DGCL"
code_comm = "Informations générales - Code INSEE de la commune"
nom_comm = "Informations générales - Nom de la commune"


tocompare = {"dsr_eligible_fraction_bourg_centre": elig_bc_dgcl,
             "dsr_eligible_fraction_perequation": elig_pq_dgcl,
             "dsr_eligible_fraction_cible": elig_cible_dgcl}


# Columns to compare that contain a bool type
# A pivot table will be printed that counts the number of values that have the different combination
def compare_results_bool(data, nom_actual, nom_expected):
    return data.pivot_table(code_comm, index=nom_actual, columns=nom_expected, aggfunc="count", fill_value=0)


def check_variables_bool(data):
    res = {}
    for k, v in tocompare.items():
        res[k] = compare_results_bool(data, k, v)
    return res


# Columns to compare that contain a number
# There will be great output, e.g. :
# Absolute differences : < 1 €, quantiles extrèmes, deciles de différence
# Différence relative (osef un peu)
# Erreur quadratique
# Norme L1, L2,
def compare_results_real(data, nom_actual, nom_expected):
    res = {}
    data_non_nul = data[(data[nom_actual] != 0) | data[nom_expected] != 0]
    diff = sorted((data_non_nul[nom_actual] - data_non_nul[nom_expected]).tolist())
    nb_non_nul = len(data_non_nul)
    avg_size = sum(data_non_nul[nom_actual]) / nb_non_nul
    avg_size2 = sum([i * i for i in data_non_nul[nom_actual]]) / (nb_non_nul - 1)
    res["Moyenne base"] = avg_size
    res["variance"] = avg_size2 - avg_size * avg_size

    # Norme L1 : ecart absolu moyen
    res["L1"] = sum([abs(dif) for dif in diff]) / nb_non_nul
    # Norme L2 (norme euclidienne) : utile pour l'estimation
    res["L2"] = (sum([dif * dif for dif in diff]) / nb_non_nul)**0.5
    # Ah ben qu'est ce que je disais : la norme L2 permet de regarder
    # quelle part de variance de la variable est expliquée par notre
    # modèle
    res["pourcentage expliqué"] = 1 - res["L2"]**2 / res["variance"]
    # Différence maximale. Sert pas à grand chose.
    res["L∞"] = max([abs(dif) for dif in diff])
    quantiles = [0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.98, 0.99]
    # Statistiques d'ordre sur les différences (min, max et quantiles)
    res["min"] = min(diff)
    res["max"] = max(diff)
    res["quantiles"] = {}
    for q in quantiles:
        rang = int(q * (nb_non_nul - 1) + 0.5)
        res["quantiles"][q] = (rang, diff[rang])
    tolerance_difference = 1

    # nombre de résultats considérés comme égaux (en fonction de la tolérance acceptable)
    res["differents"] = len([d for d in diff if abs(d) > tolerance_difference])
    res["identiques"] = nb_non_nul - res["differents"]
    return res

def print_eligible_comparison():
    PERIOD = "2020"
    DATA = adapt_dgcl_data(load_dgcl_file())
    TBS = CountryTaxBenefitSystem()
    sim = simulation_from_dgcl_csv(PERIOD, DATA, TBS)
    colonnes_to_compare = ["dsr_eligible_fraction_bourg_centre",
                           "dsr_eligible_fraction_perequation",
                           "dsr_eligible_fraction_cible"]

    for variable_to_compute in colonnes_to_compare + ["indice_synthetique_dsr_cible", "rang_indice_synthetique_dsr_cible"]:
        DATA[variable_to_compute] = sim.calculate(variable_to_compute, PERIOD)

    DATA.to_csv("data_compare.csv")

    for nom_ofdl, resultats_comparaison in check_variables_bool(DATA).items():
        print("Comparaison DGCL vs nous pour le calcul de", nom_ofdl)
        print(resultats_comparaison)


if __name__ == "__main__":
    st = time()
    print_eligible_comparison()
    print("Elapsed : {:.2f}".format(time() - st))

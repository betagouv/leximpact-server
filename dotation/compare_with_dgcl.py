from simulation import simulation_from_dgcl_csv
from load_dgcl_data import load_dgcl_file
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


def check_variables_bool(data):
    res = {}
    for k, v in tocompare.items():
        res[k] = data.pivot_table(code_comm, index=k, columns=v, aggfunc="count", fill_value=0)
    return res


def print_eligible_comparison():
    PERIOD = "2020"
    DATA = load_dgcl_file()
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

from Simulation_engine.simulate_pop_from_reform import (
    simulation,
    PERIOD,
    TBS,
    TBS_PLF,
    DUMMY_DATA,
)


# Genere un csv contenant les résultats par défaut du PLF et du code existant.
# A exécuter manuellement, puis uploader manuellement le fichier texte avec la fonction
# preload.py (i.e. comme nous faisons avec les données sources et les emails)


def generate_default_results():
    # Keeping computations short with option to keep file under 1000 FF
    # DUMMY_DATA = DUMMY_DATA[(DUMMY_DATA["idmen"] > 2500) & (DUMMY_DATA["idmen"] < 7500)]
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS)
    # precalcul cas de base sur la population pour le cache
    base_results = simulation_base_deciles[1]["foyer_fiscal"][["wprm", "idfoy"]]
    base_results["avant"] = simulation_base_deciles[0].calculate("irpp", PERIOD)
    simulation_plf_deciles = simulation(PERIOD, DUMMY_DATA, TBS_PLF)
    base_results["plf"] = simulation_plf_deciles[0].calculate("irpp", PERIOD)
    base_results[["idfoy", "avant", "plf", "wprm"]].to_csv(
        "base_results.csv", index=False
    )
    return base_results


if __name__ == "__main__":
    generate_default_results()

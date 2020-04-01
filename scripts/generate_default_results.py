from Simulation_engine.simulate_pop_from_reform import (
    simulation,
    PERIOD,
    TBS_DEFAULT,
    DUMMY_DATA,
)


# Genere un csv contenant les résultats par défaut du PLF et du code existant.
# A exécuter manuellement, puis uploader manuellement le fichier texte avec la fonction
# preload.py (i.e. comme nous faisons avec les données sources et les emails)


def generate_default_results():
    # precalcul cas de base sur la population pour le cache
    base_results = None
    liste_base_reformes = []
    for reforme in TBS_DEFAULT:
        liste_base_reformes += [reforme]
        bulk_data_simulation, data_by_entity = simulation(
            PERIOD, DUMMY_DATA, TBS_DEFAULT[reforme]
        )
        if base_results is None:
            base_results = data_by_entity["foyer_fiscal"][["wprm", "idfoy"]]
        base_results[reforme] = bulk_data_simulation.calculate("irpp", PERIOD)

    base_results[["idfoy"] + liste_base_reformes + ["wprm"]].to_csv(
        "base_results.csv", index=False
    )
    return base_results


if __name__ == "__main__":
    generate_default_results()

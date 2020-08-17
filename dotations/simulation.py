from openfisca_core.simulation_builder import SimulationBuilder  # type: ignore
from dotations.load_dgcl_data import (  # type: ignore
    load_dgcl_file,
    adapt_dgcl_data,
    insert_dsu_garanties,
    insert_dsr_garanties_communes_nouvelles,
    get_last_year_dotations)
# Actually runs the simulations
from openfisca_france_dotations_locales import CountryTaxBenefitSystem  # type: ignore
from dotations.reform import DotationReform  # type: ignore
import numpy as np  # type: ignore

code_comm = "Informations générales - Code INSEE de la commune"


def simulation_from_dgcl_csv(period, data, tbs, data_previous_year=None):
    sb = SimulationBuilder()
    sb.create_entities(tbs)
    sb.declare_person_entity("commune", data.index)
    simulation = sb.build(tbs)
    simulation.max_spiral_loops = 10
    for champ_openfisca in data.columns:
        if " " not in champ_openfisca:  # oui c'est comme ça que je checke
            # qu'une variable es openfisca ne me jugez pas
            simulation.set_input(
                champ_openfisca,
                period,
                data[champ_openfisca],
            )
    # data_previous_year est un dataframe dont toutes les colonnes
    # portent des noms de variables openfisca
    # et contiennent des valeurs de l'an dernier.
    if data_previous_year is not None:
        # on rassemble les informations de l'an dernier pour les communes
        # qui existent cette année (valeurs nouvelles communes à zéro)
        data = data.merge(data_previous_year, on=code_comm, how='left', suffixes=["_currentyear", ""])
        for champ_openfisca in data_previous_year.columns:
            if " " not in champ_openfisca:  # oui c'est comme ça que je checke
                # qu'une variable est openfisca ne me jugez pas
                simulation.set_input(
                    champ_openfisca,
                    str(int(period) - 1),
                    data[champ_openfisca].fillna(0),
                )
    return simulation


# outputte un dataframe qui contient :
# l'output normal de load_
# prend un dictionnaire de reformes (apres, eventuellement PLF)

def resultfromreforms(dict_ref=None, to_compute_res=("dsr_eligible_fraction_bourg_centre", "dsr_eligible_fraction_perequation", "dsr_eligible_fraction_cible")):
    PERIOD = "2020"
    # some of these can be preloaded in memory to improve performance.
    try:
        # Will work when app is launched with the command in Procfile
        # (for example in Scalingo)
        DATA = adapt_dgcl_data(load_dgcl_file("../assets/data/2019-communes-criteres-repartition.csv"))
        DATA = insert_dsu_garanties(DATA, PERIOD, "../assets/data/garanties_dsu.csv")
        DATA = insert_dsr_garanties_communes_nouvelles(DATA, PERIOD, folder="../assets/data/")
        results_last_year = get_last_year_dotations(load_dgcl_file("../assets/data/2019-communes-criteres-repartition.csv"))

    except FileNotFoundError:
        # Will work when app is launched from home folder (with make run, or in circleCI)
        DATA = adapt_dgcl_data(load_dgcl_file("assets/data/2019-communes-criteres-repartition.csv"))
        DATA = insert_dsu_garanties(DATA, PERIOD, "assets/data/garanties_dsu.csv")
        DATA = insert_dsr_garanties_communes_nouvelles(DATA, PERIOD, folder="assets/data/")
        results_last_year = get_last_year_dotations(load_dgcl_file("assets/data/2019-communes-criteres-repartition.csv"))

    data_last_year = results_last_year[[code_comm, "dsu_montant_eligible", "dsr_montant_eligible_fraction_bourg_centre", "dsr_montant_eligible_fraction_perequation", "dsr_montant_hors_garanties_fraction_cible"]]

    TBS = CountryTaxBenefitSystem()
    dict_sims = {"base": simulation_from_dgcl_csv(PERIOD, DATA, TBS, data_last_year)}
    # création d'un dictionnaire contenant une simulation par output
    if dict_ref is not None:
        for nom_scenario, reforme_scenario in dict_ref.items():
            TBS_Modified = DotationReform(TBS, reforme_scenario, PERIOD)
            dict_sims[nom_scenario] = simulation_from_dgcl_csv(PERIOD, DATA, TBS_Modified, data_last_year)
    # stockage des résulats dans un dataframe
    for nom_scenario, sim in dict_sims.items():
        for champ in to_compute_res:
            DATA[champ + "_" + nom_scenario] = sim.calculate(champ, PERIOD)
            if DATA[champ + "_" + nom_scenario].dtype == np.float32:
                DATA[champ + "_" + nom_scenario] = DATA[champ + "_" + nom_scenario].astype(np.float64)

    return DATA


if __name__ == "__main__":
    payload_example = {
        "dgf": {
            "dotation_solidarite_rurale": {
                "cible": {
                    "eligibilite": {
                        "seuil_classement": 23
                    }
                }
            }
        }
    }
    print(resultfromreforms({"amendement": payload_example}))

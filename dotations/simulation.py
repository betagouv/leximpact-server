from openfisca_core.simulation_builder import SimulationBuilder  # type: ignore
from dotations.load_dgcl_data import load_dgcl_file, adapt_dgcl_data  # type: ignore
# Actually runs the simulations
from openfisca_france_dotations_locales import CountryTaxBenefitSystem  # type: ignore
from dotations.reform import DotationReform  # type: ignore


code_comm = "Informations générales - Code INSEE de la commune"


def simulation_from_dgcl_csv(period, data, tbs, data_previous_year=None):
    sb = SimulationBuilder()
    sb.create_entities(tbs)
    sb.declare_person_entity("commune", data.index)
    simulation = sb.build(tbs)
    for champ_openfisca in data.columns:
        if " " not in champ_openfisca:  # oui c'est comme ça que je checke
            # qu'une variable es openfisca ne me jugez pas
            simulation.set_input(
                champ_openfisca,
                period,
                data[champ_openfisca],
            )
    # data_previous_year est un dataframe dont toutes les colonnes partent comme valeurs de l'an dernier.
    if data_previous_year is not None:
        data = data.merge(data_previous_year, on=code_comm, how='left', suffixes=["_currentyear", ""])
        for champ_openfisca in data_previous_year.columns:
            if " " not in champ_openfisca:  # oui c'est comme ça que je checke
                # qu'une variable es openfisca ne me jugez pas
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
    except FileNotFoundError:
        # Will work when app is launched from home folder (with make run, or in circleCI)
        DATA = adapt_dgcl_data(load_dgcl_file("assets/data/2019-communes-criteres-repartition.csv"))

    TBS = CountryTaxBenefitSystem()
    dict_sims = {"base": simulation_from_dgcl_csv(PERIOD, DATA, TBS)}
    # création d'un dictionnaire contenant une simulation par output
    if dict_ref is not None:
        for nom_scenario, reforme_scenario in dict_ref.items():
            TBS_Modified = DotationReform(TBS, reforme_scenario)
            dict_sims[nom_scenario] = simulation_from_dgcl_csv(PERIOD, DATA, TBS_Modified)
    # stockage des résulats dans un dataframe
    for nom_scenario, sim in dict_sims.items():
        for champ in to_compute_res:
            DATA[champ + "_" + nom_scenario] = sim.calculate(champ, PERIOD)
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

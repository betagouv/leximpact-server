from openfisca_core.simulation_builder import SimulationBuilder  # type: ignore
from load_dgcl_data import load_dgcl_file
# Actually runs the simulations
from openfisca_france_dotations_locales import CountryTaxBenefitSystem  # type: ignore
from reform import DotationReform


def simulation_from_dgcl_csv(period, data, tbs):
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
    return simulation


# outputte un dataframe qui contient :
# l'output normal de load_
# prend un dictionnaire de reformes (apres, eventuellement PLF)

def resultfromreforms(dict_ref=None, to_compute_res=("dsr_eligible_fraction_bourg_centre", "dsr_eligible_fraction_perequation", "dsr_eligible_fraction_cible")):
    PERIOD = "2020"
    # some of these can be preloaded in memory to improve performance.
    DATA = load_dgcl_file()
    TBS = CountryTaxBenefitSystem()
    dict_sims = {"avant": simulation_from_dgcl_csv(PERIOD, DATA, TBS)}
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
    print(resultfromreforms({"apres": payload_example}))

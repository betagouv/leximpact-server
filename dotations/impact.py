from pandas import DataFrame  # type: ignore


BORNES_STRATES = [0, 500, 2000, 5000, 10000, 20000, 50000, 100000, 1000000000000]  # bornes des strates en terme de POP INSEE


def get_cas_types_codes_insee():
    return ["76384", "76214"]  # sera paramétrable par l'usager


def build_response_dsr_cas_types(scenario, df_results, prefix_dsr_eligible, prefix_dsr_montant):
    # [scenario_api]["dotations"]["communes"]["dsr"]
    # > ["communes"]
    response = []
    code_comm = "Informations générales - Code INSEE de la commune"
    communes_cas_types = get_cas_types_codes_insee()
    for cas_type in communes_cas_types:
        res_cas_type = df_results[df_results[code_comm].astype(str) == cas_type]
        pop_cas_type = res_cas_type["population_insee"].values[0]
        cas_type_eligible = bool(res_cas_type[prefix_dsr_eligible + scenario].values[0])
        montant_dsr_cas_type = res_cas_type[prefix_dsr_montant + scenario].values[0]
        response += [{"code" : cas_type, "eligible": cas_type_eligible, "dotationParHab": float(montant_dsr_cas_type / pop_cas_type)}]

    return response


def build_response_dsr_eligibilites(scenario, df_results, prefix_dsr_eligible):
    # [scenario_api]["dotations"]["communes"]["dsr"]
    # > ["eligibles"]/["nouvellementEligibles"]/["plusEligibles"]
    response = {}

    response["eligibles"] = int(df_results[prefix_dsr_eligible + scenario].sum())
    if scenario != "base":
        response["nouvellementEligibles"] = len(df_results[(df_results[prefix_dsr_eligible + scenario]) & (~df_results[prefix_dsr_eligible + "base"])])
        response["plusEligibles"] = len(df_results[(~df_results[prefix_dsr_eligible + scenario]) & (df_results[prefix_dsr_eligible + "base"])])

    return response


def build_response_dsr_strates(scenario, df_results, prefix_dsr_eligible, prefix_dsr_montant):
    # [scenario_api]["dotations"]["communes"]["dsr"]
    # > ["strates"]

    # tableau nombre de communes éligibles par strate
    resultats_agreges_bornes = [{} for borne in BORNES_STRATES]

    # pour une borne, aggrège les résultats de toute la population
    # située au niveau supérieur ou égal à la borne
    for id_borne in range(len(BORNES_STRATES)):  # id borne : the borne identity
        borne = BORNES_STRATES[id_borne]
        df_strate = df_results[df_results["population_insee"] >= borne]
        resultats_agreges_bornes[id_borne]["population_insee"] = int(df_strate["population_insee"].sum())
        resultats_agreges_bornes[id_borne]["potentiel_financier"] = float(df_strate["potentiel_financier" + "_" + scenario].sum())
        resultats_agreges_bornes[id_borne]["eligibles_dsr"] = int(df_strate[prefix_dsr_eligible + scenario].sum())
        resultats_agreges_bornes[id_borne]["montant_dsr"] = int(df_strate[prefix_dsr_montant + scenario].sum())

    res_strates = [{} for borne in BORNES_STRATES[:-1]]
    for id_borne in range(len(BORNES_STRATES) - 1):
        res_strates[id_borne]["habitants"] = BORNES_STRATES[id_borne]
        pop_strate = resultats_agreges_bornes[id_borne]["population_insee"] - resultats_agreges_bornes[id_borne + 1]["population_insee"]
        res_strates[id_borne]["partPopTotale"] = pop_strate / resultats_agreges_bornes[0]["population_insee"]
        pot_strate = resultats_agreges_bornes[id_borne]["potentiel_financier"] - resultats_agreges_bornes[id_borne + 1]["potentiel_financier"]
        res_strates[id_borne]["potentielFinancierMoyenParHabitant"] = pot_strate / pop_strate
        nb_elig_strate = resultats_agreges_bornes[id_borne]["eligibles_dsr"] - resultats_agreges_bornes[id_borne + 1]["eligibles_dsr"]
        res_strates[id_borne]["eligibles"] = nb_elig_strate
        res_strates[id_borne]["dotationMoyenneParHab"] = (resultats_agreges_bornes[id_borne]["montant_dsr"] - resultats_agreges_bornes[id_borne + 1]["montant_dsr"]) / pop_strate
        res_strates[id_borne]["partDotationTotale"] = ((resultats_agreges_bornes[id_borne]["montant_dsr"] - resultats_agreges_bornes[id_borne + 1]["montant_dsr"]) / resultats_agreges_bornes[0]["montant_dsr"]) if resultats_agreges_bornes[0]["montant_dsr"] else 0

    return res_strates


def build_response_dsr(scenario: str, df_results: DataFrame, prefix_dsr_eligible: str, prefix_dsr_montant: str) -> dict:
    eligibilites = build_response_dsr_eligibilites(scenario, df_results, prefix_dsr_eligible)
    return {
        "communes": build_response_dsr_cas_types(scenario, df_results, prefix_dsr_eligible, prefix_dsr_montant),
        **eligibilites,
        "strates": build_response_dsr_strates(scenario, df_results, prefix_dsr_eligible, prefix_dsr_montant)
    }

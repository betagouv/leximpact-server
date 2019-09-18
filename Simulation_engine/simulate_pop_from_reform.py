from functools import partial
from typing import Dict, List, Optional
import os

import pandas  # type: ignore

from openfisca_core.memory_config import MemoryConfig  # type: ignore
from openfisca_core.simulation_builder import SimulationBuilder  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore
from models import from_postgres
from Simulation_engine.reforms import IncomeTaxReform
from Simulation_engine.reformePLF import reformePLF
from Simulation_engine.non_cached_variables import non_cached_variables
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

data_path = os.getenv("DATA_PATH")  # type: Optional[str]
# Config
version_beta_sans_simu_pop = False
adjust_results = True

# Types
Total = Dict[str, float]
Deciles = List[Dict[str, float]]


def load_data(filename: Optional[str]):
    if filename is None:
        filename = "DCT.csv"
    path = os.path.join(os.path.dirname(__file__), filename)
    if filename[-3:] == ".h5":
        return pandas.read_hdf(path)
    if "." in filename:
        return pandas.read_csv(path)
    return from_postgres(filename)


def simulation(period, data, tbs):
    # Traduction des roles attribués au format openfisca
    data["quimenof"] = "enfant"
    data.loc[data["quifoy"] == 1, "quimenof"] = "conjoint"
    data.loc[data["quifoy"] == 0, "quimenof"] = "personne_de_reference"

    data["quifoyof"] = "personne_a_charge"
    data.loc[data["quifoy"] == 1, "quifoyof"] = "conjoint"
    data.loc[data["quifoy"] == 0, "quifoyof"] = "declarant_principal"

    data["quifamof"] = "enfant"
    data.loc[data["quifam"] == 1, "quifamof"] = "conjoint"
    data.loc[data["quifam"] == 0, "quifamof"] = "demandeur"

    sb = SimulationBuilder()
    sb.create_entities(tbs)

    sb.declare_person_entity("individu", data.index)

    # Creates openfisca entities and generates grouped

    listentities = {"foy": "foyer_fiscal", "men": "menage", "fam": "famille"}

    instances = {}
    dictionnaire_datagrouped = {"individu": data}

    for ent, ofent in listentities.items():
        persons_ent = data["id" + ent].values
        persons_ent_roles = data["qui" + ent + "of"].values
        ent_ids = data["id" + ent].unique()
        instances[ofent] = sb.declare_entity(ofent, ent_ids)
        sb.join_with_persons(instances[ofent], persons_ent, roles=persons_ent_roles)

        # The following ssumes data defined for an entity are the same for all rows in
        # the same entity. Or at least that the first non null value found for an
        # entity will always be the total value for an entity (which is the case for
        # f4ba). These checks are performed in the checkdata function defined below.
        dictionnaire_datagrouped[ofent] = (
            data.groupby("id" + ent, as_index=False).first().sort_values(by="id" + ent)
        )

    # These variables should not be attributed to any OpenFisca Entity
    columns_not_OF_variables = set(
        [
            "idmen",
            "idfoy",
            "idfam",
            "noindiv",
            "level_0",
            "quifam",
            "quifoy",
            "quimen",
            "idmen_x",
            "idmen_y",
            "wprm",
            "index",
            "idmen_original",
            "idfoy_original",
            "idfam_original",
            "quifamof",
            "quifoyof",
            "quimenof",
        ]
    )

    simulation = sb.build(tbs)
    memory_config = MemoryConfig(
        max_memory_occupation=0.95,  # When 95% of the virtual memory is full, switch to disk storage
        priority_variables=["salary", "age"],  # Always store these variables in memory
        variables_to_drop=non_cached_variables,
    )
    simulation.memory_config = memory_config

    # Attribution des variables à la bonne entité OpenFisca
    for colonne in data.columns:
        if colonne not in columns_not_OF_variables:
            # try:
            simulation.set_input(
                colonne,
                period,
                dictionnaire_datagrouped[tbs.get_variable(colonne).entity.key][colonne],
            )
    return simulation, dictionnaire_datagrouped


def compare(period: str, dictionnaire_simulations, compute_deciles=True):
    res: Total = {}
    if (
        "avant" not in dictionnaire_simulations
    ):  # Veut dire qu'on ne demande pas le calcul du avant
        # Donc il doit déjà être dans resulats_de_base
        impots_par_reforme = resultats_de_base.copy()
    else:
        impots_par_reforme = next(iter(dictionnaire_simulations.values()))[1][
            "foyer_fiscal"
        ][["wprm"]]
    for nom_simulation in dictionnaire_simulations:
        impots_par_reforme[nom_simulation] = dictionnaire_simulations[nom_simulation][
            0
        ].calculate("irpp", period)
    for nom_res_base in [
        colonne_df for colonne_df in impots_par_reforme.columns if colonne_df != "wprm"
    ]:
        res[nom_res_base] = -(
            impots_par_reforme[nom_res_base] * impots_par_reforme["wprm"]
        ).sum()
    total: Total = res
    if compute_deciles:
        # On rajoute "avant"  et "plf" à la liste des colonnes sur lesquelles calculer les déciles,
        # On en a besoin si ces colonnes ne sont pas déjà dans le dictionnaire_simulations (par exemple
        # dans le cas d'un compare avec isdecile = True)
        noms_simus = list(set(dictionnaire_simulations.keys()) | set(["avant", "plf"]))
        totweight = impots_par_reforme["wprm"].sum()
        nbd = 10
        decilweights = [i / nbd * totweight for i in range(nbd + 1)]
        numdecile = 1
        impots_par_reforme["keysort"] = (
            -impots_par_reforme["avant"] - impots_par_reforme["apres"]
        )
        impots_par_reforme = impots_par_reforme.sort_values(
            by="keysort"
        )  # For now, deciles are organized by level of irpp
        running_sum_weights = 0
        running_sums_irpp = {nom_sim: 0 for nom_sim in noms_simus}
        decilesres = [[0] * (1 + len(noms_simus))]
        decdiffres: Deciles = []
        eps = 0.0001
        keysdicres = ["poids"] + noms_simus
        for _index_row, row in impots_par_reforme.iterrows():
            running_sum_weights += row["wprm"]
            for nom_simu in noms_simus:
                running_sums_irpp[nom_simu] -= row[nom_simu] * row["wprm"]
            if running_sum_weights >= decilweights[numdecile] - eps:
                decilesres += [
                    [running_sum_weights] + [running_sums_irpp[ns] for ns in noms_simus]
                ]
                decdiffres += [
                    {
                        keysdicres[k]: decilesres[numdecile][k]
                        - decilesres[numdecile - 1][k]
                        for k in range(len(keysdicres))
                    }
                ]
                numdecile += 1

        # TODO : interpolate quantiles instead of doing the granular approach
        # This is the only TODO part in this code, I highly doubt it's the most pressing matter

        if adjust_results:
            # empiric = valeur de base sur laquelle calibrer (pour prendre en compte, par
            # exemple les crédits d'impôts. Représente le montant total d'IR récolté l'année
            #  prochaine dans le scénario "avant" (i.e. avec le code existant))
            empiric = 73 * 10 ** 9
            factor = adjustment(empiric, total["avant"])
            total = adjust_total(factor, total)
            deciles: Deciles = adjust_deciles(factor, decdiffres)
        else:
            deciles = decdiffres

        resultat = {"total": total, "deciles": deciles}

    else:  # This only interests us for the castypes
        # On arrondit les résultats des cas-types
        dic_res_brut = impots_par_reforme.to_dict()
        for simu in dic_res_brut:
            for cas_type in dic_res_brut[simu]:
                dic_res_brut[simu][cas_type] = int(round(dic_res_brut[simu][cas_type]))
        resultat = {"total": total, "res_brut": dic_res_brut}

    return resultat


def adjustment(empiric: int, baseline: float):
    """Facteur d'ajustement à partir d'un benchmark empirique"""
    return empiric / baseline


def adjust_total(factor: int, total: dict):
    """
    Le résultat avant sera ajusté à resultBase, tout sera ajusté d'un facteur

    C'est pour permettre d'obtenir des résultats réalistes sans données.
    Pour la faire classe, on calibre le modèle sur un paramètre (facteur d'ajustement de l'impot de chacun)
    Pour minimiser un vecteur d'erreur qui ne contient qu'un paramètre (montant global des recettes de l'Etat)
    """
    return {key: value * factor for (key, value) in total.items()}


def adjust_deciles(factor: int, deciles: List[dict]):
    """
    Le résultat avant sera ajusté à resultBase, tout sera ajusté d'un facteur

    C'est pour permettre d'obtenir des résultats réalistes sans données.
    Pour la faire classe, on calibre le modèle sur un paramètre (facteur d'ajustement de l'impot de chacun)
    Pour minimiser un vecteur d'erreur qui ne contient qu'un paramètre (montant global des recettes de l'Etat)
    """
    return [adjust_total(factor, decile) for decile in deciles]


# Inversion des fonctions net to brut


def calcule_maillage_intervalle(
    nom_colonne, minv, maxv, pourcentage_hausse, valeur_hausse
):
    """
    Crée un dataframe d'une colonne portant le nom nom_colonne
    et contenant une progression entre [minv, maxv].
    """
    arr = []
    s = minv
    num_foy = 0
    while s <= maxv:
        arr += [[s] + [num_foy] * 3 + [0] * 3]
        # suite récurrente définissant l'évolution de l'estimation de nom_colonne
        s = max(s + valeur_hausse, s * (1 + pourcentage_hausse))
        num_foy += 1
    df = pandas.DataFrame(
        arr,
        columns=[nom_colonne, "idfam", "idfoy", "idmen", "quifam", "quifoy", "quimen"],
    )
    return df


def scenar_values(
    minv, maxv, var_brute, var_nette, pourcentage_hausse=0.01, valeur_hausse=100
):
    """
    Calcule les valeurs de var_nette pour var_brute dans [minv, maxv]
    et exporte dans un CSV avec les colonnes suivantes : var_brute,var_nette
    """
    if "{}_to_{}.csv".format(var_brute, var_nette) not in os.listdir():
        df = calcule_maillage_intervalle(
            var_brute, minv, maxv, pourcentage_hausse, valeur_hausse
        )
        PERIOD = "2018"
        TBS = FranceTaxBenefitSystem()
        # définit un ménage par ligne
        sim = simulation(PERIOD, df, TBS)
        net = var_nette
        df[net] = sim[0].calculate(net, "2018-01") * 12
        df[[var_brute, var_nette]].to_csv(
            "{}_to_{}.csv".format(var_brute, var_nette), index=False
        )


def from_net_to_brut(val_nette, var_brute, var_nette):
    namecsv = "{}_to_{}.csv".format(var_brute, var_nette)
    df = pandas.read_csv(namecsv)
    dfv = df.values
    N = len(dfv)
    tt = 1
    while tt < N:
        tt <<= 1
    bestsol = -1
    while tt:
        if (bestsol + tt) < N and dfv[bestsol + tt][1] < val_nette:
            bestsol += tt
        tt >>= 1
    if bestsol < 0:
        bestsol = 0
    if bestsol == N - 1:
        bestsol = N - 2
    # bestsolis the index of the highest value before val_nette
    # We extrapolate a linear function on (bestsol, bestsol +1)
    avanty = dfv[bestsol][1]
    apresy = dfv[bestsol + 1][1]
    avantx = dfv[bestsol][0]
    apresx = dfv[bestsol + 1][0]
    lambda_ = (val_nette - avanty) / (apresy - avanty)
    return lambda_ * apresx + (1 - lambda_) * avantx


def from_brut_to_net(val_brute, var_brute, var_nette):
    namecsv = "{}_to_{}.csv".format(var_brute, var_nette)
    df = pandas.read_csv(namecsv)
    dfv = df.values
    N = len(dfv)
    tt = 1
    while tt < N:
        tt <<= 1
    bestsol = -1
    while tt:
        if (bestsol + tt) < N and dfv[bestsol + tt][0] < val_brute:
            bestsol += tt
        tt >>= 1
    if bestsol < 0:
        bestsol = 0
    if bestsol == N - 1:
        bestsol = N - 2
    avanty = dfv[bestsol][0]
    apresy = dfv[bestsol + 1][0]
    avantx = dfv[bestsol][1]
    apresx = dfv[bestsol + 1][1]
    lambda_ = (val_brute - avanty) / (apresy - avanty)
    return lambda_ * apresx + (1 - lambda_) * avantx


scenar_values(0, 12_000_000, "salaire_de_base", "salaire_imposable")
scenar_values(0, 12_000_000, "retraite_brute", "retraite_imposable")


PERIOD = "2018"
TBS = FranceTaxBenefitSystem()
TBS_PLF = IncomeTaxReform(TBS, reformePLF, PERIOD)
CAS_TYPE = load_data("DCT.csv")
SIMCAT = partial(simulation, period=PERIOD, data=CAS_TYPE)
SIMCAT_BASE = SIMCAT(tbs=TBS)


if not version_beta_sans_simu_pop:
    # Initialisation des données utilisées pour le calcul sur la population
    DUMMY_DATA = load_data(data_path)
    print("Dummy Data loaded", len(DUMMY_DATA), "lines")
    # Resultats sur la population du code existant et du PLF. Ne change jamais donc pas besoin de fatiguer l'ordi à calculer
    # Test à implémenter : si les résultats de base sont là, ils correspondent aux résultats qu'on calculerait
    # sur le data_path
    resultats_de_base = from_postgres("base_results")
    if (
        resultats_de_base is not None
    ):  # Si la table n'existe pas dans le schéma SQL, ce sera None et on les calcule nous même
        resultats_de_base = resultats_de_base.set_index("idfoy")
    else:
        simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS)
        resultats_de_base = simulation_base_deciles[1]["foyer_fiscal"][["wprm"]]
        # precalcul cas de base sur la population pour le cache
        resultats_de_base["avant"] = simulation_base_deciles[0].calculate(
            "irpp", PERIOD
        )
        simulation_plf_deciles = simulation(PERIOD, DUMMY_DATA, TBS_PLF)
        resultats_de_base["plf"] = simulation_plf_deciles[0].calculate("irpp", PERIOD)

simulation_base_castypes = simulation(PERIOD, CAS_TYPE, TBS)
simulation_plf_castypes = simulation(PERIOD, CAS_TYPE, TBS_PLF)


def foyertosomethingelse(idfoy):
    return "oui j'ai un foyer son numero est {}".format(idfoy)


def foyertotexte(idfoy, data=None):
    if data is None:
        data = CAS_TYPE
    myct = data[data["idfoy"] == idfoy]
    decl = myct[myct["quifoyof"] == "declarant_principal"]
    nbdecl = len(decl)
    nbpacs = len(myct) - nbdecl
    pacs = myct[myct["quifoyof"] != "declarant_principal"]
    agedecl = sorted(decl["age"].values, reverse=True)
    agepacs = sorted(pacs["age"].values, reverse=True)
    revenu = myct["salaire_de_base"].sum()
    return "\n".join(
        [
            "{} déclarant{}, d'âge {}".format(
                nbdecl,
                "s" if nbdecl > 1 else "",
                " et ".join([str(_) for _ in agedecl]),
            )
        ]
        + (
            [
                "{} personne{} à charge, d'âge {}".format(
                    nbpacs,
                    "s" if nbpacs > 1 else "",
                    " et ".join([str(_) for _ in agepacs]),
                )
            ]
            if nbpacs
            else []
        )
        + ["revenu total du FF : {}".format(revenu)]
    )


def foyertorevenu(idfoy, data=None):
    if data is None:
        data = CAS_TYPE
    revenu = (
        data[data["idfoy"] == idfoy]["salaire_de_base"].sum()
        + data[data["idfoy"] == idfoy]["retraite_brute"].sum()
    )
    return revenu


def foyertodictcastype(idfoy, data=None):
    if data is None:
        data = CAS_TYPE
    revenu = sum(
        [
            from_brut_to_net(sb, "salaire_de_base", "salaire_imposable")
            for sb in data[data["idfoy"] == idfoy]["salaire_de_base"].values
        ]
        + [
            from_brut_to_net(rb, "retraite_brute", "retraite_imposable")
            for rb in data[data["idfoy"] == idfoy]["retraite_brute"].values
        ]
    )
    nbpr = len(data[(data["idfoy"] == idfoy) & (data["quifoy"] <= 1)])
    nbpac = len(data[(data["idfoy"] == idfoy) & (data["quifoy"] > 1)])
    nbret = len(data[(data["idfoy"] == idfoy) & (data["retraite_brute"] > 0)])
    # Si un retraite et l'autre n'a pas de revenu, on compte les 2.
    if nbret:
        nbret = len(
            data[
                (data["idfoy"] == idfoy)
                & (
                    (data["retraite_brute"] > 0)
                    | ((data["salaire_de_base"] < 1) & (data["age"] >= 65))
                )
            ]
        )

    outremer1 = (
        len(data[(data["idfoy"] == idfoy) & (data["residence_fiscale_guadeloupe"])]) > 0
    )
    outremer2 = (
        len(data[(data["idfoy"] == idfoy) & (data["residence_fiscale_guyane"])]) > 0
    )
    assert not (outremer1 * outremer2)

    nb_decl_parent_isole = (
        1
        if (
            nbpr == 1
            and (
                (
                    "caseL" in data
                    and len(data[(data["idfoy"] == idfoy) & (data["caseL"])])
                )
                or (
                    "caseT" in data
                    and len(data[(data["idfoy"] == idfoy) & (data["caseT"])])
                )
            )
        )
        else 0
    )
    nbveuf = len(data[(data["idfoy"] == idfoy) & (data["statut_marital"] == 4)])
    nb_decl_invalides = (
        len(data[(data["idfoy"] == idfoy) & (data["quifoy"] <= 1) & (data["invalide"])])
        if "invalide" in data
        else 0
    )
    nb_pac_invalides = (
        len(data[(data["idfoy"] == idfoy) & (data["quifoy"] > 1) & (data["invalide"])])
        if "invalide" in data
        else 0
    )
    nb_anciens_combattants = (
        1
        if ("caseW" in data and len(data[(data["idfoy"] == idfoy) & (data["caseW"])]))
        else 0
    )
    nb_pac_charge_partagee = (
        len(data[(data["idfoy"] == idfoy) & (data["charge_alternee"])])
        if "charge_alternee" in data
        else 0
    )

    dicres = {
        "revenu": int(round(revenu)),
        "nombre_declarants": int(nbpr),
        "nombre_personnes_a_charge": int(nbpac),
        "nombre_declarants_retraites": int(nbret),
        "outre_mer": 1 * outremer1 + 2 * outremer2,
        "nb_decl_veuf": nbveuf,
        "nb_decl_parent_isole": nb_decl_parent_isole,
        "nb_decl_invalides": nb_decl_invalides,
        "nb_pac_invalides": nb_pac_invalides,
        "nb_anciens_combattants": nb_anciens_combattants,
        "nb_pac_charge_partagee": nb_pac_charge_partagee,
    }
    return dicres


def revenus_cas_types(data=None):
    if data is None:
        data = CAS_TYPE
    dic_res = {}
    for k in data["idfoy"].values:
        dic_res[k] = foyertorevenu(k, data)
    return dic_res


def desc_cas_types(data=None):
    if data is None:
        data = CAS_TYPE
    listfoyers = sorted(list(set(data["idfoy"].values)))
    return [foyertodictcastype(k, data) for k in listfoyers]


def texte_cas_types(data=None):
    if data is None:
        data = CAS_TYPE
    dic_res = {}
    for k in data["idfoy"].values:
        dic_res[k] = foyertotexte(k, data)
    return dic_res


def simulation_from_cas_types(descriptions):
    df = dataframe_from_cas_types_description(descriptions)
    return (df, simulation(PERIOD, df, TBS), simulation(PERIOD, df, TBS_PLF))


# Transforme une description de cas types en un dataframe parsable. Good luck!
def dataframe_from_cas_types_description(descriptions):
    cols = [
        "index",
        "activite",
        "age",
        "categorie_salarie",
        "chomage_brut",
        "chomage_imposable",
        "contrat_de_travail",
        "date_naissance",
        "effectif_entreprise",
        "heures_remunerees_volume",
        "idfam",
        "idfoy",
        "idmen",
        "pensions_alimentaires_percues",
        "quifam",
        "quifoy",
        "quimen",
        "rag",
        "retraite_brute",
        "ric",
        "rnc",
        "statut_marital",
        "salaire_de_base",
        "taux_csg_remplacement",
        "f4ba",
        "loyer",
        "statut_occupation_logement",
        "taxe_habitation",
        "wprm",
        "zone_apl",
        "quimenof",
        "residence_fiscale_guadeloupe",
        "residence_fiscale_guyane",
        "quifoyof",
        "quifamof",
        "caseL",
        "caseT",
        "caseW",
        "garde_alternee",
        "invalidite",
    ]

    # liste des cols valant 0
    zerocols = [
        "chomage_brut",
        "chomage_imposable",
        "effectif_entreprise",
        "effectif_entreprise",
        "pensions_alimentaires_percues",
        "rag",
        "ric",
        "rnc",
        "f4ba",
        "loyer",
        "statut_occupation_logement",
        "taxe_habitation",
    ]
    othercolsfixes = {
        "wprm": 1,
        "zone_apl": 2,
        "taux_csg_remplacement": "taux_plein",
    }  # nom de colonne : valeur fixe

    for k in zerocols:
        othercolsfixes[k] = 0

    colbinaires = {
        "categorie_salarie": (0, 7, 7),
        "age": (60, 15, 78),
        "date_naissance": ("1958-05-10", "2005-03-10", "1940-06-18"),
    }  # nom de colonne : (valeur_adulte, valeur_enfant,valeur_retraite)

    for k in othercolsfixes:
        colbinaires[k] = (othercolsfixes[k], othercolsfixes[k], othercolsfixes[k])

    dres = {}  # keys = the columns
    for c in cols:
        dres[c] = []
    isretraite = (
        []
    )  # vecteur nous informant si le ff est "retraité", i.e. plus de 65 ans. On mettra aussi le revenu
    # en "retraite brute"

    # Si le dico est à l'ancien format, on l'accepte quand même, tout le monde est bienvenu chez nous

    valeurs_zero_si_absentes = [
        "nb_decl_parent_isole",
        "nb_decl_veuf",
        "nb_decl_invalides",
        "nb_pac_invalides",
        "nb_anciens_combattants",
        "nb_pac_charge_partagee",
    ]

    indexfoyer = 0
    indexpac = 2
    for ct in descriptions:
        for to_zero in valeurs_zero_si_absentes:
            if to_zero not in ct:
                ct[to_zero] = 0
        nbd = ct["nombre_declarants"]
        nbc = ct["nombre_personnes_a_charge"]
        for colid in ["idfoy", "idmen", "idfam"]:
            dres[colid] += [indexfoyer] * (nbd + nbc)
        for colqui in ["quifoy", "quimen", "quifam"]:
            dres[colqui] += list(range(nbd)) + list(range(indexpac, indexpac + nbc))
        dres["quimenof"] += (
            ["personne_de_reference"] * min(1, nbd)
            + ["conjoint"] * (max(0, min(1, nbd - 1)))
            + ["enfant"] * nbc
        )
        dres["quifamof"] += (
            ["demandeur"] * min(1, nbd)
            + ["conjoint"] * (max(0, min(1, nbd - 1)))
            + ["enfant"] * nbc
        )
        dres["quifoyof"] += (
            ["declarant_principal"] * min(1, nbd)
            + ["conjoint"] * (max(0, min(1, nbd - 1)))
            + ["enfant"] * nbc
        )
        indexpac += nbc
        dres["residence_fiscale_guadeloupe"] += [ct["outre_mer"] == 1] * (nbd + nbc)
        dres["residence_fiscale_guyane"] += [ct["outre_mer"] == 2] * (nbd + nbc)

        # Ces variables s'appliquent au foyer fiscal. On applique donc la valeur à tout le cas type
        dres["caseT"] += [1 if ct["nb_decl_parent_isole"] and nbc else 0] * (nbd + nbc)
        dres["caseL"] += [1 if ct["nb_decl_parent_isole"] and not nbc else 0] * (
            nbd + nbc
        )
        dres["caseW"] += [1 if ct["nb_anciens_combattants"] else 0] * (nbd + nbc)

        # separe le revenu en 2 si il y a 2 déclarants:
        if ct["nombre_declarants_retraites"] == nbd:
            dres["retraite_brute"] += [
                from_net_to_brut(
                    ct["revenu"] / nbd, "retraite_brute", "retraite_imposable"
                )
            ] * nbd + [0] * nbc
            dres["salaire_de_base"] += [0] * (nbd + nbc)
            isretraite += [1] * (nbd) + [0] * (nbc)
        elif ct["nombre_declarants_retraites"] == 1 and nbd == 2:
            # On décrète que le retraité, c'est le 2ème !
            dres["retraite_brute"] += (
                [0]
                + [
                    from_net_to_brut(
                        ct["revenu"] / nbd, "retraite_brute", "retraite_imposable"
                    )
                ]
                + [0] * nbc
            )
            dres["salaire_de_base"] += (
                [
                    from_net_to_brut(
                        ct["revenu"] / nbd, "salaire_de_base", "salaire_imposable"
                    )
                ]
                + [0]
                + [0] * (nbc)
            )
            isretraite += [0] + [1] + [0] * (nbc)
        else:
            isretraite += [0] * (nbd + nbc)
            dres["salaire_de_base"] += [
                from_net_to_brut(
                    ct["revenu"] / nbd, "salaire_de_base", "salaire_imposable"
                )
            ] * nbd + [0] * nbc
            dres["retraite_brute"] += [0] * (nbd + nbc)
        indexfoyer += 1

        dres["invalidite"] += [
            1 if id_declarant < ct["nb_decl_invalides"] else 0
            for id_declarant in range(nbd)
        ] + [1 if id_pac < ct["nb_pac_invalides"] else 0 for id_pac in range(nbc)]
        # TODO : be able to choose if garde_alternee personnes_a_charges are also the ones with invalidite or not
        dres["garde_alternee"] += [0] * nbd + [
            1 if id_pac < ct["nb_pac_invalides"] else 0 for id_pac in range(nbc)
        ]

        for _ in range(nbd):
            dres["activite"] += [0] if not ct["nombre_declarants_retraites"] else [3]
            dres["contrat_de_travail"] += (
                [0] if not ct["nombre_declarants_retraites"] else [6]
            )
            dres["heures_remunerees_volume"] += (
                [1200] if not ct["nombre_declarants_retraites"] else [0]
            )
            dres["statut_marital"] += (
                [4 if ct["nb_decl_veuf"] else 5] if nbd > 1 else [2]
            )
        for _ in range(nbc):
            dres["activite"] += [2]
            dres["contrat_de_travail"] += [6]
            dres["heures_remunerees_volume"] += [0]
            dres["statut_marital"] += [2]
    dres["index"] = list(range(len(dres["quifoy"])))
    for col, v in colbinaires.items():
        dres[col] = [
            v[2]
            if k[1]
            else (v[0] if k[0] in ("personne_de_reference", "conjoint") else v[1])
            for k in zip(dres["quimenof"], isretraite)
        ]
    df = pandas.DataFrame.from_dict(dres)
    return df


def CompareOldNew(taux=None, isdecile=True, dictreform=None, castypedesc=None):
    # if isdecile, we want the impact on the full population, while just a cas type on
    # the isdecile=False

    if isdecile:
        data = DUMMY_DATA
        reform = IncomeTaxReform(TBS, dictreform, PERIOD)
        simulation_reform = simulation(PERIOD, data, reform)
        return compare(PERIOD, {"apres": simulation_reform}, isdecile)

    data, simulation_base, simulation_plf = (
        (CAS_TYPE, simulation_base_castypes, simulation_plf_castypes)
        if castypedesc is None
        else simulation_from_cas_types(castypedesc)
    )
    reform = IncomeTaxReform(TBS, dictreform, PERIOD)
    simulation_reform = simulation(PERIOD, data, reform)

    if dictreform is None:
        assert taux is not None
        dictreform = {
            "impot_revenu": {
                "bareme": {
                    "seuils": [0] + taux[: len(taux) // 2],
                    "taux": [0.0] + taux[len(taux) // 2 :],
                }
            }
        }
    return compare(
        PERIOD,
        {"avant": simulation_base, "plf": simulation_plf, "apres": simulation_reform},
        isdecile,
    )

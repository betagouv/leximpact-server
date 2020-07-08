from typing import Any, Dict, List, Optional
import os
import re
import pandas  # type: ignore
import logging

from openfisca_core.memory_config import MemoryConfig  # type: ignore
from openfisca_core.simulation_builder import SimulationBuilder  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore
from models import from_postgres
from Simulation_engine.reforms import IncomeTaxReform
from Simulation_engine.non_cached_variables import non_cached_variables
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# Config
data_path = os.getenv("POPULATION_TABLE_PATH")  # type: Optional[str]
nom_table_resultats_base = os.getenv("NAME_TABLE_BASE_RESULT")  # type: Optional[str]
if nom_table_resultats_base is None:
    nom_table_resultats_base = "base_results"

version_beta_sans_simu_pop = (
    data_path is None
)  # Si POPULATION_TABLE_PATH n'est pas renseigné dans .env, on lance sans simpop

#  PARTIE CONFIGURABLE PAR L'UTILISATEUR

# Decrit les réformes renvoyées par défaut.
# Vide en l'absence de PLF, si un PLF survient on peut le renseigner
# Toutes les requêtes renvoient un résultat "avant" (code existant),
# un résultat "apres" (reforme renseignée dans la requete)
# et un résultat par réforme présente dans reformes_par_defaut
reformes_par_defaut: Dict[str, Dict] = {}

# On verifie dans la variable d'environnement PLF_PATH si on doit inclure le PLF ou pas.
reforme_adresse = os.getenv("PLF_PATH")
# Ce reforme path doit contenir le path vers une librairie python qui contient un dictionnaire au bon format.
if reforme_adresse is not None:
    regex_secu = re.compile(r"^[^\s;]*$")
    if regex_secu.match(reforme_adresse) is None:
        logging.error(
            "Votre variable d'environnement PLF_PATH contient des ; ou des caractères vides. Elle n'a pas le droit. Nommez vos fichiers normalement s'il vous plaît. Bisous."
        )
        raise ImportError
    elements = reforme_adresse.split(".")
    origine_import = ".".join(elements[:-1])
    nom_dic_import = elements[-1]
    reforme_PLF: Dict[
        Any, Any
    ] = {}  # Declare une valeur par défaut, la valeur arrivant par des moyens détournés que le linter ne peut voir
    try:
        exec("from {} import {} as reforme_PLF".format(origine_import, nom_dic_import))
    except (ImportError, ModuleNotFoundError, SyntaxError) as e:
        logging.error(
            "Si la variable PLF_PATH est renseignée, elle doit contenir un chemin\
            valide vers un dictionnaire présentant la réforme. PLF_PATH renseigné\
            : {}".format(reforme_adresse)
        )
        raise e
    reformes_par_defaut["plf"] = reforme_PLF

# Année sur la législation de laquelle les calculs seront menés.
annee_de_calcul = os.getenv("YEAR_COMPUTATION")

# FIN DE LA PARTIE CONFIGURABLE PAR L'UTILISATEUR

# liste_noms_reformes_sans_apres contient les noms de réformes hormis celle demandée par l'usager :
liste_noms_reformes_sans_apres = sorted(list(reformes_par_defaut.keys()) + ["avant"])
# liste_noms_reformes_avec_apres contient les noms de réformes incluant celle demandée par l'usager :
liste_noms_reformes_avec_apres = liste_noms_reformes_sans_apres + ["apres"]


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


def calcule_personnes_touchees(impots_par_reforme):
    # On fait tous les passages possibles entre les resultats:
    simus_passages = liste_noms_reformes_avec_apres
    transcription_code = ["neutre", "gagnant", "perdant_zero", "neutre_zero", "perdant"]
    foyers_fiscaux_touches: Dict[str, Dict[str, int]] = {}
    IMPOT_DIMINUE = 1
    IMPOT_INCHANGE = 0
    IMPOT_AUGMENTE = -1
    IMPOT_NUL_DELTA = -2

    for id_comp_1 in range(len(simus_passages)):
        nom_comp_1 = simus_passages[id_comp_1]
        for id_comp_2 in range(id_comp_1 + 1, len(simus_passages)):
            nom_comp_2 = simus_passages[id_comp_2]
            nom_colonne_affectation = "{}_to_{}".format(nom_comp_1, nom_comp_2)
            foyers_fiscaux_touches[nom_colonne_affectation] = {}
            impots_par_reforme[nom_colonne_affectation] = IMPOT_INCHANGE
            impots_par_reforme.loc[
                (impots_par_reforme[nom_comp_1] - 0.1 > impots_par_reforme[nom_comp_2]),
                nom_colonne_affectation,
            ] = IMPOT_AUGMENTE
            impots_par_reforme.loc[
                (impots_par_reforme[nom_comp_1] + 0.1 < impots_par_reforme[nom_comp_2]),
                nom_colonne_affectation,
            ] = IMPOT_DIMINUE
            impots_par_reforme.loc[
                (impots_par_reforme[nom_comp_1]) > -0.01, nom_colonne_affectation
            ] = (impots_par_reforme[nom_colonne_affectation] + IMPOT_NUL_DELTA)
            # Ca nous amene à : -3 si (avant=0, plf !=0),
            # -2 si (avant=0, plf=0), -1 si (avant!=0 et perdant),
            # 0 si (avant!=0 et ni gagnant ni perdant), 1 si (avant!=0 et gagnant)
            # Oui, c'est ca que ca veut dire le transcription_code
            compte_code_affectation = (
                impots_par_reforme.groupby(nom_colonne_affectation)[["wprm"]]
                .sum()
                .to_dict()["wprm"]
            )
            for code, somme_poids_code in compte_code_affectation.items():
                foyers_fiscaux_touches[nom_colonne_affectation][
                    transcription_code[code]
                ] = round(somme_poids_code)

    return foyers_fiscaux_touches


def dataframe_pondere(dictionnaire_simulations: Dict) -> pandas.DataFrame:
    # Pondération des foyers fiscaux : une ligne par foyer fiscal, une colonne pour le poids (wprm)
    return next(iter(dictionnaire_simulations.values()))[1]["foyer_fiscal"][["wprm"]]


def compare(period: str, dictionnaire_simulations, compute_deciles=True):
    res: Total = {}
    if (
        "avant" not in dictionnaire_simulations
    ):  # Veut dire qu'on ne demande pas le calcul du avant
        # Donc il doit déjà être dans resulats_de_base
        impots_par_reforme = resultats_de_base.copy()
    else:
        impots_par_reforme = dataframe_pondere(dictionnaire_simulations)
    nbptr_par_reforme = dataframe_pondere(dictionnaire_simulations)
    for nom_simulation in dictionnaire_simulations:
        impots_par_reforme[nom_simulation] = dictionnaire_simulations[nom_simulation][
            0
        ].calculate("irpp", period)
        if compute_deciles:
            impots_par_reforme["rfr"] = dictionnaire_simulations[nom_simulation][
                0
            ].calculate("rfr", period)
        else:  # Evitons de calculer le nbptr quand on fait toute la population
            nbptr_par_reforme[nom_simulation] = dictionnaire_simulations[nom_simulation][
                0
            ].calculate("nbptr", period)

    for nom_res_base in liste_noms_reformes_avec_apres:
        res[nom_res_base] = -(
            impots_par_reforme[nom_res_base] * impots_par_reforme["wprm"]
        ).sum()
    total: Total = res
    if compute_deciles:
        # On rajoute les simulations par défaut à la liste des colonnes sur lesquelles calculer les déciles,
        # On en a besoin si ces colonnes ne sont pas déjà dans le dictionnaire_simulations (par exemple
        # dans le cas d'un compare avec isdecile = True)
        frontieres_deciles: List[float] = []
        noms_simus = list(
            set(dictionnaire_simulations.keys()) | set(liste_noms_reformes_sans_apres)
        )
        totweight = impots_par_reforme["wprm"].sum()
        nbd = 10
        decilweights = [i / nbd * totweight for i in range(nbd + 1)]
        numdecile = 1
        impots_par_reforme["keysort"] = impots_par_reforme["rfr"]
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
                frontieres_deciles += [row["keysort"]]
                numdecile += 1

        # TODO : interpolate quantiles instead of doing the granular approach
        # This is the only TODO part in this code, I highly doubt it's the most pressing matter
        if os.getenv("RECETTES_ETAT_EURO") is not None:
            # empiric = valeur de base sur laquelle calibrer (pour prendre en compte, par
            # exemple les crédits d'impôts. Représente le montant total d'IR récolté l'année
            # prochaine dans le scénario "avant" (i.e. avec le code existant)).
            empiric = int(os.getenv("RECETTES_ETAT_EURO"))  # type: ignore
            factor = adjustment(empiric, total)
            total = adjust_total(factor, total)
            deciles: Deciles = adjust_deciles(factor, decdiffres)
        else:
            deciles = decdiffres

        foyers_fiscaux_touches = calcule_personnes_touchees(impots_par_reforme)
        resultat = {
            "total": total,
            "deciles": deciles,
            "frontieres_deciles": frontieres_deciles,
            "foyers_fiscaux_touches": foyers_fiscaux_touches,
        }

    else:  # This only interests us for the castypes
        # On arrondit les résultats des cas-types
        dic_res_brut = impots_par_reforme.to_dict()
        del dic_res_brut["wprm"]
        for simu in dic_res_brut:
            for cas_type in dic_res_brut[simu]:
                dic_res_brut[simu][cas_type] = int(round(dic_res_brut[simu][cas_type]))
        dic_nbptr = nbptr_par_reforme.to_dict()
        del dic_nbptr["wprm"]
        resultat = {"total": total, "res_brut": dic_res_brut, "nbreParts": dic_nbptr}

    return resultat


def adjustment(empiric: int, brute_result: dict):
    baseline_result = brute_result["avant"]
    """Facteur d'ajustement à partir d'un benchmark empirique :
    soit r_b le calcul du code existant, et e_b la valeur empirique des recettes de l'état,
    le resultat ajusté est calculé comme :
    adjusted_result[nom_reforme] = e_b/r_b  si nom_reforme =="avant"
    adjusted_result[nom_reforme] = e_b/r_b  si brute_result[nom_reforme] > 0.95 * r_b
    si brute_result[nom_reforme] < 0.95 * r_b, on applique le même taux d'ajustement que pour
    brute_result[nom_reforme] == 0.95 * r_b, soit  (e_b - 0.05 * r-b) / (0.95 * r_b)
    """
    adj_lim = 0.9
    return {
        key: ((empiric + brute_result[key] - baseline_result) / brute_result[key])
        if (brute_result[key] - baseline_result) / baseline_result > -(1 - adj_lim)
        else (empiric - (1 - adj_lim) * baseline_result) / (adj_lim * baseline_result)
        for key in brute_result
    }


def adjust_total(factor: dict, total: dict, ignore_keys: Optional[List[str]] = None):
    """
    Le résultat avant sera ajusté à resultBase, tout sera ajusté d'un facteur

    C'est pour permettre d'obtenir des résultats réalistes sans données.
    Pour la faire classe, on calibre le modèle sur un paramètre
    (facteur d'ajustement de l'impôt de chacun des ménages).
    """
    if ignore_keys is None:
        ignore_keys = ["poids"]
    return {
        key: value * (factor[key] if key not in ignore_keys else 1)
        for (key, value) in total.items()
    }


def adjust_deciles(factor: dict, deciles: List[dict]):
    """
    Le résultat avant sera ajusté à resultBase, tout sera ajusté d'un facteur

    C'est pour permettre d'obtenir des résultats réalistes sans données.
    Pour la faire classe, on calibre le modèle sur un paramètre
    (facteur d'ajustement de l'impôt de chacun des ménages).
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
    minv, maxv, var_brute, var_nette, pourcentage_hausse=0.001, valeur_hausse=100
):
    """
    Calcule les valeurs de var_nette pour var_brute dans [minv, maxv]
    et exporte dans un CSV avec les colonnes suivantes : var_brute,var_nette
    """
    df = calcule_maillage_intervalle(
        var_brute, minv, maxv, pourcentage_hausse, valeur_hausse
    )
    PERIOD = str(annee_de_calcul)
    TBS = FranceTaxBenefitSystem()
    # définit un ménage par ligne
    sim = simulation(PERIOD, df, TBS)
    net = var_nette
    df[net] = sim[0].calculate_add(net, PERIOD)
    return df[[var_brute, var_nette]]


def from_net_to_brut(val_nette, dataframe_brut_to_net):
    dfv = dataframe_brut_to_net.values
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


def from_brut_to_net(val_brute, dataframe_brut_to_net):
    dfv = dataframe_brut_to_net.values
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


conversion_variables = {}

conversion_variables["salaire_de_base_to_salaire_imposable"] = scenar_values(
    0, 12_000_000, "salaire_de_base", "salaire_imposable"
)
conversion_variables["retraite_brute_to_retraite_imposable"] = scenar_values(
    0, 12_000_000, "retraite_brute", "retraite_imposable"
)


PERIOD = str(annee_de_calcul)
TBS = FranceTaxBenefitSystem()
TBS_DEFAULT = {"avant": TBS}
for nom_reforme in reformes_par_defaut:
    TBS_DEFAULT[nom_reforme] = IncomeTaxReform(
        TBS, reformes_par_defaut[nom_reforme], PERIOD
    )
CAS_TYPE = load_data("DCT.csv")
DUMMY_DATA = (
    CAS_TYPE
    if version_beta_sans_simu_pop
    else load_data(data_path).sort_values(by="idfoy")
)

# Initialisation des données utilisées pour le calcul sur la population
logging.info(
    "Dummy Data loaded "
    + str(len(DUMMY_DATA))
    + " lines "
    + str(len(DUMMY_DATA["idfoy"].unique()))
    + " foyers fiscaux"
)
# Resultats sur la population du code existant et, lorsqu'il y en a un de configuré, du PLF.
# Ne change jamais donc pas besoin de fatiguer l'ordi à calculer : ils sont mémorisés en base de données.
# Test à implémenter : si les résultats de base sont là, ils correspondent aux résultats qu'on calculerait
# sur le data_path
resultats_de_base = from_postgres(nom_table_resultats_base)
if (
    resultats_de_base is not None
):  # Si la table n'existe pas dans le schéma SQL (par exemple si la variable d'environnement comporte une erreur, ou si on n'a pas mis les données dans la base SQL du serveur), ce sera None et on les calcule nous même
    logging.info(
        "Table resultats de base used : "
        + nom_table_resultats_base
        + " "
        + str(len(resultats_de_base))
        + " rows"
    )
    resultats_de_base = resultats_de_base.set_index("idfoy").sort_index()
else:
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS)
    resultats_de_base = simulation_base_deciles[1]["foyer_fiscal"][["wprm"]]
    # precalcul cas de base sur la population pour le cache
    simulations_reformes_par_defaut_deciles = {}
    for nom_reforme in TBS_DEFAULT:
        simulations_reformes_par_defaut_deciles[nom_reforme] = simulation(
            PERIOD, DUMMY_DATA, TBS_DEFAULT[nom_reforme]
        )
        resultats_de_base[nom_reforme] = simulations_reformes_par_defaut_deciles[
            nom_reforme
        ][0].calculate("irpp", PERIOD)
simulations_reformes_par_defaut_castypes = {}
for nom_reforme in liste_noms_reformes_sans_apres:
    simulations_reformes_par_defaut_castypes[nom_reforme] = simulation(
        PERIOD, CAS_TYPE, TBS_DEFAULT[nom_reforme]
    )


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
            from_brut_to_net(
                sb, conversion_variables["salaire_de_base_to_salaire_imposable"]
            )
            for sb in data[data["idfoy"] == idfoy]["salaire_de_base"].values
        ]
        + [
            from_brut_to_net(
                rb, conversion_variables["retraite_brute_to_retraite_imposable"]
            )
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
        len(
            data[
                (data["idfoy"] == idfoy) & (data["quifoy"] <= 1) & (data["invalidite"])
            ]
        )
        if "invalidite" in data
        else 0
    )
    nb_pac_invalides = (
        len(
            data[(data["idfoy"] == idfoy) & (data["quifoy"] > 1) & (data["invalidite"])]
        )
        if "invalidite" in data
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
    return (
        df,
        {
            nom_reforme: simulation(PERIOD, df, reforme)
            for nom_reforme, reforme in TBS_DEFAULT.items()
        },
    )


def dataframe_from_cas_types_description(descriptions):
    """
    Transforme une description de cas types (au format de l'API web)
    en un dataframe parsable. Good luck!
    """

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
        "caseF",
        "caseL",
        "caseP",
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
                    ct["revenu"] / nbd,
                    conversion_variables["retraite_brute_to_retraite_imposable"],
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
                        ct["revenu"] / nbd,
                        conversion_variables["retraite_brute_to_retraite_imposable"],
                    )
                ]
                + [0] * nbc
            )
            dres["salaire_de_base"] += (
                [
                    from_net_to_brut(
                        ct["revenu"] / nbd,
                        conversion_variables["salaire_de_base_to_salaire_imposable"],
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
                    ct["revenu"] / nbd,
                    conversion_variables["salaire_de_base_to_salaire_imposable"],
                )
            ] * nbd + [0] * nbc
            dres["retraite_brute"] += [0] * (nbd + nbc)
        indexfoyer += 1
        # Finalement, invalides vont :
        # Le premier du ménage compte pour caseP
        # Le deuxième adulte compte pour caseF
        # En plus de ça, on renseigne par individu la colonne "invalidite"
        # parce qu'OF calcule bien à partir de cette colonne pour les PAC
        # pas pour les déclarants
        dres["invalidite"] += [
            1 if id_declarant < ct["nb_decl_invalides"] else 0
            for id_declarant in range(nbd)
        ] + [1 if id_pac < ct["nb_pac_invalides"] else 0 for id_pac in range(nbc)]
        dres["caseP"] += [1 if ct["nb_decl_invalides"] else 0] * (nbd + nbc)
        dres["caseF"] += [1 if ct["nb_decl_invalides"] > 1 else 0] * (nbd + nbc)
        # TODO : be able to choose if garde_alternee personnes_a_charges are also the ones with invalidite or not
        dres["garde_alternee"] += [0] * nbd + [
            1 if id_pac < ct["nb_pac_charge_partagee"] else 0 for id_pac in range(nbc)
        ]

        for _ in range(nbd):
            dres["activite"] += [0] if not ct["nombre_declarants_retraites"] else [3]
            dres["contrat_de_travail"] += (
                [0] if not ct["nombre_declarants_retraites"] else [6]
            )
            dres["statut_marital"] += (
                [5] if nbd > 1 else [4 if ct["nb_decl_veuf"] else 2]
            )
        for _ in range(nbc):
            dres["activite"] += [2]
            dres["contrat_de_travail"] += [6]
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
        # On prend les données de la population entière
        data = DUMMY_DATA
        reform = IncomeTaxReform(TBS, dictreform, PERIOD)
        # On ne crée qu'une simulation, le moteur de calcul ayant précalculé les autres.
        simulation_reform = simulation(PERIOD, data, reform)
        # On n'envoie à simuler que le "apres"
        return compare(PERIOD, {"apres": simulation_reform}, isdecile)

    # Pour les cas-types, on n'utilise pas de resultats précalculés
    # donc on inclut aussi les simulations par défaut
    data, default_sims = (
        (CAS_TYPE, simulations_reformes_par_defaut_castypes)
        if castypedesc is None
        else simulation_from_cas_types(castypedesc)
    )
    reform = IncomeTaxReform(TBS, dictreform, PERIOD)
    simulation_reform = simulation(PERIOD, data, reform)
    default_sims["apres"] = simulation_reform

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

    return compare(PERIOD, default_sims, isdecile)

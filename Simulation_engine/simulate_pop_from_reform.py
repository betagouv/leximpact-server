from functools import partial
from typing import Dict, List, Optional
import os

import pandas  # type: ignore

from openfisca_core.simulation_builder import SimulationBuilder  # type: ignore
from openfisca_france import FranceTaxBenefitSystem  # type: ignore
from models import from_postgres
from Simulation_engine.reforms import IncomeTaxReform

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


def compare(period: str, simulation_base, simulation_reform, compute_deciles=True):
    res: List[float] = []
    kk = 0

    for simulation, dictionnaire_datagrouped in [simulation_base, simulation_reform]:
        if not kk:
            df = dictionnaire_datagrouped["foyer_fiscal"][["wprm"]]
        for nomvariable in ["irpp", "nbptr"]:

            dictionnaire_datagrouped["foyer_fiscal"][
                nomvariable
            ] = simulation.calculate(nomvariable, period)
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"] = (
                dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                * dictionnaire_datagrouped["foyer_fiscal"]["wprm"]
            )

            if nomvariable == "irpp":
                res += [
                    -dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum()
                ]  # / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()]
                if kk:
                    df["apres"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                else:
                    df["avant"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                    kk += 1

    total: Total = {"avant": res[0], "apres": res[1]}

    if compute_deciles:
        totweight = dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()
        nbd = 10
        decilweights = [i / nbd * totweight for i in range(nbd + 1)]
        numdecile = 1
        df["keysort"] = -df["avant"] - df["apres"]
        df = df.sort_values(
            by="keysort"
        )  # For now, deciles are organized by level of irpp
        currw = 0
        currb = 0
        curra = 0
        dfv = df.values
        decilesres = [[0, 0, 0]]
        decdiffres: Deciles = []
        eps = 0.0001
        keysdicres = ["poids", "avant", "apres"]
        for v in dfv:
            currw += v[0]
            currb += -v[1] * v[0]
            curra += -v[2] * v[0]
            if currw >= decilweights[numdecile] - eps:
                decilesres += [[currw, currb, curra]]
                decdiffres += [
                    {
                        keysdicres[k]: decilesres[numdecile][k]
                        - decilesres[numdecile - 1][k]
                        for k in range(3)
                    }
                ]
                numdecile += 1

        # TODO : interpolate quantiles instead of doing the granular approach
        # This is the only TODO part in this code, I highly doubt it's the most pressing matter

        if adjust_results:
            empiric = 78 * 10 ** 9
            factor = adjustment(empiric, total["avant"])
            total = adjust_total(factor, total)
            deciles: Deciles = adjust_deciles(factor, decdiffres)
        else:
            deciles = decdiffres

        resultat = {"total": total, "deciles": deciles}

    else:  # This only interests us for the castypes
        resultat = {"total": total, "res_brut": df.to_dict()}

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


PERIOD = "2018"
TBS = FranceTaxBenefitSystem()
CAS_TYPE = load_data("DCT.csv")
SIMCAT = partial(simulation, period=PERIOD, data=CAS_TYPE)
SIMCAT_BASE = SIMCAT(tbs=TBS)

if not version_beta_sans_simu_pop:
    DUMMY_DATA = load_data(data_path)
    SIMPOP = partial(simulation, period=PERIOD, data=DUMMY_DATA)
    SIMPOP_BASE = SIMPOP(tbs=TBS)
    # Keeping computations short with option to keep file under 1000 FF
    # DUMMY_DATA = DUMMY_DATA[(DUMMY_DATA["idmen"] > 2500) & (DUMMY_DATA["idmen"] < 7500)]
    print("Dummy Data loaded", len(DUMMY_DATA), "lines")
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS)
simulation_base_castypes = simulation(PERIOD, CAS_TYPE, TBS)


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
            u"{} déclarant{}, d'âge {}".format(
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
    revenu = (
        data[data["idfoy"] == idfoy]["salaire_de_base"].sum()
        + data[data["idfoy"] == idfoy]["retraite_brute"].sum()
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
                    | ((data["salaire_de_base"] < 1) & (data["age"] >= 55))
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

    dicres = {
        "revenu": int(revenu),
        "nombre_declarants": int(nbpr),
        "nombre_personnes_a_charge": int(nbpac),
        "nombre_declarants_retraites": int(nbret),
        "outre_mer": 1 * outremer1 + 2 * outremer2,
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


def simulation_from_ct(descriptions):
    df = dataframe_from_ct_desc(descriptions)
    return (df, simulation(PERIOD, df, TBS))


# Transforme une description de cas types en un dataframe parsable. Good luck!
def dataframe_from_ct_desc(descriptions):
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

    indexfoyer = 0
    indexpac = 2
    for ct in descriptions:
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
        if ct["nombre_declarants_retraites"]:
            dres["retraite_brute"] += [ct["revenu"] / nbd] * nbd + [0] * nbc
            dres["salaire_de_base"] += [0] * (nbd + nbc)
            isretraite += [1] * (nbd) + [0] * (nbc)
        else:
            isretraite += [0] * (nbd + nbc)
            dres["salaire_de_base"] += [ct["revenu"] / nbd] * nbd + [0] * nbc
            dres["retraite_brute"] += [0] * (nbd + nbc)
        indexfoyer += 1

        for _ in range(nbd):
            dres["activite"] += [0] if not ct["nombre_declarants_retraites"] else [3]
            dres["contrat_de_travail"] += (
                [0] if not ct["nombre_declarants_retraites"] else [6]
            )
            dres["heures_remunerees_volume"] += (
                [1200] if not ct["nombre_declarants_retraites"] else [0]
            )
            dres["statut_marital"] += [5] if nbd > 1 else [2]
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
    data, simulation_base = (
        (DUMMY_DATA, simulation_base_deciles)
        if isdecile
        else (
            (CAS_TYPE, simulation_base_castypes)
            if castypedesc is None
            else simulation_from_ct(castypedesc)
        )
    )
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

    reform = IncomeTaxReform(TBS, dictreform, PERIOD)
    #   reform = reform_from_bareme(
    #       TBS, [0] + taux[: len(taux) // 2], [0] + taux[len(taux) // 2 :], PERIOD
    #   )
    simulation_reform = simulation(PERIOD, data, reform)
    return compare(PERIOD, simulation_base, simulation_reform, isdecile)


if __name__ == "__main__":
    dictreform = {
        "impot_revenu": {
            "bareme": {
                "seuils": [0, 9964, 27159, 73779, 156244],
                "taux": [0, 0.14, 0.30, 0.41, 0.45],
            },
            "decote": {"seuil_celib": 1000, "seuil_couple": 2000},
        }
    }
    reform = IncomeTaxReform(TBS, dictreform, PERIOD)
    if version_beta_sans_simu_pop:
        simulation_reform = simulation(PERIOD, CAS_TYPE, reform)
        compare(
            PERIOD, simulation_base_castypes, simulation_reform, compute_deciles=False
        )
        CompareOldNew("osef", False, dictreform, desc_cas_types())
    else:
        simulation_reform = simulation(PERIOD, DUMMY_DATA, reform)
        compare(PERIOD, simulation_base_deciles, simulation_reform)
        compare(PERIOD, None, simulation_reform)

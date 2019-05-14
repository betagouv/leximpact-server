# -*- coding: utf-8 -*-


from typing import List
from typing import Callable
from functools import partial

import pandas
import time

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem
from openfisca_core import periods
from openfisca_france.model.base import Reform


version_beta_sans_simu_pop = False


def fread(filename: str) -> Callable:
    if filename[-3:] == ".h5":
        fun = pandas.read_hdf

    else:
        fun = pandas.read_csv

    return lambda path: fun(path.format(filename))


def load_data(fread: Callable):
    try:
        data = fread("./{}")

    except (Exception):
        try:
            data = fread("./Simulation_engine/{}")

        except (Exception):
            data = fread("C:/EIG/Leximpact_git/Simulation_engine/{}")

    return data


# impot_revenu:
#  bareme:
#    seuils : list of thresholds
#    taux :  list of rates x 100
#  decote :
#    seuil_celib :
#    seuil_couple :


def reform_generique(tbs, dictparams, period):
    class apply_reform(Reform):
        def apply(self):
            self.modify_parameters(modifier_function=reform)

    def reform(parameters):
        print("Oui je suis censé passer par là")
        instant = periods.instant(period)
        reform_period = periods.period(
            "year:1900:200"
        )  # Pour le moment mes réformes sont sur l'éternité
        print(dictparams)
        if "impot_revenu" in dictparams:
            dir = dictparams["impot_revenu"]
            if "decote" in dir:
                dird = dir["decote"]
                seuil_celib = dird["seuil_celib"]
                seuil_couple = dird["seuil_couple"]
                print("decote avant modif : ")
                print(
                    parameters.impot_revenu.decote.seuil_celib.get_at_instant(instant),
                    parameters.impot_revenu.decote.seuil_couple.get_at_instant(instant),
                )
                parameters.impot_revenu.decote.seuil_celib.update(
                    period=reform_period, value=float(seuil_celib)
                )
                parameters.impot_revenu.decote.seuil_couple.update(
                    period=reform_period, value=float(seuil_couple)
                )
                print("decote apres modif : ")
                print(
                    parameters.impot_revenu.decote.seuil_celib.get_at_instant(instant),
                    parameters.impot_revenu.decote.seuil_couple.get_at_instant(instant),
                )
            if "bareme" in dir:
                dirb = dir["bareme"]
                seuils = dirb["seuils"]
                taux = dirb["taux"]
                print("bareme avant modif :")
                print(parameters.impot_revenu.bareme.get_at_instant(instant))
                for i in range(len(seuils)):
                    parameters.impot_revenu.bareme.brackets[i].threshold.update(
                        period=reform_period, value=seuils[i]
                    )
                    parameters.impot_revenu.bareme.brackets[i].rate.update(
                        period=reform_period, value=taux[i] * 0.01
                    )

                for i in range(len(seuils), 15):
                    try:
                        parameters.impot_revenu.bareme.brackets[i].threshold.update(
                            period=reform_period, value=seuils[-1] + i
                        )
                        parameters.impot_revenu.bareme.brackets[i].rate.update(
                            period=reform_period, value=taux[-1] * 0.01
                        )
                    except (Exception):
                        break

                print("bareme après modif :")
                print(parameters.impot_revenu.bareme.get_at_instant(instant))
        return parameters

    return apply_reform(tbs)


# Deprecated function
def reform_from_bareme(tbs, seuils, taux, period):
    class apply_reform(Reform):
        def apply(self):
            self.modify_parameters(modifier_function=reform)

    def reform(parameters):
        print("Non je ne suis plus censé passer par là")
        assert 1 == 0  # Le script doit désormais utiliser une autre fonction
        instant = periods.instant(period)

        print("bareme avant modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(instant))
        reform_period = periods.period(
            "year:1900:200"
        )  # Pour le moment mes réformes sont sur l'éternité
        for i in range(len(seuils)):
            parameters.impot_revenu.bareme.brackets[i].threshold.update(
                period=reform_period, value=seuils[i]
            )
            parameters.impot_revenu.bareme.brackets[i].rate.update(
                period=reform_period, value=taux[i] * 0.01
            )

        for i in range(len(seuils), 15):
            try:
                parameters.impot_revenu.bareme.brackets[i].threshold.update(
                    period=reform_period, value=seuils[-1] + i
                )
                parameters.impot_revenu.bareme.brackets[i].rate.update(
                    period=reform_period, value=taux[-1] * 0.01
                )
            except (Exception):
                break

        print("bareme après modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(instant))

        return parameters

    return apply_reform(tbs)


def simulation(period, data, tbs, timer=None):
    if timer is not None:
        starttime = timer.time()
        print("Elapsed time : {:.2f}".format(timer.time() - starttime))

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

        # The following ssumes data defined for an entity are the same for all rows in the same entity
        # Or at least that the first non null value found for an entity will always be the total value for an entity
        # (Which is the case for f4ba). These checks are performed in the checkdata function defined belowx
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
            try:
                simulation.set_input(
                    colonne,
                    period,
                    dictionnaire_datagrouped[tbs.get_variable(colonne).entity.key][
                        colonne
                    ],
                )
                print(
                    "{} was attributed to {}".format(
                        colonne, tbs.get_variable(colonne).entity.key
                    )
                )

            except (Exception):
                try:
                    print(
                        "{} failed to be attributed to {}".format(
                            colonne, tbs.get_variable(colonne).entity.key
                        )
                    )
                except (Exception):
                    print("{} was attributed to NOUGHT".format(colonne))
                raise

    if timer is not None:
        print("Elapsed time : {:.2f}".format(timer.time() - starttime))

    return simulation, dictionnaire_datagrouped


def compare(
    period: str, simulation_base, simulation_reform, compute_deciles=True, timer=None
):
    res = []
    kk = 0
    for simulation, dictionnaire_datagrouped in [simulation_base, simulation_reform]:
        if not kk:
            df = dictionnaire_datagrouped["foyer_fiscal"][["wprm"]]
        for nomvariable in ["irpp", "nbptr"]:
            if timer is not None:
                starttime = timer.time()

            dictionnaire_datagrouped["foyer_fiscal"][
                nomvariable
            ] = simulation.calculate(nomvariable, period, max_nb_cycles=1)
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"] = (
                dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                * dictionnaire_datagrouped["foyer_fiscal"]["wprm"]
            )

            print(
                "{} sum : {}  mean : {}".format(
                    nomvariable,
                    dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum(),
                    dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum()
                    / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum(),
                )
            )

            if timer is not None:
                print("Elapsed time : {:.2f}".format(timer.time() - starttime))

            if nomvariable == "irpp":
                res += [
                    -dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum()
                ]  # / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()]
                if kk:
                    df["apres"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                else:
                    df["avant"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                    kk += 1
    dic_res = {}
    dic_res["total"] = {}
    dic_res["total"]["avant"] = res[0]
    dic_res["total"]["apres"] = res[1]
    if compute_deciles:
        print("Computing Deciles")
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
        decdiffres = []
        print(decilweights, dfv[0], totweight)
        print(dfv[1])
        eps = 0.0001
        for v in dfv:
            currw += v[0]
            currb += v[1] * v[0]
            curra += v[2] * v[0]
            if currw >= decilweights[numdecile] - eps:
                decilesres += [[currw, currb, curra]]
                decdiffres += [
                    [
                        decilesres[numdecile][k] - decilesres[numdecile - 1][k]
                        for k in range(3)
                    ]
                ]
                numdecile += 1
        print("In fine ", currw, currb, curra)
        print("mes valeurs agreg deciles :", decilesres)
        print("mes valeurs diff deciles :", decdiffres)
        # TODO : interpolate quantiles instead of doing the granular approach
        dic_res["deciles"] = decdiffres
    else:  # This only interests us for the castypes
        dic_res["res_brut"] = df.to_dict()
    print(dic_res)
    return dic_res


PERIOD = "2018"
TBS = FranceTaxBenefitSystem()
# REFORM = partial(reform_from_bareme, period=PERIOD, tbs=TBS)
REFORM = partial(reform_generique, period=PERIOD, tbs=TBS)

CAS_TYPE = load_data(fread("DCT.csv"))
SIMCAT = partial(simulation, period=PERIOD, data=CAS_TYPE)
SIMCAT_BASE = SIMCAT(tbs=TBS)

if not version_beta_sans_simu_pop:
    DUMMY_DATA = load_data(fread("dummy_data.h5"))
    SIMPOP = partial(simulation, period=PERIOD, data=DUMMY_DATA)
    SIMPOP_BASE = SIMPOP(tbs=TBS)
    # Keeping computations short with option to keep file under 1000 FF
    # DUMMY_DATA = DUMMY_DATA[DUMMY_DATA["idmen"] < 1000]
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS, timer=time)

simulation_base_castypes = simulation(PERIOD, CAS_TYPE, TBS, timer=time)


def foyertosomethingelse(idfoy):
    return "oui j'ai un foyer son numero est {}".format(idfoy)


def foyertotexte(idfoy, data=None):
    if data is None:
        data = CAS_TYPE
    myct = data[data["idfoy"] == idfoy]
    # print("Je fais un foyer to texte pour le foyer ",idfoy,myct)
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
    print(idfoy, "est mon idfoy et mon rev ", revenu)
    return revenu


def revenus_cas_types(data=None):
    if data is None:
        data = CAS_TYPE
    dic_res = {}
    for k in data["idfoy"].values:
        dic_res[k] = foyertorevenu(k, data)
    print("dic_res ", dic_res)
    return dic_res


def texte_cas_types(data=None):
    if data is None:
        data = CAS_TYPE
    dic_res = {}
    for k in data["idfoy"].values:
        dic_res[k] = foyertotexte(k, data)
    return dic_res


def CompareOldNew(taux=None, isdecile=True, dictreform=None):
    print("comparing old new, isdecile = {} ".format(isdecile))
    # if isdecile, we want the impact on the full population, while just a cas type on the isdecile=False
    data, simulation_base = (
        (DUMMY_DATA, simulation_base_deciles)
        if isdecile
        else (CAS_TYPE, simulation_base_castypes)
    )
    if dictreform is None:
        assert taux is not None
        dictreform = {
            "impot_revenu": {
                "bareme": {
                    "seuils": [0] + taux[: len(taux) // 2],
                    "taux": [0] + taux[len(taux) // 2 :],
                }
            }
        }
    reform = reform_generique(TBS, dictreform, PERIOD)
    #   reform = reform_from_bareme(
    #       TBS, [0] + taux[: len(taux) // 2], [0] + taux[len(taux) // 2 :], PERIOD
    #   )
    simulation_reform = simulation(PERIOD, data, reform, timer=time)
    return compare(PERIOD, simulation_base, simulation_reform, isdecile, timer=time)


if __name__ == "__main__":
    taux = [9964, 27159, 73779, 156244, 14, 30, 41, 45]
    dictreform = {
        "impot_revenu": {
            "bareme": {
                "seuils": [0] + taux[: len(taux) // 2],
                "taux": [0] + taux[len(taux) // 2 :],
            },
            "decote": {"seuil_celib": 1000, "seuil_couple": 2000},
        }
    }
    reform = reform_generique(TBS, dictreform, PERIOD)
    # reform = reform_from_bareme(
    #     TBS, [0] + taux[: len(taux) // 2], [0] + taux[len(taux) // 2 :], PERIOD
    # )
    if version_beta_sans_simu_pop:
        simulation_reform = simulation(PERIOD, CAS_TYPE, reform, timer=time)
        compare(
            PERIOD,
            simulation_base_castypes,
            simulation_reform,
            compute_deciles=False,
            timer=time,
        )
    else:
        simulation_reform = simulation(PERIOD, DUMMY_DATA, reform, timer=time)
        compare(PERIOD, simulation_base_deciles, simulation_reform, timer=time)

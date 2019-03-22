# -*- coding: utf-8 -*-


from typing import Callable
from functools import partial

import pandas
import time

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem
from openfisca_core import periods
from openfisca_france.model.base import Reform


def fread(filename: str) -> Callable:
    if filename[-3:] == ".h5":
        fun = pandas.read_hdf

    else:
        fun = pandas.read_csv

    return lambda path: fun(path.format(filename))


def load_data(fread: Callable):
    try:
        data = fread("./{}")

    except(Exception):
        try:
            data = fread("./Simulation_engine/{}")

        except(Exception):
            data = fread("C:/EIG/Leximpact_git/Simulation_engine/{}")

    return data


def reform_from_bareme(period, tbs, taux):
    class apply_reform(Reform):
        def apply(self):
            self.modify_parameters(modifier_function = reform)

    def reform(parameters):
        instant = periods.instant(period)

        print("bareme avant modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(instant))

        seuil = parameters.impot_revenu.bareme.get_at_instant(instant)
        reform_period = periods.period("year:1900:200")  # Pour le moment mes réformes sont sur l'éternité

        for i in range(len(seuil.rates)):
            parameters.impot_revenu.bareme.brackets[i].threshold.update(
                period = reform_period,
                value = seuil.thresholds[i] if i != 1 else min(taux, seuil.thresholds[i + 1])
                )

            parameters.impot_revenu.bareme.brackets[i].rate.update(period = reform_period, value = seuil.rates[i])

        for i in range(len(seuil.rates), 15):
            try:
                parameters.impot_revenu.bareme.brackets[i].threshold.update(
                    period = reform_period,
                    value = seuil.thresholds[-1] + i
                    )

                parameters.impot_revenu.bareme.brackets[i].rate.update(period = reform_period, value = seuil.rates[-1])

            except(Exception):
                pass

        parameters.impot_revenu.bareme.brackets[1].threshold.update(period = reform_period, value = taux)

        print("bareme après modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(instant))

        return parameters

    return apply_reform(tbs)


def simulation(period, data, tbs, timer = None):
    if timer:
        starttime = timer.time()
        print("Elapsed time : {:.2f}".format(timer.time() - starttime))

    # Traduction des roles attribués au format openfisca
    data["quimenof"] = "enfant"
    data.loc[data["quifoy"] == 1, 'quimenof'] = "conjoint"
    data.loc[data["quifoy"] == 0, 'quimenof'] = "personne_de_reference"

    data["quifoyof"] = "personne_a_charge"
    data.loc[data["quifoy"] == 1, 'quifoyof'] = "conjoint"
    data.loc[data["quifoy"] == 0, 'quifoyof'] = "declarant_principal"

    data["quifamof"] = "enfant"
    data.loc[data["quifam"] == 1, 'quifamof'] = "conjoint"
    data.loc[data["quifam"] == 0, 'quifamof'] = "demandeur"

    sb = SimulationBuilder()
    sb.create_entities(tbs)

    sb.declare_person_entity('individu', data.index)

    # Creates openfisca entities and generates grouped

    listentities = {
        "foy": "foyer_fiscal",
        "men": "menage",
        "fam": "famille",
        }

    instances = {}
    dictionnaire_datagrouped = {"individu": data}

    for ent, ofent in listentities.items():
        persons_ent = data["id" + ent].values
        persons_ent_roles = data["qui" + ent + "of"].values
        ent_ids = data["id" + ent].unique()
        instances[ofent] = sb.declare_entity(ofent, ent_ids)
        sb.join_with_persons(instances[ofent], persons_ent, roles = persons_ent_roles)

        # The following ssumes data defined for an entity are the same for all rows in the same entity
        # Or at least that the first non null value found for an entity will always be the total value for an entity
        # (Which is the case for f4ba). These checks are performed in the checkdata function defined belowx
        dictionnaire_datagrouped[ofent] = data.groupby("id" + ent, as_index = False).first().sort_values(by = "id" + ent)

    # These variables should not be attributed to any OpenFisca Entity
    columns_not_OF_variables = set([
        "idmen",
        "idfoy",
        "idfam",
        "noindiv",
        "level_0",
        "quifam",
        "quifoy",
        "quimen",
        "wprm",
        "index",
        "idmen_original",
        "idfoy_original",
        "idfam_original",
        "quifamof",
        "quifoyof",
        "quimenof",
        ])

    simulation = sb.build(tbs)

    # Attribution des variables à la bonne entité OpenFisca
    for colonne in data.columns:
        if colonne not in columns_not_OF_variables:
            try:
                simulation.set_input(colonne, period, dictionnaire_datagrouped[tbs.get_variable(colonne).entity.key][colonne])
                print("{} was attributed to {}".format(colonne, tbs.get_variable(colonne).entity.key))

            except(Exception):
                print("{} failed to be attributed to {}".format(colonne, tbs.get_variable(colonne).entity.key))
                raise

    if timer:
        print("Elapsed time : {:.2f}".format(timer.time() - starttime))

    return simulation, dictionnaire_datagrouped


def compare_cas_type(simulation_base, simulation_reform, period: str, taux: int, timer = None):
    res = []

    for simulation, dictionnaire_datagrouped in [simulation_base, simulation_reform]:
        for nomvariable in ["irpp", "nbptr"]:
            if timer:
                starttime = timer.time()
                print("Elapsed time : {:.2f}".format(timer.time() - starttime))

            dictionnaire_datagrouped["foyer_fiscal"][nomvariable] = simulation.calculate(nomvariable, period, max_nb_cycles = 1)
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable] * dictionnaire_datagrouped["foyer_fiscal"]["wprm"]

            print("{} sum : {}  mean : {}".format(nomvariable, dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum(), dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum() / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()))

            if timer:
                print("Elapsed time : {:.2f}".format(timer.time() - starttime))

            if nomvariable == "irpp":
                res += [-dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum() / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()]

    print("Je suis Wengerboy et j'ai été lancé avec un parametre de {} et oui j'ai fini {}".format(taux, res))

    return res


def compare_decile(simulation_base, simulation_reform, period: str, taux: int, timer = None):
    res = []
    kk = 0

    for simulation, dictionnaire_datagrouped in [simulation_base, simulation_reform]:
        if not kk:
            df = dictionnaire_datagrouped["foyer_fiscal"][["wprm"]]
        for nomvariable in ["irpp", "nbptr"]:
            st = time.time()
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable] = simulation.calculate(nomvariable, period, max_nb_cycles = 1)
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable] * dictionnaire_datagrouped["foyer_fiscal"]["wprm"]

            print("{} sum : {}  mean : {}".format(nomvariable, dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum(), dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum() / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()))
            print("Elapsed : {:.2f}".format(time.time() - st))

            if nomvariable == "irpp":
                res += [-dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum()]  # / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()]

                if kk:
                    df["after"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                else:
                    df["before"] = dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                    kk += 1

    print("Je suis Wengerboy et j'ai été lancé avec un parametre de {} et oui j'ai fini {}".format(taux, res))
    print("Computing Deciles")

    totweight = dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()
    nbd = 10
    decilweights = [i / nbd * totweight for i in range(nbd + 1)]
    numdecile = 1
    df = df.sort_values(by = 'after')  # For now, deciles are organized by level of irpp
    currw = 0
    currb = 0
    curra = 0
    dfv = df.values
    decilesres = [(0, 0, 0)]
    decdiffres = []

    print(decilweights, dfv[0], totweight)

    eps = 0.0001

    for v in dfv:
        currw += v[0]
        currb += v[1] * v[0]
        curra += v[2] * v[0]

        if currw >= decilweights[numdecile] - eps:
            decilesres += [(currw, currb, curra)]
            decdiffres += [[decilesres[numdecile][k] - decilesres[numdecile - 1][k] for k in range(3)]]
            numdecile += 1

    print("In fine ", currw, currb, curra)
    print("mes valeurs agreg deciles :", decilesres)
    print("mes valeurs diff deciles :", decdiffres)
    # TODO : interpolate quantiles instead of doing the granular approach
    return res + decdiffres


TBS = FranceTaxBenefitSystem()
PERIOD = "2014"
REFORM = partial(reform_from_bareme, period = PERIOD, tbs = TBS)

CAS_TYPE = load_data(fread("UCT-0001.csv"))
SIMCAT = partial(simulation, period = PERIOD, data = CAS_TYPE)
SIMCAT_BASE = SIMCAT(tbs = TBS)

DUMMY_DATA = load_data(fread("dummy_data.h5"))
SIMPOP = partial(simulation, period = PERIOD, data = DUMMY_DATA)
SIMPOP_BASE = SIMPOP(tbs = TBS)


def cas_type(taux):
    reform = REFORM(taux = taux)
    simulation_reform = SIMCAT(tbs = reform)
    return compare_cas_type(SIMCAT_BASE, simulation_reform, PERIOD, taux)


def decile(taux):
    reform = REFORM(taux = taux)
    simulation_reform = SIMPOP(tbs = reform)
    return compare_decile(SIMPOP_BASE, simulation_reform, PERIOD, taux)


def cout_etat(taux):
    reform = REFORM(taux = taux)
    simulation_reform = SIMPOP(tbs = reform)
    return compare_decile(SIMPOP_BASE, simulation_reform, PERIOD, taux)

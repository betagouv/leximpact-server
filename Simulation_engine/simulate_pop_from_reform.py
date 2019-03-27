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


def reform_from_bareme(tbs, seuils,taux, period):
    class apply_reform(Reform):
        def apply(self):
            self.modify_parameters(modifier_function = reform)

    def reform(parameters):
        instant = periods.instant(period)

        print("bareme avant modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(instant))
        reform_period = periods.period("year:1900:200")  # Pour le moment mes réformes sont sur l'éternité
        for i in range(len(seuils)):
            parameters.impot_revenu.bareme.brackets[i].threshold.update(
                period = reform_period,
                value = seuils[i]
                )
            parameters.impot_revenu.bareme.brackets[i].rate.update(
                period = reform_period,
                value = taux[i]*0.01
                )

        for i in range(len(seuils), 15):
            try:
                parameters.impot_revenu.bareme.brackets[i].threshold.update(
                    period = reform_period,
                    value = seuils[-1] + i
                    )
                parameters.impot_revenu.bareme.brackets[i].rate.update(period = reform_period, value = taux[-1]*0.01)
            except(Exception):
                break

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

from typing import List
def compare(bareme: List[int], period: str, simulation_base, simulation_reform):
    res = []
    kk=0
    taux=bareme[0]
    for simulation, dictionnaire_datagrouped in [simulation_base, simulation_reform]:
        if not kk:
            df = dictionnaire_datagrouped["foyer_fiscal"][["wprm"]]
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
                res += [-dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"].sum()] # / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()]
                if kk:
                    df["after"]=dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                else:
                    df["before"]=dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                    kk+=1
    print("Je suis Wengerboy et j'ai été lancé avec un parametre de {} et oui j'ai fini {}".format(taux, res))
    print("Computing Deciles")
    totweight=dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum()
    nbd=10
    decilweights=[i/nbd*totweight for i in range(nbd+1)]
    numdecile=1
    df["keysort"]=-df["before"]-df["after"]
    df=df.sort_values(by='keysort') #For now, deciles are organized by level of irpp
    currw=0
    currb=0
    curra=0
    dfv=df.values
    decilesres=[(0,0,0)]
    decdiffres=[]
    print(decilweights,dfv[0],totweight)
    print(dfv[1])
    eps=0.0001
    for v in dfv:
        currw+=v[0]
        currb+=v[1]*v[0]
        curra+=v[2]*v[0]
        if currw>=decilweights[numdecile]-eps:
            decilesres+=[(currw,currb,curra)]
            decdiffres+=[[decilesres[numdecile][k] - decilesres[numdecile-1][k] for k in range(3)]]
            numdecile+=1
    print("In fine ",currw,currb,curra)
    print("mes valeurs agreg deciles :",decilesres)
    print("mes valeurs diff deciles :",decdiffres)
    #TODO : interpolate quantiles instead of doing the granular approach
    return res+decdiffres

TBS = FranceTaxBenefitSystem()
REFORM = partial(reform_from_bareme, period = PERIOD, tbs = TBS)

CAS_TYPE = load_data(fread("UCT-0001.csv"))
SIMCAT = partial(simulation, period = PERIOD, data = CAS_TYPE)
SIMCAT_BASE = SIMCAT(tbs = TBS)

DUMMY_DATA = load_data(fread("dummy_data.h5"))
SIMPOP = partial(simulation, period = PERIOD, data = DUMMY_DATA)
SIMPOP_BASE = SIMPOP(tbs = TBS)

DUMMY_DATA = DUMMY_DATA [DUMMY_DATA ["idmen"]<1000]

data = DUMMY_DATA
period = "2014"
simulation_base = simulation(TBS, data, timer = time)

def CompareOldNew(taux):
    print(taux)
    print(taux[0],len(taux))
    reform = reform_from_bareme(TBS, [0]+taux[:len(taux)//2],[0]+taux[len(taux)//2:], period)
    simulation_reform = simulation(reform, data, timer = time)
    return compare(taux, period, simulation_base, simulation_reform)

if __name__ == "__main__":
    taux = [9964,27159,73779,156244,14,30,41,45]
    reform = reform_from_bareme(TBS, [0]+taux[:len(taux)//2],[0]+taux[len(taux)//2:], period)
    simulation_reform = simulation(reform, data, timer = time)
    compare(taux, period, simulation_base, simulation_reform)



def cas_type(taux):
    reform = REFORM(taux = taux)
    simulation_reform = SIMCAT(tbs = reform)
    return compare(PERIOD, taux,SIMCAT_BASE, simulation_reform, )

def decile(taux):
    reform = REFORM(taux = taux)
    simulation_reform = SIMPOP(tbs = reform)
    return compare(PERIOD, taux,SIMPOP_BASE, simulation_reform)


def cout_etat(taux):
    reform = REFORM(taux = taux)
    simulation_reform = SIMPOP(tbs = reform)
    return compare_decile(SIMPOP_BASE, simulation_reform, PERIOD, taux)

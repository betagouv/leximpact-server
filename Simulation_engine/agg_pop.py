# -*- coding: utf-8 -*-


from functools import partial

import pandas
import time
import os

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem
from openfisca_core import periods
from openfisca_france.model.base import Reform


def load_data(filename: str):
    path = os.path.join(os.path.dirname(__file__), filename)

    if filename[-3:] == ".h5":
        return pandas.read_hdf(path)

    return pandas.read_csv(path)


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


def aggregate(period: str, simulation_base):
    res = []
    for simulation, dictionnaire_datagrouped in [simulation_base]:
        df = dictionnaire_datagrouped["foyer_fiscal"][["wprm"]]
        for nomvariable in ["rfr", "irpp", "nbptr"]:
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
    return dictionnaire_datagrouped["foyer_fiscal"]


if __name__ == "__main__":
    PERIOD = "2018"
    TBS = FranceTaxBenefitSystem()
    DUMMY_DATA = load_data("./Simulation_engine/dummy_data.h5")
    # Keeping computations short with option to keep file under 1000 FF
    # DUMMY_DATA = DUMMY_DATA[DUMMY_DATA["idmen"] < 1000]
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS, timer=time)

    df = aggregate(PERIOD, simulation_base_deciles).sort_values(by="rfr")
    df.to_csv("exporteveryone.csv")
    print(
        "{} FF sur {} ont un revenu>0 , donc {:.2f}% ont que dalle ".format(
            len(df[df["rfr"] > 0.01]),
            len(df),
            100 - 100 * len(df[df["rfr"] > 0.01]) / len(df),
        )
    )

    # Step 1 : Ajustement du nombre de mecs à zéro...
    oldweight = 1 - df[df["rfr"] > 0.01]["wprm"].sum() / df["wprm"].sum()
    targetweight = 0.06
    redweightifrfr0 = targetweight * (1 - oldweight) / oldweight / (1 - targetweight)
    print(
        "Non en fait {} FF sur {} ont un revenu>0 , donc {:.2f}% ont que dalle. Je vais les ajuster.".format(
            df[df["rfr"] > 0.01]["wprm"].sum(),
            df["wprm"].sum(),
            100 - 100 * df[df["rfr"] > 0.01]["wprm"].sum() / df["wprm"].sum(),
        )
    )
    print("old : {} new : {} adj : {}".format(oldweight, targetweight, redweightifrfr0))
    # Revenus deciles:
    totrunsumrfr = 0
    totrunsumwprm = 0
    # Ajustement de réduction du poids
    df.loc[df["rfr"] < 0.01, "wprm"] = df["wprm"] * redweightifrfr0
    df.loc[df["rfr"] < 0.01, "rfrw"] = df["rfrw"] * redweightifrfr0
    print(
        "Non en fait {} FF sur {} ont un revenu>0 , donc {:.2f}% ont que dalle ".format(
            df[df["rfr"] > 0.01]["wprm"].sum(),
            df["wprm"].sum(),
            100 - 100 * df[df["rfr"] > 0]["wprm"].sum() / df["wprm"].sum(),
        )
    )
    # Step 1.1 : Ajuster le 1er décile  (pour l'instant on fait que dalle, y a pas vraiment d'impact

    # Step 2 : PBP (pareto by parts)

    # Stats officielles
    so = pandas.read_csv("./Simulation_engine/Calib/ResFinalCalibSenat.csv")
    # Je vais désormais déterminer la distribution de tout le monde :
    # - dans le premier décile :  Les valeurs exactes de l'ERFS * un facteur scalaire qui permet de rendre le premier décile = ce que je veux.
    # - dans la dernière catégorie : je prend le param de la loi de Pareto qui permet d'égaliser la moyenne de la dernière tranche
    # - dans toutes les autres catégories (sauf la dernière) : la distrib restrinte à un intervalle est une loi de Pareto au premier paramètre = le
    # debut de l'intervalle et deuxième paramètre : celui qui permet d'obtenir le bon nombre de gens dans l'intervalle
    ### End of step 2. Why am I commenting like that ? Who knows?

    totw = df["wprm"].sum()
    decilesagg = [(0, 0)]  # poids, rfr
    nbdec = 10
    wlims = [(totw - 0.00001) * _ / nbdec for _ in range(1, nbdec + 1)]
    numdec = 1
    for x in df[["wprm", "rfr", "rfrw"]].values:
        totrunsumwprm += x[0]
        totrunsumrfr += x[2]
        if totrunsumwprm >= wlims[numdec - 1]:
            print("{} Decile lim : {}".format(numdec, x[1]))
            decilesagg += [(totrunsumwprm, totrunsumrfr)]
            thisdec = [
                decilesagg[-1][0] - decilesagg[-2][0],
                decilesagg[-1][1] - decilesagg[-2][1],
            ]
            print(thisdec, "{:.2f}".format(thisdec[1] / thisdec[0]))
            numdec += 1
    tranches = (
        [10, 12, 15, 20, 30, 50]
        + list(range(100, 1000, 100))
        + list(range(1000, 10000, 1000))
        + [10 ** 6]
    )
    trancheslim = [tranche * 1000 for tranche in tranches]
    sommesPartielles = [(0, 0, 0)]
    nbp = [0]
    for tranche in trancheslim:
        nombreCourant, sommeCourante, sommeimpots = df[df["rfr"] <= tranche][
            ["wprm", "rfrw", "irppw"]
        ].sum()
        sommesPartielles += [(nombreCourant, sommeCourante, sommeimpots)]
        nbp += [len(df[df["rfr"] <= tranche])]
    valeursref = [
        (8779578, 37017352.91, -120470.926),
        (2141456, 23577329.09, -52667.915),
        (3415487, 46459160.772, -97920.236),
        (5907523, 102764311.931, 1757682.568),
        (6830792, 167947232.228, 5647709.376),
        (6553656, 250560654.266, 13309362.326),
        (3305940, 217391801.563, 20630440.587),
        (597946, 78515622.095, 12812673.619),
        (88183, 21094944.421, 4697851.34),
        (28243, 9670624.317, 2422618.717),
        (12523, 5567585.822, 1464664.904),
        (6552, 3572204.884, 965369.51),
        (3889, 2512859.538, 685320.67),
        (2456, 1833358.763, 511723.79),
        (1709, 1445836.223, 405218.849),
        (1247, 1181172.438, 330407.275),
        (4463, 6045094.957, 1605428.388),
        (978, 2349456.523, 618765.854),
        (389, 1339663.563, 332044.446),
        (177, 792643.994, 192016.727),
        (106, 582664.429, 145106.787),
        (62, 399427.263, 108240.956),
        (41, 310128.514, 84401.203),
        (36, 302012.261, 65296.768),
        (163, 2701278.296, 580641.771),
    ]

    res = {}
    adjust = [1, 1000, -1000]
    for k in range(len(tranches)):
        res[tranches[k]] = [
            (sommesPartielles[k + 1][i] - sommesPartielles[k][i]) / adjust[i]
            for i in range(3)
        ]

        res[tranches[k]] += [
            (res[tranches[k]][i] - valeursref[k][i]) * 100 / valeursref[k][i]
            for i in range(3)
        ]
        res[tranches[k]] += [nbp[k + 1] - nbp[k]]
        print(
            "{} : {:.2f} \t{:.2f}\t{:.2f}\t{:.2f}%\t{:.2f}%\t{:.2f}%\t{}".format(
                tranches[k], *res[tranches[k]]
            )
        )

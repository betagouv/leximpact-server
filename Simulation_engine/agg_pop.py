# -*- coding: utf-8 -*-


import pandas
import time
import os
import math

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


def simulation(period, data, tbs, timer=None, verbose=False):
    if verbose and timer is not None:
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
                if verbose:
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

    if verbose and timer is not None:
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
            ] = simulation.calculate(nomvariable, period)
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


def aggregats_ff(
    period: str, simulation_base, name_variables=["rfr", "irpp", "nbptr"], verbose=False
):
    res = []
    for simulation, dictionnaire_datagrouped in [simulation_base]:
        df = dictionnaire_datagrouped["foyer_fiscal"][["wprm"]]
        for nomvariable in name_variables:
            dictionnaire_datagrouped["foyer_fiscal"][
                nomvariable
            ] = simulation.calculate(nomvariable, period)
            dictionnaire_datagrouped["foyer_fiscal"][nomvariable + "w"] = (
                dictionnaire_datagrouped["foyer_fiscal"][nomvariable]
                * dictionnaire_datagrouped["foyer_fiscal"]["wprm"]
            )
            if verbose:
                print(
                    "{} sum : {}  mean : {} nb nonzero : {}".format(
                        nomvariable,
                        dictionnaire_datagrouped["foyer_fiscal"][
                            nomvariable + "w"
                        ].sum(),
                        dictionnaire_datagrouped["foyer_fiscal"][
                            nomvariable + "w"
                        ].sum()
                        / dictionnaire_datagrouped["foyer_fiscal"]["wprm"].sum(),
                        dictionnaire_datagrouped["foyer_fiscal"][
                            dictionnaire_datagrouped["foyer_fiscal"][nomvariable] != 0
                        ]["wprm"].sum(),
                    )
                )
    return dictionnaire_datagrouped["foyer_fiscal"]


def genpareto(xm, k, x):
    # (xm/res)^k=x
    return pow(x, -1 / k) * xm


def reverseCDF(calibratedso):
    sonk = calibratedso["Nk"].values
    sork = calibratedso["Rk"].values
    sopp = calibratedso["paramPareto"].values

    def reverseCDFfromTable(row):
        x = 1 - row["rsnw"]
        eps = 10 ** -9
        # returns (with the params specified) the value of Y so that (the probability that a random foyer
        # fiscal is higher than Y) is x.
        for piece in range(
            len(sonk)
        ):  # unoptimised computationally, ln(len(sov)) is possible
            if piece == len(sonk) - 1 or x > sonk[piece + 1] - eps:
                break
        if sopp[piece] < 0:
            return row["rfr"]
        # otherwise, we should not be here (we keep the empirical distribution for the lowest part so not
        # supposed to call this function)
        relprob = x / sonk[piece]
        simrfr = genpareto(sork[piece], sopp[piece], relprob)
        assert piece == len(sork) - 1 or simrfr <= sork[piece + 1]
        # making sure I stay within the bounds
        return simrfr

    return reverseCDFfromTable


def testerrorvalues(df, namerfr="rfr", nameweight="wprm"):
    errs = {
        var: [] for var in ["nombre_ff", "rfr", "irpp"]
    }  # absolute value of percentage differences
    totw = df[nameweight].sum()
    decilesagg = [(0, 0)]  # poids, rfr
    nbdec = 10
    wlims = [(totw - 0.00001) * _ / nbdec for _ in range(1, nbdec + 1)]
    numdec = 1
    namerfrw = namerfr + "w"  # Revenus deciles:
    totrunsumrfr = 0
    totrunsumwprm = 0
    for x in df[[nameweight, namerfr, namerfrw]].values:
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

    if namerfr != "rfr":
        print("WARNING: the impot is not good")
    for tranche in trancheslim:
        nombreCourant, sommeCourante, sommeimpots = df[df[namerfr] <= tranche][
            [nameweight, namerfr + "w", "irppw"]
        ].sum()
        sommesPartielles += [(nombreCourant, sommeCourante, sommeimpots)]
        nbp += [len(df[df[namerfr] <= tranche])]
        # nb foyers fisccaux , rfr, impots
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
        errs["nombre_ff"] += [res[tranches[k]][3] / 100]
        errs["rfr"] += [res[tranches[k]][4] / 100]
        errs["irpp"] += [res[tranches[k]][5] / 100]
        res[tranches[k]] += [nbp[k + 1] - nbp[k]]
        print(
            "{} : {:.2f} \t{:.2f}\t{:.2f}\t{:.2f}%\t{:.2f}%\t{:.2f}%\t{}".format(
                tranches[k], *res[tranches[k]]
            )
        )
    print("MY ERRORS")
    res_to_return = {}
    for k in errs:
        print(k, errs[k])
        err_moyenne = sum(
            [abs(errs[k][i] * res[tranches[i]][0]) for i in range(len(errs[k]))]
        ) / sum([res[tranches[i]][0] for i in range(len(errs[k]))])
        print(k, err_moyenne)
        # Erreur moyenne de rfr moye
        res_to_return[k] = err_moyenne
    print("returning", res_to_return)
    return res_to_return


def test_h5_input(
    input_h5="./Simulation_engine/dummy_data.h5",
    name_variables=["rfr", "irpp", "nbptr"],
    aggfunc="sum",
    compdic=None,
):
    PERIOD = "2018"
    TBS = FranceTaxBenefitSystem()
    DUMMY_DATA = load_data(input_h5)
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS, timer=time)
    df = aggregats_ff(PERIOD, simulation_base_deciles, name_variables).sort_values(
        by="rfr"
    )
    if aggfunc == "sum":  # Pour la somme, on calcule les % d'erreur sur la répartition.
        testerrorvalues(df)
    aggs_to_compute = ["wprm", "salaire_de_base", "retraite_brute"] + name_variables
    val_donnees_pac_agg = 0
    trpac_agg = [
        compdic[ag]
        for ag in ["nbF", "nbG", "nbH", "nbJ", "nbR"]
        if compdic is not None and ag in compdic
    ]
    val_reelle_pac_agg = sum(trpac_agg) if len(trpac_agg) else None
    for ag in aggs_to_compute:
        if aggfunc == "sum":
            nom_a_afficher = "Total aggrégé"
            if ag != "wprm":
                val_donnees = (df[ag] * df["wprm"]).sum()
            else:
                val_donnees = (df[ag]).sum()
        elif aggfunc == "countnonzero":
            if ag != "wprm":
                nom_a_afficher = "Non nuls"
                val_donnees = (df[df[ag] != 0]["wprm"]).sum()
            else:
                nom_a_afficher = "Nombre FF (c'est comme ça le count sur wprm)"
                val_donnees = df[ag].count()
        else:
            raise (
                "Only aggregation functions supported are sum and countnonzero. The rest is not very good if you want my opinion"
            )
        val_reelle = compdic[ag] if compdic is not None and ag in compdic else None
        print(
            "{} {} : {:.0f} {} {}".format(
                nom_a_afficher,
                ag,
                val_donnees,
                val_reelle if val_reelle is not None else "",
                "{:.2f}%".format((val_donnees / val_reelle - 1) * 100)
                if val_reelle is not None
                else "",
            )
        )
        if ag in ["nbF", "nbG", "nbH", "nbJ", "nbR"]:
            val_donnees_pac_agg += val_donnees
    if val_reelle_pac_agg is not None:
        print(
            "{} {} : {:.0f} {} {}".format(
                nom_a_afficher,
                "Enfants cumules",
                val_donnees_pac_agg,
                val_reelle_pac_agg if val_reelle_pac_agg is not None else "",
                "{:.2f}%".format((val_donnees_pac_agg / val_reelle_pac_agg - 1) * 100)
                if val_reelle_pac_agg is not None
                else "",
            )
        )


def ajustement_h5(
    input_h5="./Simulation_engine/dummy_data.h5",
    output_h5="./Simulation_engine/dummy_data_ajuste.h5",
    distribution_rfr_population="./Simulation_engine/Calib/ResFinalCalibSenat.csv",
):
    PERIOD = "2018"
    ajuste_h5 = output_h5
    TBS = FranceTaxBenefitSystem()
    DUMMY_DATA = load_data(input_h5)
    # Keeping computations short with option to keep file under 1000 FF
    # DUMMY_DATA = DUMMY_DATA[DUMMY_DATA["idmen"] < 1000]
    simulation_base_deciles = simulation(PERIOD, DUMMY_DATA, TBS, timer=time)
    df = aggregats_ff(PERIOD, simulation_base_deciles).sort_values(by="rfr")
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

    # Ajustement de réduction du poids
    df["adjwstep0"] = 1
    df["realwprm"] = df["wprm"]
    df.loc[df["rfr"] < 0.01, "adjwstep0"] = redweightifrfr0
    df.loc[df["rfr"] < 0.01, "realwprm"] = df["wprm"] * redweightifrfr0
    # Calibration du nombre total de foyers fiscaux
    target_foyers_fiscaux = 37889181
    # src : https://www.economie.gouv.fr/files/files/directions_services/dgfip/Rapport/2017/RA2017_cahierstats_0719.pdf
    adjust_wprm = target_foyers_fiscaux / df["realwprm"].sum()
    df["realwprm"] = df["realwprm"] * adjust_wprm
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
    so = pandas.read_csv(distribution_rfr_population)
    # doit contenir :
    # Colonne Rk : Revenu Fiscal de référence
    # Colonne Nk : Pourcentage de foyers fiscaux ayant un RFR >= à la colonne Rk
    # Colonne Ark : RFR moyen des foyers fiscaux  ayant un RFR >= à la colonne Rk (utilisée seulement pour la loi du
    # plus haut décile
    # Je vais désormais déterminer la distribution de tout le monde :
    # 2.0 - bon je vais associer le running weight de chaque mec...
    totw = df["realwprm"].sum()
    df = df.sort_values(by="rfr")
    df["nw"] = df["realwprm"] / totw  # normalized weight (total = 1)
    df["rsnw"] = df["nw"].cumsum() - df["nw"] / 2  # somme cumulée des nw.  on prend
    # 2.1 - dans le premier décile :  Les valeurs exactes de l'ERFS * un facteur scalaire qui permet de rendre le premier décile = ce que je veux.
    targetFirstDec = so["Rk"][1]
    limWeightFirstDec = so["Nk"][1]
    limOrigFirstDec = max(df[df["rsnw"] <= 1 - limWeightFirstDec]["rfr"])
    df["adjrevstep2"] = 1
    df.loc[df["rsnw"] <= 1 - limWeightFirstDec, "adjrevstep2"] = (
        targetFirstDec / limOrigFirstDec
    )
    # 2.2 - dans toutes les autres catégories (sauf la dernière) : la distrib restrinte à un intervalle est une loi de Pareto au premier paramètre = le
    # debut de l'intervalle et deuxième paramètre : celui qui permet d'obtenir le bon nombre de gens dans l'intervalle
    # Détermination de ce paramètre
    sonk = so["Nk"].values
    # parce que je sais toujours pas itérer ligne à ligne dans un DataFrame
    sork = so["Rk"].values
    paramsPareto = [-1]
    for i in range(1, len(sonk) - 1):
        n0 = sonk[i]
        n1 = sonk[i + 1]
        r0 = sork[i]
        r1 = sork[i + 1]

        newparam = math.log(n1 / n0) / math.log(r0 / r1)
        paramsPareto += [newparam]

    # 2.3 - dans la dernière catégorie : je prend le param de la loi de Pareto qui permet d'égaliser la moyenne de la dernière tranche
    # OK la moyenne d'une Pareto est : esp = (1 + 1/(k-1)) * xm
    #  k = 1/(esp/xm - 1) + 1
    lastaverage = so["dArk"].values[-1] * 1000
    lastthresh = sork[-1]
    paramsPareto += [1 / (lastaverage / lastthresh - 1) + 1]
    so["paramPareto"] = paramsPareto

    df["realrfr"] = df.apply(reverseCDF(so), axis=1)
    df["realrfrw"] = df["realrfr"] * df["realwprm"]

    # OK now that this great function works (does it? Why not try it? comparing it now to the original function??)
    # I can generate the REAL rfr

    ### End of step 2.

    testerrorvalues(df, "rfr", "wprm")
    aa = testerrorvalues(df, "realrfr", "realwprm")
    print("Aggregated Error % after calibration :", aa)
    # OKOK bon maintenant mon df contient le bon rfr et le bon realwprm
    df["total_ajust_revenu"] = 1
    df.loc[df["rfr"] > 0, "total_ajust_revenu"] = df["realrfr"] / df["rfr"]
    df["total_ajust_poids"] = df["realwprm"] / df["wprm"]

    # Je vais ajuster le .h5
    to_transform = pandas.read_hdf(input_h5)
    tt_colonnes = to_transform.columns
    df_changes = df[["idfoy", "total_ajust_revenu", "total_ajust_poids"]]
    to_transform = to_transform.merge(df_changes, on="idfoy")
    colspoids = ["wprm"]
    colsrevenus = [
        "chomage_brut",
        "pensions_alimentaires_percues",
        "rag",
        "ric",
        "rnc",
        "salaire_de_base",
        "f4ba",
        # "loyer",
        # "taxe_habitation",
    ]
    for cp in colspoids:
        to_transform[cp] = to_transform[cp] * to_transform["total_ajust_poids"]
    for cp in colsrevenus:
        to_transform[cp] = to_transform[cp] * to_transform["total_ajust_revenu"]
    to_transform = to_transform[tt_colonnes]
    to_transform.to_hdf(ajuste_h5, key="input")

    # J'ai ajusté le h5


if __name__ == "__main__":
    ajustement_h5()
    print("before adj :")
    test_h5_input()

    theoric_values = {  # source : stats impots 2018 (sur revenu 2017)
        "sum": {
            "rfr": 985_934_421,
            "irpp": -78000000000,
            "wprm": 38332977,
            "nbG": 244715,
            "nbF": 15748883,
            "nbH": 972058,
            "nbJ": 1906364,
            "nbR": 52124,
        },
        "countnonzero": {
            "maries_ou_pacses": 12990578,
            "celibataire_ou_divorce": 21388331,
            "veuf": 3954068,
            "nbF": 9088622,
            "nbH": 642590,
            "nbJ": 1630205,
            "nbR": 50091,
            "nbG": 232088,
        },
    }

    print("after adj :")
    test_h5_input(
        "./Simulation_engine/dummy_data_ajuste.h5",
        name_variables=[
            "rfr",
            "irpp",
            "nbptr",
            "maries_ou_pacses",
            "celibataire_ou_divorce",
            "veuf",
            "nbF",
            "nbG",
            "nbH",
            "nbJ",
            "nbR",
        ],
        aggfunc="sum",
        compdic=theoric_values["sum"],
    )
    print("And now, the counts : ")

    test_h5_input(
        "./Simulation_engine/dummy_data_ajuste.h5",
        name_variables=[
            "rfr",
            "irpp",
            "nbptr",
            "maries_ou_pacses",
            "celibataire_ou_divorce",
            "veuf",
            "nbF",
            "nbG",
            "nbH",
            "nbJ",
            "nbR",
        ],
        aggfunc="countnonzero",
        compdic=theoric_values["countnonzero"],
    )


# ToDo : Le test doit retourner True si :
#  - On a Une erreur totale sur la distrib de rfr < 2.5% après ajustement
#  - nb maries & co : 25% ecart maximum
#  - Enfants cumulés : 25% ecart?

def bareme(args: tuple) -> tuple:
    parameters, dir, instant, reform_period, verbose = args

    dirb = dir["bareme"]
    seuils = dirb["seuils"]
    taux = dirb["taux"]
    if verbose:
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

    if verbose:
        print("bareme après modif :")
        print(parameters.impot_revenu.bareme.get_at_instant(instant))

    return parameters, dir, instant, reform_period, verbose


def decote(args: tuple) -> tuple:
    parameters, dir, instant, reform_period, verbose = args
    dird = dir["decote"]
    seuil_celib = dird["seuil_celib"]
    seuil_couple = dird["seuil_couple"]
    taux = dird["taux"]
    if verbose:
        print("decote avant modif : ")
        print(
            parameters.impot_revenu.decote.seuil_celib.get_at_instant(instant),
            parameters.impot_revenu.decote.seuil_couple.get_at_instant(instant),
            parameters.impot_revenu.decote.taux.get_at_instant(instant),
        )
    parameters.impot_revenu.decote.seuil_celib.update(
        period=reform_period, value=float(seuil_celib)
    )
    parameters.impot_revenu.decote.seuil_couple.update(
        period=reform_period, value=float(seuil_couple)
    )
    parameters.impot_revenu.decote.taux.update(
        period=reform_period, value=float(taux) * 0.01
    )
    if verbose:
        print("decote apres modif : ")
        print(
            parameters.impot_revenu.decote.seuil_celib.get_at_instant(instant),
            parameters.impot_revenu.decote.seuil_couple.get_at_instant(instant),
            parameters.impot_revenu.decote.taux.get_at_instant(instant),
        )

    return parameters, dir, instant, reform_period, verbose


def plafond_qf(args: tuple) -> tuple:
    parameters, dir, instant, reform_period, verbose = args

    if verbose:
        print("plaf qf avant :")
        print(parameters.impot_revenu.plafond_qf.get_at_instant(instant))
    dirr = dir["plafond_qf"]

    # if "maries_ou_pacses" in requete["impot_revenu"]["plafond_qf"]:
    #     parameters.impot_revenu.plafond_qf.maries_ou_pacses.update(
    #         period=reform_period,
    #         value=requete["impot_revenu"]["plafond_qf"]["maries_ou_pacses"],
    #     )

    for var_name in [
        "maries_ou_pacses",
        "celib_enf",
        "celib",
        "reduc_postplafond",
        "reduc_postplafond_veuf",
    ]:
        if var_name in dirr:
            pp = eval("parameters.impot_revenu.plafond_qf.{}".format(var_name))
            pp.update(period=reform_period, value=float(dirr[var_name]))

    if "abat_dom" in dirr:
        paramstoprint = [
            parameters.impot_revenu.plafond_qf.abat_dom.taux_GuadMarReu,
            parameters.impot_revenu.plafond_qf.abat_dom.plaf_GuadMarReu,
            parameters.impot_revenu.plafond_qf.abat_dom.taux_GuyMay,
            parameters.impot_revenu.plafond_qf.abat_dom.plaf_GuyMay,
        ]
        if verbose:
            print("abat_dom avant modif : ")
            for pp in paramstoprint:
                print(pp.get_at_instant(instant))
        dirrr = dirr["abat_dom"]
        taux_GuadMarReu = dirrr["taux_GuadMarReu"]
        parameters.impot_revenu.plafond_qf.abat_dom.taux_GuadMarReu.update(
            period=reform_period, value=float(taux_GuadMarReu)
        )
        plaf_GuadMarReu = dirrr["plaf_GuadMarReu"]
        parameters.impot_revenu.plafond_qf.abat_dom.plaf_GuadMarReu.update(
            period=reform_period, value=float(plaf_GuadMarReu)
        )
        taux_GuyMay = dirrr["taux_GuyMay"]
        parameters.impot_revenu.plafond_qf.abat_dom.taux_GuyMay.update(
            period=reform_period, value=float(taux_GuyMay)
        )
        plaf_GuyMay = dirrr["plaf_GuyMay"]
        parameters.impot_revenu.plafond_qf.abat_dom.plaf_GuyMay.update(
            period=reform_period, value=float(plaf_GuyMay)
        )
    if "reduction_ss_condition_revenus" in dirr:
        dirrr = dirr["reduction_ss_condition_revenus"]
        for var_name in ["seuil_maj_enf", "seuil1", "seuil2", "taux"]:
            if var_name in dirrr:
                pp = eval(
                    "parameters.impot_revenu.plafond_qf.reduction_ss_condition_revenus.{}".format(
                        var_name
                    )
                )
                pp.update(period=reform_period, value=float(dirrr[var_name]))

    if verbose:
        print("plaf qf après :")
        print(parameters.impot_revenu.plafond_qf.get_at_instant(instant))

    return parameters, dir, instant, reform_period, verbose


def abattements_rni(args: tuple) -> tuple:
    parameters, dir, instant, reform_period, verbose = args
    if verbose:
        print("abattements_rni :")
        print(parameters.impot_revenu.abattements_rni.get_at_instant(instant))
    try:
        dirr = dir["abattements_rni"]["personne_agee_ou_invalide"]
    except KeyError:
        dirr = {}
    print(dirr)
    print("au cas ou", dir)
    # if "maries_ou_pacses" in requete["impot_revenu"]["plafond_qf"]:
    #     parameters.impot_revenu.plafond_qf.maries_ou_pacses.update(
    #         period=reform_period,
    #         value=requete["impot_revenu"]["plafond_qf"]["maries_ou_pacses"],
    #     )

    for var_name in ["montant_1", "montant_2", "plafond_1", "plafond_2"]:
        if var_name in dirr:
            pp = eval(
                "parameters.impot_revenu.abattements_rni.personne_agee_ou_invalide.{}".format(
                    var_name
                )
            )
            pp.update(period=reform_period, value=float(dirr[var_name]))

    if verbose:
        print("abattements_rni après :")
        print(parameters.impot_revenu.abattements_rni.get_at_instant(instant))

    return parameters, dir, instant, reform_period, verbose


def mapping() -> dict:
    return {
        "decote": decote,
        "bareme": bareme,
        "plafond_qf": plafond_qf,
        "abattements_rni": abattements_rni,
    }

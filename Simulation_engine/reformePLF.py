reforme_base = {
    "impot_revenu": {
        "bareme": {
            "seuils": [9964, 27519, 73779, 156244],
            "taux": [0.14, 0.3, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 1196, "seuil_couple": 1970, "taux": 0.75},
        "plafond_qf": {
            "abat_dom": {
                "plaf_GuadMarReu": 2450,
                "plaf_GuyMay": 4050,
                "taux_GuadMarReu": 0.3,
                "taux_GuyMay": 0.4,
            },
            "celib": 927,
            "celib_enf": 3660,
            "maries_ou_pacses": 1551,
            "reduc_postplafond": 1547,
            "reduc_postplafond_veuf": 1728,
            "reduction_ss_condition_revenus": {
                "seuil1": 18984,
                "seuil2": 21036,
                "seuil_maj_enf": 3797,
                "taux": 0.2,
            },
        },
        "calculNombreParts": {
            "partsSelonNombrePAC": [
                {"veuf": 1, "mariesOuPacses": 2, "celibataire": 1, "divorce": 1},
                {
                    "veuf": 2.5,
                    "mariesOuPacses": 2.5,
                    "celibataire": 1.5,
                    "divorce": 1.5,
                },
                {"veuf": 3, "mariesOuPacses": 3, "celibataire": 2, "divorce": 2},
                {"veuf": 4, "mariesOuPacses": 4, "celibataire": 3, "divorce": 3},
                {"veuf": 5, "mariesOuPacses": 5, "celibataire": 4, "divorce": 4},
                {"veuf": 6, "mariesOuPacses": 6, "celibataire": 5, "divorce": 5},
                {"veuf": 7, "mariesOuPacses": 7, "celibataire": 6, "divorce": 6},
            ],
            "partsParPACAuDela": 1,  # Le "Et ainsi de suite..." pour toute PAC au-delà du tableau "partsSelonNombrePAC".
            "partsParPACChargePartagee": {  # On a maintenant 12 cas différents en fonction du nobre d'enfants.
                "zeroChargePrincipale": {"deuxPremiers": 0.25, "suivants": 0.5},
                "unChargePrincipale": {"premier": 0.25, "suivants": 0.5},
                "deuxOuPlusChargePrincipale": {"suivants": 0.5},
            },
            "bonusParentIsole": {
                "auMoinsUnChargePrincipale": 0.5,
                "zeroChargePrincipaleUnPartage": 0.25,
                "zeroChargeprincipaleDeuxOuPlusPartage": 0.5,
            },
        },
    }
}


reforme_base_inflatee = {
    "impot_revenu": {
        "bareme": {
            "seuils": [int(k * 1.01 + 0.5) for k in [9964, 27519, 73779, 156244]],
            "taux": [0.14, 0.3, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 1196, "seuil_couple": 1970, "taux": 0.75},
        "plafond_qf": {
            "abat_dom": {
                "plaf_GuadMarReu": 2450,
                "plaf_GuyMay": 4050,
                "taux_GuadMarReu": 0.3,
                "taux_GuyMay": 0.4,
            },
            "celib": 936,
            "celib_enf": 3697,
            "maries_ou_pacses": 1567,
            "reduc_postplafond": 1562,
            "reduc_postplafond_veuf": 1745,
            "reduction_ss_condition_revenus": {
                "seuil1": 18984,
                "seuil2": 21036,
                "seuil_maj_enf": 3797,
                "taux": 0.2,
            },
        },
    }
}

only_reforme = {
    "impot_revenu": {
        "bareme": {
            "seuils": [int(k / 1.01) for k in [10064, 25659, 73369, 157806]],
            "taux": [0.11, 0.3, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 777, "seuil_couple": 1286, "taux": 0.4525},
        "plafond_qf": {
            "abat_dom": {
                "plaf_GuadMarReu": 2450,
                "plaf_GuyMay": 4050,
                "taux_GuadMarReu": 0.3,
                "taux_GuyMay": 0.4,
            },
            "celib": 927,
            "celib_enf": 3660,
            "maries_ou_pacses": 1551,
            "reduc_postplafond": 1547,
            "reduc_postplafond_veuf": 1728,
            "reduction_ss_condition_revenus": {
                "seuil1": 18984,
                "seuil2": 21036,
                "seuil_maj_enf": 3797,
                "taux": 0,
            },
        },
    }
}


reforme_PLF_2020 = {
    "impot_revenu": {
        "bareme": {
            "seuils": [10064, 25659, 73369, 157806],
            "taux": [0.11, 0.3, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 777, "seuil_couple": 1286, "taux": 0.4525},
        "plafond_qf": {
            "abat_dom": {
                "plaf_GuadMarReu": 2450,
                "plaf_GuyMay": 4050,
                "taux_GuadMarReu": 0.3,
                "taux_GuyMay": 0.4,
            },
            "celib": 936,
            "celib_enf": 3697,
            "maries_ou_pacses": 1567,
            "reduc_postplafond": 1562,
            "reduc_postplafond_veuf": 1745,
            "reduction_ss_condition_revenus": {
                "seuil1": 18984,
                "seuil2": 21036,
                "seuil_maj_enf": 3797,
                "taux": 0,
            },
        },
    }
}

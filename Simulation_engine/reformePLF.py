reformePLF = {
    "impot_revenu": {
        "bareme": {
            "seuils": [9964, 25405, 72643, 156244],
            "taux": [0.11, 0.3, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 768, "seuil_couple": 1272, "taux": 0.45},
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

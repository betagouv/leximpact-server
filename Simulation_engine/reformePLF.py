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
        "calcul_nombre_parts": {
            "parts_selon_nombre_personnes_a_charge":{  #Contenu du tableau, 4  cas distincts
                "veuf":[1, 2.5, 3, 4, 5, 6, 7],
                "maries_ou_pacses":[2, 2.5, 3, 4, 5, 6, 7],
                "celibataire" : [1, 1.5, 2, 3, 4, 5, 6],
                "divorce" : [1, 1.5, 2, 3, 4, 5, 6],
            },
            "parts_par_pac_au_dela" : 1, # LE "Et ainsi de suite..."
            "nombre_de_parts_charge_partagee":{ #On a maintenant 12 cas différents en fonction du nobre d'enfants. 
                "zero_charge_principale": {
                    "deux_premiers" : 0.25, 
                    "suivants" : 0.5,
                },
                "un_charge_principale": {
                    "premier" : 0.25, 
                    "suivants" : 0.5,
                },
                "deux_ou_plus_charge_principale" :  {
                    "suivants" : 0.5,
                },
            },
            #Pfff c vraiment la pire paramétrisation du monde, ca contraint énormément la réflexion

        },
    },
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

import pandas as pd
from time import time
import sys

starttime = time()

rfrs = pd.read_csv("JusteRFR.txt")

rfrs.loc[rfrs["revkire"].isna(), "revkire"] = 0

nbff = len(rfrs)

# pas du tout optimal en temps de calcul mais bon
# Les seuils ont vocation à offrir une granularité meilleure que l'existant.
# On va faire à la main, je dirais qu'on a envie d'un peu plus de lignes mais pas forcément beaucoup.
# Essayons de mettre :
# - maximum 5% de la population dans chaque tranche
# - Meilleure estimation des hauts revenus (on peut monter jusqu'à 20_000_000 de rfr
# sans mettre à mal le SS : il y a >400 FF au dessus de 10M de RFR.

seuils = [0, 1, 1500, 3714, 5000, 7000, 9168, 10000, 12000, 13500,
        15000, 16000, 17000, 18000, 19221, 21000, 23314, 25000,
        28000, 30000, 33000, 35000, 37500, 40000, 42500, 45000,
        47500, 50000, 60000, 75000, 100000]

while seuils[-1] < 20_000_000:
    seuils + = [int(seuils[-1] * 1.3)]

seuils += [50_000_000]

print(f"j'ai {len(seuils)} seuils")
pops = []
sumrevs = []

nombre_personnes_tranche = nbff
min_pt = nbff
max_poids = 0

with open("CalibPOTE.txt", "w") as f:
    f.write("Rk,Nk,Ark\n")

    for seuil in seuils:
        filtered_above_seuil = rfrs[rfrs["revkire"] >= seuil]
        nb_above_seuil = len(filtered_above_seuil)
        sum_above_seuil = sum(filtered_above_seuil["revkire"])
        pops += [nb_above_seuil]
        sumrevs += [sum_above_seuil]
        highest_rfr = (seuil - 1)
        if len(pops) > = 2:
            nombre_personnes_tranche = pops[-2] - pops[-1]
        # print(sumrevs, highest_rfr)
        poids_plus_gros_ff = (highest_rfr / (sumrevs[-2] - sumrevs[-1])) if highest_rfr > 0 else 0
        '''Cet extrait a été fabriqué par la procédure suivante :
        - Extraction de la variable revkire (Revenu fiscal de référence du ménage) du fichier POTE 2018
        - A partir de ce fichier, on extrait un fichier texte qui contient pour un certain nombre de seuils (54) :
        - le nombre de foyers fiscaux ayant un revenu supérieur ‡ ce seuil
        - le revenu moyen des foyers fiscaux ayant un revenu supérieur ‡ ce seuil '''
        print(seuil,
              nb_above_seuil,
              nb_above_seuil / nbff,
              sum_above_seuil / nb_above_seuil,
              "nombres foyers tranches (doit être >12)", nombre_personnes_tranche,
              "poids plus haut revenu (doit être <85%)", poids_plus_gros_ff)
        min_pt = min(min_pt, nombre_personnes_tranche)
        max_poids = max(poids_plus_gros_ff, max_poids)
        f.write(f"{seuil},{nb_above_seuil / nbff},{sum_above_seuil / nb_above_seuil}\n")
    print("last population", pops[-1], "last weight", rfrs["revkire"].max() / sumrevs[-1])
    min_pt = min(min_pt, pops[-1])
    max_poids = max(max_poids, rfrs["revkire"].max() / sumrevs[-1])

sys.stderr.write(f"Well done, elapsed = {time()-starttime : .2f}, smallest tranche : {min_pt}, poids maximum d'un FF dans une tranche {max_poids*100:.2f}%")

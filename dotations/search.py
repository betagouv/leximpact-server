from dotations.load_dgcl_data import load_dgcl_file  # type: ignore
import pandas as pd  # type: ignore
from utils.folder_finder import path_folder_assets  # type: ignore


cached_data = None

# Charge un dictionnaire des communes, afin d'effectuer des recherches textuelles sur le nom de la commune.


def load_cached_data():
    global cached_data
    if cached_data is None:  # Dictionary of communes is only loaded once
        communes = load_dgcl_file()
        colonnes_a_garder = {
            "Informations générales - Code INSEE de la commune": "code",
            "Informations générales - Nom de la commune": "name",
            "Informations générales - Code département de la commune": "code_departement",
            "Informations générales - Population INSEE Année N ": "habitants",
            "Potentiel fiscal et financier des communes - Potentiel financier par habitant": "potentielFinancierParHab"
        }

        df_base = communes[list(colonnes_a_garder.keys())]

        # Translation of fields towards less cumbersome names
        df_base.columns = [colonnes_a_garder[col] for col in df_base.columns]
        # Make sure the department code has at least two characters
        df_base["code_departement"] = df_base["code_departement"].astype(str).apply(lambda x: str(x).zfill(2))
        # Le fichier de liste des départements est présent en ligne sur :
        # https://www.data.gouv.fr/fr/datasets/r/70cef74f-70b1-495a-8500-c089229c0254
        path_assets = path_folder_assets()
        liste_departements = pd.read_csv(path_assets + "/data/departements-france.csv", dtype=str)

        communes_avec_departement = df_base.merge(liste_departements, how="left", on="code_departement")
        communes_avec_departement.loc[communes_avec_departement["nom_departement"].isnull(), "nom_departement"] = communes_avec_departement["code_departement"]
        communes_avec_departement.columns = [col if col != "nom_departement" else "departement" for col in communes_avec_departement.columns]

        dict_result = communes_avec_departement[["code", "name", "habitants", "potentielFinancierParHab", "departement"]].to_dict(orient="records")
        cached_data = dict_result
    return cached_data


def search_commune_by_name(nom_commune):
    res = []
    resultats_maximum = 20
    for commune in load_cached_data():
        if nom_commune.upper() in commune["name"]:
            res += [commune]
        if len(res) >= resultats_maximum:
            break
    return res

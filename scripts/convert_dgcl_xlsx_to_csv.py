import pandas as pd  # type: ignore


def convert_col_names_2020_to_2019(data):
    # Modifies column names that cchanged between 2019 and 2020
    # We give them the name they had in 2019, cause our loader uses these.
    dict_convert = {
        "Dotation de solidarité rurale - Cible - IS DSR Cible": "Dotation de solidarité rurale - Cible - Indice synthétique",
        "Dotation de solidarité rurale - Cible - Part Pfi": "Dotation de solidarité rurale - Cible - Part Pfi (avant garantie CN)",
        "Dotation de solidarité rurale - Cible - Part VOIRIE": "Dotation de solidarité rurale - Cible - Part VOIRIE (avant garantie CN)",
        "Dotation de solidarité rurale - Cible - Part ENFANTS": "Dotation de solidarité rurale - Cible - Part ENFANTS (avant garantie CN)",
        "Dotation de solidarité rurale - Cible - Part Pfi/hectare (Pfis)": "Dotation de solidarité rurale - Cible - Part Pfi/hectare (Pfis) (avant garantie CN)",
        "Informations générales - Population DGF de l'année N'": "Informations générales - Population DGF Année N'",
        "Informations générales - Strate démographique de l'année N": "Informations générales - Strate démographique Année N",
        "Informations générales - Population INSEE de l'année N": "Informations générales - Population INSEE Année N ",
        "Informations générales - Superficie année N": "Informations générales - Superficie 2019",
    }
    data.columns = [dict_convert[k] if k in dict_convert else k for k in data.columns]
    return data


def xlsxtocsv(filename):
    df = pd.read_excel(filename, header=[0, 1], dtype=str)  # Les noms de colonnes viennent sur 2 lignes dans le fichier DGCL.
    col_name_separator = " - "
    df.columns = df.columns.map(col_name_separator.join).str.strip(col_name_separator)  # On les concatène ainsi
    nom_fichier = filename.split(".")[0]
    df = df.replace(r'\.', ",", regex=True)
    df = convert_col_names_2020_to_2019(df)
    df.to_csv(nom_fichier + ".csv", index=False, decimal=",")

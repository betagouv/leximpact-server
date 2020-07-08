# Vérifications au format pytest mais elles ne seront pas exécutées automatiquement
# avec les autres tests grâce à un nom de fichier ne démarrant pas par "test".
from pytest import fixture  # type: ignore

from dotations.load_dgcl_data import nom_comm, code_comm, load_dgcl_file  # type: ignore


nb_communes_guadeloupe = 32
nb_communes_martinique = 34

# 24 lignes Guyane dans le document DGCL
# = 22 communes + 2 arrondissements
# https://www.insee.fr/fr/metadonnees/cog/departement/DEP973-guyane
nb_communes_guyane = 22
nb_arrondissements_guyane = 2  # Cayenne + Saint-Laurent-du-Maroni

nb_communes_la_reunion = 24
nb_communes_saint_pierre_et_miquelon = 2
nb_communes_mayotte = 17
nb_communes_saint_barthelemy = 0

# À vérifier : absent de la DGCL mais 1 commune sur site INSEE
# https://www.insee.fr/fr/information/2028040#st-martin
nb_communes_saint_martin = 0

nb_communes_terres_australes_et_antarctiques_francaises = 0

# https://www.insee.fr/fr/information/2028040#wallis-futuna
nb_communes_wallis_et_futuna = 3

nb_communes_polynesie_francaise = 48
nb_communes_nouvelle_caledonie = 33
nb_communes_clipperton = 0


@fixture(scope="session", autouse=True)
def loaded_data():
    return load_dgcl_file()


def test_communes_outre_mer(loaded_data):
    # https://fr.wikipedia.org/wiki/France_d%27outre-mer
    departement = "Informations générales - Code département de la commune"

    code_insee_guadeloupe = 971
    communes_guadeloupe = loaded_data.loc[loaded_data[departement] == code_insee_guadeloupe]
    code_communes_guadeloupe = communes_guadeloupe[code_comm]
    assert code_communes_guadeloupe.count() == nb_communes_guadeloupe

    code_insee_martinique = 972
    communes_martinique = loaded_data.loc[loaded_data[departement] == code_insee_martinique]
    code_communes_martinique = communes_martinique[code_comm]
    assert code_communes_martinique.count() == nb_communes_martinique

    code_insee_guyane = 973
    communes_guyane = loaded_data.loc[loaded_data[departement] == code_insee_guyane]
    code_communes_guyane = communes_guyane[code_comm]
    assert code_communes_guyane.count() == nb_communes_guyane, communes_guyane[nom_comm]

    code_insee_la_reunion = 974
    communes_la_reunion = loaded_data.loc[loaded_data[departement] == code_insee_la_reunion]
    code_communes_la_reunion = communes_la_reunion[code_comm]
    assert code_communes_la_reunion.count() == nb_communes_la_reunion

    code_insee_saint_pierre_et_miquelon = 975
    communes_saint_pierre_et_miquelon = loaded_data.loc[loaded_data[departement] == code_insee_saint_pierre_et_miquelon]
    code_communes_saint_pierre_et_miquelon = communes_saint_pierre_et_miquelon[code_comm]
    assert code_communes_saint_pierre_et_miquelon.count() == nb_communes_saint_pierre_et_miquelon

    code_insee_mayotte = 976
    communes_mayotte = loaded_data.loc[loaded_data[departement] == code_insee_mayotte]
    code_communes_mayotte = communes_mayotte[code_comm]
    assert code_communes_mayotte.count() == nb_communes_mayotte

    code_insee_saint_barthelemy = 977
    communes_saint_barthelemy = loaded_data.loc[loaded_data[departement] == code_insee_saint_barthelemy]
    code_communes_saint_barthelemy = communes_saint_barthelemy[code_comm]
    # https://fr.wikipedia.org/wiki/Saint-Barthélemy_(Antilles_françaises)
    # "l'île devient, le 15 juillet 2007, officiellement collectivité d'outre-mer :
    # la commune de Saint-Barthélemy est dissoute, de même que l’arrondissement départemental et le canton"
    assert code_communes_saint_barthelemy.count() == nb_communes_saint_barthelemy

    code_insee_saint_martin = 978
    communes_saint_martin = loaded_data.loc[loaded_data[departement] == code_insee_saint_martin]
    code_communes_saint_martin = communes_saint_martin[code_comm]
    assert code_communes_saint_martin.count() == nb_communes_saint_martin

    code_insee_terres_australes_et_antarctiques_francaises = 984
    communes_terres_australes_et_antarctiques_francaises = loaded_data.loc[loaded_data[departement] == code_insee_terres_australes_et_antarctiques_francaises]
    code_communes_terres_australes_et_antarctiques_francaises = communes_terres_australes_et_antarctiques_francaises[code_comm]
    # https://fr.wikipedia.org/wiki/Terres_australes_et_antarctiques_françaises
    # "territoire administré depuis Saint-Pierre, à La Réunion"
    assert code_communes_terres_australes_et_antarctiques_francaises.count() == nb_communes_terres_australes_et_antarctiques_francaises

    code_insee_wallis_et_futuna = 986
    communes_wallis_et_futuna = loaded_data.loc[loaded_data[departement] == code_insee_wallis_et_futuna]
    code_communes_wallis_et_futuna = communes_wallis_et_futuna[code_comm]
    assert code_communes_wallis_et_futuna.count() == nb_communes_wallis_et_futuna

    code_insee_polynesie_francaise = 987
    communes_polynesie_francaise = loaded_data.loc[loaded_data[departement] == code_insee_polynesie_francaise]
    code_communes_polynesie_francaise = communes_polynesie_francaise[code_comm]
    assert code_communes_polynesie_francaise.count() == nb_communes_polynesie_francaise

    code_insee_nouvelle_caledonie = 988
    communes_nouvelle_caledonie = loaded_data.loc[loaded_data[departement] == code_insee_nouvelle_caledonie]
    code_communes_nouvelle_caledonie = communes_nouvelle_caledonie[code_comm]
    assert code_communes_nouvelle_caledonie.count() == nb_communes_nouvelle_caledonie

    code_insee_clipperton = 989
    communes_clipperton = loaded_data.loc[loaded_data[departement] == code_insee_clipperton]
    code_communes_clipperton = communes_clipperton[code_comm]
    # https://fr.wikipedia.org/wiki/Île_Clipperton
    # "Possession française sous l'autorité directe du gouvernement"
    assert code_communes_clipperton.count() == nb_communes_clipperton

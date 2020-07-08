from pytest import fixture

from dotations.load_dgcl_data import (
    code_comm,
    load_dgcl_file,
    ajoute_population_plus_grande_commune_agglomeration,
    ajuste_part_communes_canton,
    ajoute_appartenance_outre_mer,
    ajoute_est_chef_lieu_canton,
    ajoute_population_chef_lieu_canton,
    corrige_revenu_moyen_strate
)

from check_dgcl_data import (
    nb_communes_guadeloupe,
    nb_communes_martinique,
    nb_communes_guyane,
    nb_communes_la_reunion,
    nb_communes_saint_pierre_et_miquelon,
    nb_communes_mayotte,
    nb_communes_saint_barthelemy,
    nb_communes_saint_martin,
    nb_communes_terres_australes_et_antarctiques_francaises,
    nb_communes_wallis_et_futuna,
    nb_communes_polynesie_francaise,
    nb_communes_nouvelle_caledonie,
    nb_communes_clipperton
)


@fixture(scope="session", autouse=True)  # ne charger le fichier qu'une fois pour tous les tests
def loaded_data():
    return load_dgcl_file()


def test_ajoute_appartenance_outre_mer(loaded_data):
    # https://fr.wikipedia.org/wiki/Liste_des_communes_de_la_France_d%27outre-mer
    nombre_communes_outre_mer = (
        nb_communes_guadeloupe
        + nb_communes_martinique
        + nb_communes_guyane
        + nb_communes_la_reunion
        + nb_communes_saint_pierre_et_miquelon
        + nb_communes_mayotte
        + nb_communes_saint_barthelemy
        + nb_communes_saint_martin
        + nb_communes_terres_australes_et_antarctiques_francaises
        + nb_communes_wallis_et_futuna
        + nb_communes_polynesie_francaise
        + nb_communes_nouvelle_caledonie
        + nb_communes_clipperton
    )

    outre_mer_dgcl = "commune d'outre mer"
    data = ajoute_appartenance_outre_mer(loaded_data, outre_mer_dgcl)

    assert data[outre_mer_dgcl] is not None
    assert data[outre_mer_dgcl].loc[data[outre_mer_dgcl] == True].count() == nombre_communes_outre_mer

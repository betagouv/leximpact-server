from pytest import fixture  # type: ignore
from pandas import DataFrame  # type: ignore

from dotations.load_dgcl_data import (  # type: ignore
    variables_openfisca_presentes_fichier,
    load_dgcl_file,
    ajoute_population_plus_grande_commune_agglomeration,
    # ajuste_part_communes_canton,
    ajoute_appartenance_outre_mer,
    # ajoute_est_chef_lieu_canton,
    # ajoute_population_chef_lieu_canton,
    # corrige_revenu_moyen_strate,
    # corrige_revenu_moyen_commune
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
)  # type: ignore


@fixture(scope="session", autouse=True)  # ne charger le fichier qu'une fois pour tous les tests
def loaded_data():
    return load_dgcl_file()


@fixture
def table_openfisca_to_dgcl_column():
    return variables_openfisca_presentes_fichier


def test_ajoute_population_plus_grande_commune_agglomeration(table_openfisca_to_dgcl_column):
    dgcl_pop_agglo = "Dotation de solidarité rurale Bourg-centre - Population DGF des communes de l'agglomération"
    dgcl_pop_dgf = "Informations générales - Population DGF Année N'"

    # une ligne par commune de test
    input_data = DataFrame(data={
        dgcl_pop_agglo: [500, 100, 500],
        dgcl_pop_dgf: [1, 2, 3]  # par commune
    })

    plus_grosse_commune = "Population plus grande commune de l'agglomération"
    result_data = ajoute_population_plus_grande_commune_agglomeration(
        table_openfisca_to_dgcl_column, input_data, plus_grosse_commune)

    assert result_data.count(axis='columns')[0] == input_data.count(axis='columns')[0] + 1
    assert result_data[plus_grosse_commune].dtype == 'int64'
    assert result_data[plus_grosse_commune].tolist() == [3, 2, 3]


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
    assert data[outre_mer_dgcl].loc[data[outre_mer_dgcl]].count() == nombre_communes_outre_mer

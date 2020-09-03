from dotations.search import search


def test_paris():
    # Verifie les champs renvoyés
    recherche_resultats = search("paris")
    # Au moins un resultat
    assert len(recherche_resultats)>=1
    # Chaque élément du résultat contient les bons champs
    for resultat in recherche_resultats:
        for champ in ["code", "name", "departement", "potentielFinancier", "habitants"]:
            assert champ in resultat

def test_nombre_max_resultats():
    # Verifie les champs renvoyés
    recherche_resultats = search("a")
    assert len(recherche_resultats)==20
    # Chaque élément du résultat contient les bons champs
    for resultat in recherche_resultats:
        for champ in ["code", "name", "departement", "potentielFinancier", "habitants"]:
            assert champ in resultat
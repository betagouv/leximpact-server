# LexImpact

Dépôt du défi LexImpact du programme Entrepreneur·e d'Intérêt Général


* [Fiche du défi](https://entrepreneur-interet-general.etalab.gouv.fr/defis/2019/leximpact.html)

* [Fiche produit](https://beta.gouv.fr/startups/leximpact.html)

## Installation


```sh
make install
```

## Exécuter

**Mode demo**

Le mode demo lance dans localhost:8050 une version locale du serveur

```sh
make run
```

ou


```sh
python interface_reform/app.py
```

**Mode API**

Le mode API sépare Leximpact en deux éléments :

- Une API qui effectue les calculs openfisca, se trouve par défaut sur le serveur localhost:5000  et se lance par :

```sh
cd server
python app.py
```

- L'interface en mode API : Une fois qu'une API existe, le serveur 
peut requêter cette API (et ne nécessite plus l'installation d'openfisca). 
Pour ce faire, l'app doit être lancée comme décrite plus haut, en prenant soin de modifier le flag dans interface_reform/app.py

```python
API_mode = (
    True  #au lieu de False par défaut
)
```

**Mode graphes population**

Par défaut, seul un graph de cas-types est présent. Dans le cas où une base de 
données représentant la population française (non inclus dans la bibliothèque) est présente
sur l'ordinateur d'exécution, des graphes d'impacts généraux sur la population  peuvent être affichés 
en sélectionnant dans  interface_reform/app.py.  

**ATTENTION** : Ce mode est très peu documenté et indicatif, l'équipe de développement ne disposant pas à ce stade de véritable jeu de données.

```python
version_beta_sans_graph_pop = False  #Au lieu de True par défaut
```



## Test

```sh
make test
```

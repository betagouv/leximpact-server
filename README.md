# LexImpact-Server

## [EN] Introduction
LexImpact allows civil servants, policy makers and citizens to simulate the _ex ante_ impact of a reform to a country's tax-benefit system.
* [Call for candidates (FR)](https://entrepreneur-interet-general.etalab.gouv.fr/defis/2019/leximpact.html)
* [Elevator pitch (FR)](https://beta.gouv.fr/startups/leximpact.html)
* [LexImpact](https://leximpact.an.fr)

## [FR] Introduction
LexImpact permet aux administrations, aux parlementaires et à la société civile de simuler l'impact _ex ante_ des réformes au système socio-fiscal.
* [Appels à candidatures](https://entrepreneur-interet-general.etalab.gouv.fr/defis/2019/leximpact.html)
* [Fiche produit](https://beta.gouv.fr/startups/leximpact.html)
* [LexImpact](https://leximpact.an.fr)

Leximpact est constitué de deux parties :
- [Leximpact-server](https://github.com/betagouv/leximpact-server/) : interface en python utilisant openfisca permettant de mettre en place une API répondant à des questions sur l'impact de modifications de la loi fiscale
- [Leximpact-client](https://github.com/betagouv/leximpact-client/) : interface web communiquant avec l'API qui met à disposition des usagers un site web permettant de visulaliser les résultats des calculs de l'API

## Installation

Cette application requiert [Python 3.7](https://www.python.org/downloads/release/python-370/) et [pip](https://pip.pypa.io/en/stable/installing/).

Plateformes supportées :
- distributions GNU/Linux (en particulier Debian and Ubuntu) ;
- Mac OS X ;
- Windows;

Pour les autres OS : si vous pouvez exécuter Python et Numpy, l'installation de LexImpact-Server devrait fonctionner.

### Installez un environnement virtuel

Nous recommandons l'utilisation d'un [environnement virtuel](https://virtualenv.pypa.io/en/stable/) (_virtualenv_) avec un gestionnaire de _virtualenv_ tel que [Pyenv](https://github.com/pyenv/pyenv).

- Un _[virtualenv](https://virtualenv.pypa.io/en/stable/)_ crée un environnement pour les besoins spécifiques du projet sur lequel vous travaillez.
- Un gestionnaire de _virtualenv_, tel que [Pyenv](https://github.com/pyenv/pyenv), vous permet de facilement créer, supprimer et naviguer entre différents projets.

Pour installer Pyenv (macOS), lancez une fenêtre de terminal et suivez ces instructions :

```sh
brew update
brew install pyenv
brew install pyenv-virtualenv
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
exec "$SHELL"
```

Créez un nouveau _virtualenv_ nommé **leximpact-server** et configurez-le avec python 3.7 :

```sh
pyenv install 3.7.3
pyenv virtualenv 3.7.3 leximpact-server-3.7.3
pyenv activate leximpact-server-3.7.3
```

Le  _virtualenv_ **leximpact-server** sera alors activé, c'est-à-dire que les commandes suivantes s'exécuteront directement dans l'environnement virtuel.

Bravo :tada: Vous êtes prêt·e à installer LexImpact-Server !

### Installez LexImpact-Server

Pour installer LexImpact-Server, dans votre fenêtre de terminal :

```sh
make install
```

ou sous Windows 

```sh
pip install --editable .[dev]
```

🎉 Félicitations LexImpact-Server est prêt à être utilisé !

## Lancez l'API Web LexImpact

### Fichier de configuration `.env`


ℹ️ Uniquement nécessaire dans le cas où les données sur la population sont utilisées (fonctionnalité simpop). En l'absence d'utilisation de ces fonctionnalités (i.e. les endpoints auth et simpop), il devrait être possible de faire tourner Leximpact-server sans base de données ni fichier `.env` .

Pour lancer LexImpact-Server, vous devez tout d'abord créer un fichier de configuration `.env`. Le fichier `.env.example` contient un exemple de fichier de configuration `.env`, les champs y apparaissant sont :

- `DATABASE_*` : décrit la configuration de la base de données, leximpact-server doit avoit un accès à une base de données postgres lui permettant de se comporter correctement 
- `JWT_*` : Décrit les caractéristique du [JSON Web Token](https://jwt.io/). `JWT_SECRET` est une clef privée, `JWT_AUDIENCE` et `JWT_ISSUER` sont vérifiés quand le token est vérifié, mais peuvent être lu par quiconque a un token (car ces derniers ne sont pas chiffrés, mais juste signés par une clef privée)
- `MAILJET_*` : données d'authentification pour Mailjet, qui est utilisé pour envoyer les emails contenant les liens de connexion.
- `POPULATION_TABLE_PATH` :  Les données de population prises en compte dans la simulation du budget de l'État. Peut contenir un nom de fichier (.csv ou .h5) ou un nom de table dans la base SQL. Cette source de données sera importée. Un exemple de fichier fonctionnnant comme source de données situé dans le dépôt est `DCT.csv`. Des fonctions pour calibrer une source de données en fonction des données existantes de la population française sont disponibles dans le fichier sous `./scripts` (utilisés notamment dans le script `TransformData.py`) 
- `NAME_TABLE_BASE_RESULTS` : Table SQL, générée par le script generate_default_results.csv, qui contient les résultats de la population pour les calculs réutilisés (i.e. code existant et PLF) utilisée pour économiser du temps de calcul.
- `RECETTES_ETAT_EURO` : Valeur (entière) représentant le montant total de l'impôt attendu avec le code existant. Les résultats sur l'échantillon de population sont ajustés pour matcher cet ordre de grandeur pour le code existant. Si la valeur n'est pas spécifiée, aucun ajustement n'a lieu sur les résultats bruts de la simulation.
- `YEAR_COMPUTATION` : Année de calcul : les revenus des cas-types et de la population seront supposés survenir l'année spécifiée, et seront donc taxés aux taux applicables cette année là.
- `PLF_PATH` : Contient le chemin où l'on peut trouver un dictionnaire représentant la réforme.  Un plf_path écrit au format "dossier.sousdossier.fichier.nom_dictionnaire" importera le dictionnaire portant le nom "nom_dictionnaire" dans le fichier "dossier/sousdossier/fichier.py" de l'arborescence. Cette variable fera planter le programme si elle contient des espaces ou le caractère ';', pour éviter toute fausse manipulation de l'utilisateur.


Variable optionnelle :
- `ASSETS_PATH` : Par défaut, le folder /assets/ contient toutes les données publiques utiles au calcul des simulations. Il est toutefois possible pour l'usager de déclarer sa propre adresse de fichier dans cette variable d'environnement, qui doit être un chemin de répertoire valide.

### Base de données et migrations

Pour créer la base de données, et exécuter toutes les migrations, dans votre fenêtre de terminal :

```sh
make migrate
```

### Mode demo

Pour lancer LexImpact-Server, dans votre fenêtre de terminal :

```sh
make run
```

Pour s'assurer que tout marche bien :

```sh
./tests/server/stress/test.sh
```

🎉 Félicitations LexImpact-Server est en train de tourner !

### Mode agrégats de population

Par défaut, seul de résultats à partir de cas-types sont présents dans l'API.

Dans le cas où une base de données représentant la population française (non incluse dans la bibliothèque) est présente sur l'ordinateur d'exécution, des agrégats d'impact (budgétaire, redistributif...) seront inclus dans les réponses de l'API.

Cette documentation a vocation à expliquer la marche à suivre à partir du moment où l'usager dispose d'un fichier .h5 ou csv représentatif de la population contenant pour chaque personne physique :
- des variables openfisca suffisantes au calcul de l'impôt sur le revenu
- des identifiants permettant d'identifier les entités (ménage, famille, foyer fiscal) auxquelles appartient chaque personne, et son rôle en leurs seins.
- une variable wprm, indiquant le poids du foyer fiscal dans la simulation

Un exemple de fichier ayant ce format est le fichier DCT.csv du repo. A ce stade, il n'existe pas de fichier public contenant ces données pour un échantillon représentatif de la population.

Le fichier source peut être transformé par le script Transformdata.py qui fournit un jeu d'utilitaires pour anonymiser et calibrer les données sources.

#### le script Transformdata.py

4 fonctions sont composées quand ce script est lancé. Chacune des fonctions prend en argument un fichier source, et un fichier destination. Avant de lancer ce script, il convient de modifier les noms initiaux et finaux de fichiers sources pour correspondre à ceux dont l'usager dispose.

* test_useless_variables : retire les colonnes inutiles du fichier source, c'est à dire les colonnes qui n'ont aucun impact sur le résultat des trois variables openfisca "rfr", "irpp" et "nbptr" dans le cadre d'un calcul sur le fichier source. Il est à noter que cet algorithme ne garantit pas que les colonnes ignorées n'auront aucun impact dans aucune situation simulable via LexImpact
* inflate : ajuste les données pour prendre en compte le temps écoulé entre le moment où les données ont été générées et le moment où la simulation est lancée : les poids des foyers fiscaux sont ajustés pour prendre en compte l'évolution du nombre de foyers fiscaux sur la période , et les variables exprimées en euros sont ajustées de l'inflation. Ces deux variables sont paramétrables dans le code.
* noise : un bruit gaussien de 2% (paramétrable dans le code) est ajouté sur les variables continues pouvant potentiellement servir à une réidentification.
* ajustement_h5 : ajuste les revenus des foyers fiscaux par une fonction croissante qui permet à la distribution des revenus finale d'épouser le plus précisément possible une distribution spécifiée par l'utilisateur. Un exemple d'une telle distribution figure dans le repo, estimée en s'appuyant sur des données publiques agrégées publiées par [la DGFiP](https://www.impots.gouv.fr/portail/statistiques) et un rapport du Sénat. 

Le fichier obtenu peut désormais figurer dans la variable d'environnement POPULATION_TABLE_PATH

🎉 Félicitations, vous-êtes en train de réformer le système socio-fiscal français !

## Testing

Pour faire tourner les tests de LexImpact-Server, exécutez la commande suivante :

```sh
make test
```

Pour faire tourner les tests de performance de LexImpact-Server :

```sh
make stress-server
```

Puis, dans une nouvelle fenêtre, lancez :

```sh
make stress-test
```

## Style

Ce dépôt adhère à un style de code précis, et on vous invite à le suivre pour que vos contributions soient intégrées au plus vite.

L'analyse de style est déjà exécutée avec `make test`. Pour le faire tourner de façon indépendante :

```sh
make check-style
```

Pour corriger les erreurs de style de façon automatique:

```sh
make format-style
```

Pour corriger les erreurs de style de façon automatique à chaque fois que vous faites un _commit_ :

```sh
touch .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

tee -a .git/hooks/pre-commit << END
#!/bin/sh
#
# Automatically format your code before committing.
exec make format-style
END
```


## Endpoints de l'API Web - Impôt sur le revenu

L'API Web dispose des itinéraires suivants :

* `/`
* `/metadata/description_cas_types`
* `/auth/login`
* `/calculate/compare`
* `/calculate/simpop`

Parmi ces itinéraires, deux nécessitent une vérification de l'identité de l'appelant :

* `/auth/login` : vérifie que l'email mentionné dans le corps est dans la base de données (si oui, lui envoie par mail un lien comportant un token)
* `/calculate/simpop` : vérifie que le token présent dans le corps de la requête est valide, non expiré, et n'appartient pas à un utilisateur suspendu

###  Itinéraire par défaut ou /

- Type : GET
- Description : Permet de vérifier que le serveur est en fonctionnement.
- Requête - contenu du body : None
- Réponse - contenu du body :

    ```json
    { "hello": "coucou" }
    ```

### /metadata/description_cas_types

- Type : POST
- Description :  Requête le serveur pour obtenir le contenu des cas types par défaut. Permet d'éviter de stocker le contenu de ces cas types dans le client. 
- Requête - contenu du body : None
- Réponse - contenu du body : `Array of objects`. Chaque objet décrit un foyer fiscal sous forme de nombre entier à travers le schéma suivant :

    ```
    { 
        "nb_anciens_combattants": 0, //nombre d'anciens combattants parmi les déclarants 
        "nb_decl_invalides": 0, //nombre d'invalides parmi les déclarants
        "nb_decl_parent_isole": 0, //nombre de parents isolés parmi les déclarants
        "nb_decl_veuf":  0, //nombre de veufs parmi les déclarants
        "nb_pac_charge_partagee":  0, //nombre de personnes à charge en charge partagée
        "nb_pac_invalides":  0, //nombre de personnes à charge invalides
        "nombre_declarants":  1, //nombre de déclarants (1 ou 2)
        "nombre_declarants_retraites":  0, //nombre de déclarants ayant plus de 65 ans
        "nombre_personnes_a_charge":  0, //nombre de personnes à charge
        "outre_mer":  0, //0 si métropole, 1 pour Guadeloupe/Martinique/Réunion, 2 pour Mayotte/Guyane
        "revenu":  15000, //en euros imposable pour l'ensemble du foyer fiscal
    }
    ```

###  /auth/login

- Type : POST
- Description : Soumet un email au serveur. Si cet email est dans la liste des adresses autorisées, un lien de connexion au service LexImpact IR à accès restreint est envoyé à l'adresse email spécifiée.
- Requête - contenu du body : Ne contient qu'un champ tel que décrit dans l'exemple suivant.

    ```json
    {
        "email" : "email@tester.io"
    }
    ```

- Réponse - contenu du body :  La réponse renvoyée sera toujours la même, afin d'éviter de donnner des informations sur la validité des adresses mail : juste une chaîne de caractères qui contient `Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation`.

Dans le cas où le mail demandé correspond aux critères de validité (être présent dans la table de données users ou avoir un nom de domaine en clb-an.fr), un email est envoyé via Mailjet (en utilisant les informations d'authentification présentes dans les variables d'environnement) à l'adresse email spécifiée contenant un lien vers le client incluant un token.

###  /calculate/compare

- Type : POST
- Description : On décrit au serveur une description de cas-types, et une réforme, et ce dernier nous renvoie l'effet de la réforme sur ces cas-types.
- Requête - contenu du body :

    ```
    {
        "reforme" : décrit la réforme,
        "deciles": deprecated - n'a plus d'impact,
        "description_cas_types": array de descriptions de cas-types (pour la structure, cf. le guide du endpoint 
        /metadata/description_cas_types) ; champ optionnel, si non fourni, utilise les descriptions de cas types par défaut,
        "timestamp" : chaîne de caractères qui sera renvoyé tel quel par le programme ; champ optionnel, si non fourni, la réponse ne contiendra pas de champ "timestamp"
    }
    ``` 

En version `1.1.0` de la [spécification de l'API Web](./server/api.yaml), la structure de la réforme étend les possibilités d'amendement du quotient familial et cela est défini par un nouveau champ `calculNombreParts`. 

Elle reproduit presque la structure d'OpenFisca-France. Si un paramètre est omis, il est remplacé par la version par défaut d'OpenFisca-France (donc le code de loi existant). Le champ `calculNombreParts` est optionnel, mais s'il figure, tous ses champs doivent y figurer, et les élément du tableau associés aux quatre situations familiales doivent faire la même longueur :


```json
"reforme" : {
    "impot_revenu" :{
        "bareme" :{
            "seuils": [9964, 25659, 73369, 157806],
            "taux": [0.14, 0.3, 0.41, 0.45]
        },
        "decote" : {"seuil_celib": 777, "seuil_couple": 1286, "taux": 0.4525},
        "plafond_qf":{
            "abat_dom":{
                "taux_GuadMarReu" : 0.3,
                "plaf_GuadMarReu" : 2450,
                "taux_GuyMay" : 0.4,
                "plaf_GuyMay" : 4050
            },
            "maries_ou_pacses" : 1567,
            "celib_enf" : 3697,
            "celib" : 936,
            "reduc_postplafond" : 1562,
            "reduc_postplafond_veuf": 1745,
            "reduction_ss_condition_revenus" :{
                "seuil_maj_enf": 3797, 
                "seuil1": 18985,
                "seuil2":21037,
                "taux":0
            }
        },
        "calculNombreParts": {
            "partsSelonNombrePAC": [
                {
                    "veuf": 1,
                    "mariesOuPacses": 2,
                    "celibataire": 1,
                    "divorce": 1
                },
                {
                    "veuf": 2.5,
                    "mariesOuPacses": 2.5,
                    "celibataire": 1.5,
                    "divorce": 1.5
                },
                {
                    "veuf": 3,
                    "mariesOuPacses": 3,
                    "celibataire": 2,
                    "divorce": 2
                },
                {
                    "veuf": 4,
                    "mariesOuPacses": 4,
                    "celibataire": 3,
                    "divorce": 3
                }
            ],
            "partsParPACAuDela": 1,
            "partsParPACChargePartagee": {
                "zeroChargePrincipale": {
                    "deuxPremiers": 0.25,
                    "suivants": 0.5
                },
                "unChargePrincipale": {
                    "premier": 0.25,
                    "suivants": 0.5
                },
                "deuxOuPlusChargePrincipale": {
                    "suivants": 0.5
                }
            },
            "bonusParentIsole": {
                "auMoinsUnChargePrincipale": 0.5,
                "zeroChargePrincipaleUnPartage": 0.25,
                "zeroChargeprincipaleDeuxOuPlusPartage": 0.5
            }
        }
    }
}
```
Où `PAC` désigne `personne à charge`.

- Réponse - contenu du body : 
  - res_brut : Impôts payés par les cas-types : 
    - res_brut.avant : Impôt payé avec le code existant 
    - res_brut.plf : Impôt payé avec le PLF (seulement si le PLF est activé, cf partie afférente au PLF)
    - res_brut.apres : Impot payé avec la réforme spécifiée par la requête.
  - nbreParts : Nombre de parts fiscales des cas-types :
    > Le champ `nbreParts` est ajouté à la réponse en version `1.2.0`.
    - nbreParts.avant : Nombre de parts avec le code existant 
    - nbreParts.plf : Nombre de parts avec le PLF (seulement si le PLF est activé, cf partie afférente au PLF)
    - nbreParts.apres : Nombre de parts avec la réforme spécifiée par la requête.
  - timestamp : Chaîne de caractères reçue dans la requête 
  - total : somme des impôts payés par les cas-types dans les trois scénarios. Inutile pour cette requête. 

    ```json
    {
       "res_brut":{
          "apres":{
             "0":0,
             "1":-1839,
             "2":-1292,
             "3":0,
             "4":-2545,
             "5":-1206
          },
          "avant":{
             "0":0,
             "1":-1839,
             "2":-1292,
             "3":0,
             "4":-2545,
             "5":-1206
          },
          "plf":{
             "0":0,
             "1":-1297,
             "2":-1020,
             "3":0,
             "4":-1655,
             "5":-772
          }
       },       
        "nbreParts":{
          "apres": {
            "0": 1.0,
            "1": 1.5,
            "2": 2.0,
            "3": 2.0,
            "4": 3.0,
            "5": 3.0
            },
          "avant": {
            "0": 1.0,
            "1": 1.5,
            "2": 2.0,
            "3": 2.0,
            "4": 3.0,
            "5": 3.0
            },
          "plf": {
            "0": 1.0,
            "1": 1.5,
            "2": 2.0,
            "3": 2.0,
            "4": 3.0,
            "5": 3.0
            }
       },
       "timestamp":"1234564689",
       "total":{
          "apres":6882.0,
          "avant":6882.0,
          "plf":4744.0
       }
    }
    ```


### /calculate/simpop

- Type : POST
- Description : On décrit au serveur une réforme. On s'authentifie par le `token` qui nous a été fourni dans le mail d'authentification/login. Le serveur renvoie l'impact de la réforme sur la population : recettes totales, recettes par décile de RFR (Revenu Fiscal de Référence), frontières entre les déciles, nombre de foyers fiscaux touchés.
- Requête - contenu du body :

    ```
    {
        "reforme" : décrit la réforme au même format que la réforme de l'itinéraire /calculate/compare,
        "timestamp" : chaîne de caractères qui sera renvoyée telle quelle par le programme.
            Champ optionnel, si non fourni, la réponse ne contiendra pas de champ "timestamp",
        "token" : le token d'authentification temporaire qui a été fourni dans l'email.
    }
    ```

- Réponse - contenu du body :
  - timestamp : chaîne de caractères reçue dans la requête
  - total : somme des impots payés par la population dans les trois scénarios. 
  - frontieres_deciles : limites supérieures des RFR des 10 déciles de foyers fiscaux (classés par RFR total par foyer fiscal)
  - foyers_fiscaux_touches : dictionnaire contenant les clefs `avant_to_plf`, `avant_to_apres`, `plf_to_apres`. Chaque élément du dictionnaire divise les foyers fiscaux en 5 catégories : `gagnant`, `perdant`, `neutre`, `neutre_zero`, `perdant_zero` : Ils décrivent si les foyers fiscaux payent plus ou moins d'impôts à l'arrivée qu'au départ. Les catégories finissant par `_zero` décrivent le foyers fiscaux qui étaient exonérés d'impôt au départ.
 Par exemple, `neutre_zero` désigne le nombre de personnes pour lesquelles l'impact est neutre (avant = après) et qui sont exonérées d'impôt (donc, avant = après = 0).

## Endpoints de l'API Web - Dotations aux collectivités locales

L'API Web traite également d'une thématique isolée de l'impôt sur le revenu : les dotations
de l'État aux collectivités locales.

### /dotations

- Type : POST
- Description :
- Requête - contenu du body :
  > Description des contenus :
  ```
  {   
    "descriptionCasTypes": tableau d'objets contenant le code commune des variables apparaissant dans l'output comme communes-types,  
    "reforme":{
        "dotations":{
            "montants":{
                "dgf": montant total de la DGF 
                "dsu": {"variation": Augmentation minimale du montant de l'enveloppe de la DSU},
                "dsr": {"variation": Augmentation minimale du montant de l'enveloppe de la DSR}
            },
            "communes":{
                                "eligibilite":{
                    "popChefLieuMax":Taille maximum DSR bourg-centre si chef lieu de canton,
                    "popMax":Population maximum d'une commune pour être éligible à la DSR (hors cas spécial bourg-centre)
                },
                "bourgCentre":{
                    "eligibilite":{
                        "partPopCantonMin": Part minimum dans la population du canton pour être éligible,
                        "exclusion":{
                            "agglomeration":{
                                "partPopDepartementMin": Part maximum de l'agglomération dans la population du département pour être éligible à la fraction bourg centre de la DSR,
                                "popMin": Population maximum de l'agglomération pour être éligible à la fraction bourg centre de la DSR,
                                "popCommuneMin": Population maximum de la plus grosse commune de l'agglomération pour être éligible à la fraction bourg centre de la DSR
                            },
                            "canton":{
                                "popChefLieuMin": Population maximum du chef-lieu de canton pour être éligible à la fraction bourg-centre sauf bien sûr s'il est bureau centralisateur
                            },
                            "potentielFinancier":{
                                "rapportPotentielFinancierMoyen": Limite de ratio entre le potentiel financier moyen de la commune et le potentiel financier moyen des communes de moins de 10000 habitants
                            }
                        }
                    },
                    "attribution":{
                        "popLimite": Limite prise en compte de la population DGF dans le calcul de la fraction bourg-centre,
                        "effortFiscalLimite": Limite de prise en compte de l'effort fiscal,
                        "coefMultiplicateurRevitalisationRurale": Facteur appliqué au score d'attribution quand la commune appartient à une ZRR,
                        "plafonnementPopulation": Objet décrivant le plafonnement de la population DGF en fonction de la population INSEE
                    }
                },
                "perequation":{
                    "eligibilite":{
                        "rapportPotentielFinancier": Limite de ratio entre le potentiel financier moyen de la commune et le potentiel financier moyen des communes de la strate démographique pour l'éligibilité à la fraction péréquation
                    },
                    "attribution":{
                        "repartition":{
                            "ponderationPotentielFinancier": Part de la DSR (péréquation et cible) répartie en fonction du potentiel financier par habitant,
                            "ponderationLongueurVoirie": Part de la DSR (péréquation et cible) répartie en fonction de la longueur de voirie,
                            "ponderationNbreEnfants": Part de la DSR (péréquation et cible) répartie en fonction du nombre d'enfants,
                            "ponderationPotentielFinancierParHectare": Part de la DSR (péréquation et cible) répartie en fonction du potentiel financier par hectare
                        }
                    }
                },
                "cible":{
                    "eligibilite":{
                        "premieresCommunes": Limite de classement d'indice synthétique pour éligibilité à la fraction cible de la DSR,
                        "indiceSynthetique":{
                            "ponderationPotentielFinancier": Part du potentiel financier par habitant dans l'indice synthétique d'éligibilité à la fraction cible de la DSR,
                            "ponderationRevenu": Part du revenu par habitant dans l'indice synthétique d'éligibilité à la fraction cible de la DSR
                        }
                    }
                }
            },
            "dsu":{
                "eligibilite":{
                    "popMinSeuilBas": Seuil bas de population minimale pour être éligible à la DSU,
                    "popMinSeuilHaut": Seuil haut de population minimale pour être éligible à la DSU,
                    "rapportPotentielFinancier": Limite de ratio entre le potentiel financier moyen de la commune et le potentiel financier moyen des communes de la strate démographique pour l'éligibilité à la DSU,
                    "pourcentageRangSeuilBas": Part des premières communes situées entre le seuil bas et le seuil haut et classées par indice synthétique décroissant touchant la DSU,
                    "pourcentageRangSeuilHaut": Part des communes au dessus du seuil haut de population et classées par indice synthétique décroissant touchant la DSU,
                    "indiceSynthetique":{
                        "ponderationPotentielFinancier": Part de l'indice synthétique d'éligibilité de la DSU déterminée par le ratio entre les potentiels financiers par habitant de la commune et des communes de la même strate, où les strates sont définies par les seuils de population d'éligibilité à la DSU,
                        "ponderationLogementsSociaux": Part de l'indice synthétique d'éligibilité de la DSU déterminée par le ratio entre les parts de logements sociaux de la commune et des communes de la même strate, où les strates sont définies par les seuils de population d'éligibilité à la DSU,
                        "ponderationAideAuLogement": Part de l'indice synthétique d'éligibilité de la DSU déterminée par le ratio entre les aides aux logements par habitant de la commune et des communes de la même strate, où les strates sont définies par les seuils de population d'éligibilité à la DSU,
                        "ponderationRevenu": Part de l'indice synthétique d'éligibilité de la DSU déterminée par le ratio entre les revenus par habitant de la commune et des communes de la même strate, où les strates sont définies par les seuils de population d'éligibilité à la DSU
                    }
                },
                "attribution":{
                    "effortFiscalLimite": Limite de prise en compte de l'effort fiscal dans l'attribution de DSU,
                    "facteurClassementMax": Facteur maximal appliqué au score d'attribution de la DSU en fonction du classement,
                    "facteurClassementMin": Facteur minimal appliqué au score d'attribution de la DSU en fonction du classement,
                    "poidsSupplementaireZoneUrbaineSensible": Coefficient multiplicateur affecté au ratio de population en Zone urbaine sensible dans le calcul du score d'attribution de la DSU,
                    "poidsSupplementaireZoneFrancheUrbaine": Coefficient multiplicateur affecté au ratio de population en Zone franche urbaine dans le calcul du score d'attribution de la DSU,
                    "augmentationMax": Augmentation maximale annuelle de la DSU pour une commune
                }
            }
            }
        }
   },
   "strates": tableau d'objets décrivant les séparations entre strates de la population qui seront utilisées pour renvoyer les résultats agrégés par strate.
  }
  ```
  > Valeur par défaut :
  ```
  {   
    "descriptionCasTypes":[     
      {
         "code":"76384"
      },
      {
         "code":"76214"
      },
      {
         "code":"77186"
      }
    ],  
    "reforme":{
        "dotations":{
            "montants":{
            "dgf":26846874416,
            "dsu": {"variation": 0},
            "dsr": {"variation": 0}
            },
            "communes":{
                "dsr":{
                    "eligibilite":{
                        "popChefLieuMax":20000,
                        "popMax":10000
                    },
                    "bourgCentre":{
                        "eligibilite":{
                            "partPopCantonMin":0.15,
                            "exclusion":{
                            "agglomeration":{
                                "partPopDepartementMin":0.1,
                                "popMin":250000,
                                "popCommuneMin":100000
                            },
                            "canton":{
                                "popChefLieuMin":10000
                            },
                            "potentielFinancier":{
                                "rapportPotentielFinancierMoyen":2
                            }
                            }
                        },
                        "attribution":{
                            "popLimite":10000,
                            "effortFiscalLimite":1.2,
                            "coefMultiplicateurRevitalisationRurale":1.3,
                            "plafonnementPopulation":{
                            "0":500,
                            "100":1000,
                            "500":2250,
                            "1500":999999999
                            }
                        }
                    },
                    "perequation":{
                        "eligibilite":{
                            "rapportPotentielFinancier":2
                        },
                        "attribution":{
                            "repartition":{
                            "ponderationPotentielFinancier":0.3,
                            "ponderationLongueurVoirie":0.3,
                            "ponderationNbreEnfants":0.3,
                            "ponderationPotentielFinancierParHectare":0.1
                            }
                        }
                    },
                    "cible":{
                        "eligibilite":{
                            "premieresCommunes":10000,
                            "indiceSynthetique":{
                            "ponderationPotentielFinancier":0.7,
                            "ponderationRevenu":0.3
                            }
                        }
                    }
                },
                "dsu":{
                    "eligibilite":{
                        "popMinSeuilBas":5000,
                        "popMinSeuilHaut":8000,
                        "rapportPotentielFinancier":2.5,
                        "pourcentageRangSeuilBas":0.1,
                        "pourcentageRangSeuilHaut":0.666667,
                        "indiceSynthetique":{
                            "ponderationPotentielFinancier":0.3,
                            "ponderationLogementsSociaux":0.15,
                            "ponderationAideAuLogement":0.3,
                            "ponderationRevenu":0.25
                        }
                    },
                    "attribution":{
                        "effortFiscalLimite":1.3,
                        "facteurClassementMax":4,
                        "facteurClassementMin":0.5,
                        "poidsSupplementaireZoneUrbaineSensible":2,
                        "poidsSupplementaireZoneFrancheUrbaine":1,
                        "augmentationMax":4000000
                    }
                }
            }
        }
   },
   "strates":[
      {
         "habitants":500
      },
      {
         "habitants":2000
      },
      {
         "habitants":3500
      },
      {
         "habitants":5000
      },
      {
         "habitants":7500
      },
      {
         "habitants":10000
      },
      {
         "habitants":15000
      },
      {
         "habitants":20000
      },
      {
         "habitants":35000
      },
      {
         "habitants":50000
      },
      {
         "habitants":75000
      },
      {
         "habitants":100000
      },
      {
         "habitants":200000
      },
      {
         "habitants":-1
      }
   ]
  }
  ```
- Réponse - contenu du body :
  > Format par défaut :
  ```
{
    "amendement": {  Décrit les résultats obtenus pour la réforme décrite dans la requête
        "communes": {
            "df": {
                "communes": pour chaque commune des cas type apparaît :
                    {
                        "code": code INSEE de la commune,
                        "dotationParHab": dotation forfaitaire reçue par habitant INSEE
                    }
                ],
                "strates": [
                    pour chaque strate (spécifiées dans la requête)
                    {
                        "dotationMoyenneParHab": dotation forfaitaire reçue par habitant INSEE de la strate démographique,
                        "habitants": nombre minimal d'habitants INSEE pour qu'une commune appartienne à la strate,
                        "partDotationTotale": part de la dotation forfaitaire totale attribuée à la strate,
                        "partPopTotale": part de la population INSEE totale représentée par les communes de la strate,
                        "potentielFinancierMoyenParHabitant": potentiel financier moyen par habitant au sein de la strate démographique
                    }
                ]
            },
            "dsr": {
                "communes": [
                    {
                        "code": code INSEE de la commune,
                        "dotationParHab": dotation de solidarité rurale reçue à terme par habitant INSEE
                        "dotationParHabAnneeSuivante": dotation de solidarité rurale reçue l'an prochain par la commune,
                        "dureeAvantTerme": Nombre d'années nécessaire pour que la dotation converge en supposant que la dotation de solidarité rurale reçue à terme ne change pas sur la période,
                        "eligible": statut d'éligibilité de la commune à au moins une fraction de la dotation de solidarité rurale
                    }
                ],
                "eligibles": nombre de communes éligibles à au moins une fraction de la Dotation de solidarité rurale,
                "strates": [
                    pour chaque strate (spécifiées dans la requête)
                    {
                        "dotationMoyenneParHab": dotation de solidarité rurale reçue par habitant INSEE de la strate démographique,
                        "habitants": nombre minimal d'habitants INSEE pour qu'une commune appartienne à la strate,
                        "partDotationTotale": part de la dotation de solidarité rurale totale attribuée à la strate,
                        "partPopTotale": part de la population INSEE totale représentée par les communes de la strate,
                        "potentielFinancierMoyenParHabitant": potentiel financier moyen par habitant au sein de la strate démographique
                    }
                ]
            },
            "dsu": {
                "communes": [
                    {
                        "code": code INSEE de la commune,
                        "dotationParHab": dotation de solidarité rurale reçue à terme par habitant INSEE
                        "eligible": statut d'éligibilité de la commune à au moins une fraction de la dotation de solidarité rurale
                    }
                ],
                "eligibles": nombre de communes éligibles à au moins la Dotation de solidarité urbaine,
                "strates": [
                    pour chaque strate (spécifiées dans la requête)
                    {
                        "dotationMoyenneParHab": dotation de solidarité urbaine reçue par habitant INSEE de la strate démographique,
                        "habitants": nombre minimal d'habitants INSEE pour qu'une commune appartienne à la strate,
                        "partDotationTotale": part de la dotation de solidarité urbaine totale attribuée à la strate,
                        "partPopTotale": part de la population INSEE totale représentée par les communes de la strate,
                        "potentielFinancierMoyenParHabitant": potentiel financier moyen par habitant au sein de la strate démographique
                    }
                ]
            }
        }
    },
    "base": { Même contenu que "amendement", mais avec le code existant au lieu de la réforme spécifiée dans la requête
    },
    "baseToAmendement": { décrit les changements entre le scénario "base" et le scénario "amendement"
        "communes": {
            "dsr": {
                "nouvellementEligibles": nombre de communes nouvellement éligibles à au moins une fraction de la dotation de solidarité rurale,
                "plusEligibles": nombre de commune perdant leur éligibilité à au moins une fraction de la dotation de solidarité rurale,
                "toujoursEligibles": nombre de communes restant éligible à au moins une fraction de la dotation de solidarité rurale
            },
            "dsu": {
                "nouvellementEligibles": nombre de communes nouvellement éligibles à la dotation de solidarité urbaine,
                "plusEligibles": nombre de commune perdant leur éligibilité à la dotation de solidarité urbaine,
                "toujoursEligibles": nombre de communes restant éligible à la dotation de solidarité urbaine
            }
        }
    },
    "baseToPlf": { décrit les changements entre le scénario "base" et le scénario "plf" de la même manière que baseToAmendement. Seulement présent quand un PLF a été spécifié
    },
    "plf": {Même contenu que "amendement", mais avec le PLF au lieu de la réforme spécifiée dans la requête.  Seulement présent quand un PLF a été spécifié
    }
}
  ```

### /search?commune=chaine

renvoie une liste (limitée à 20) des communes contenant la chaîne de caractères demandée en argument comme une sous-chaîne de caractères de leur nom. Chaque élément du tableau des communes contient:

    {
        "code": Code INSEE de la commune,
        "departement": Département de la commune,
        "habitants": population INSEE de la commune,
        "name": nom de la commune en majuscule,
        "potentielFinancierParHab": potentiel financier de la commune divisée par sa population DGF
    }


## Base de données

Uniquement nécessaire dans le cas où les données sur la population sont utilisées (fonctionnalité simpop).  En l'absence d'utilisation de ces données (i.e. les endpoints auth et simpop), il devrait être possible de faire tourner Leximpact-server sans base de données ni fichier .env .

Leximpact-server conserve l'ensemble des données qu'il utilise et qui ne sont pas ouvertes dans une base de données sécurisée en postgresql. Cette partie décrit les différentes tables nécessaire au fonctionnement du site, et la manière de les créer.

Une base de données [PostgreSQL](https://www.postgresql.org/) doit être installée afin de remplir les différentes fonctions suivantes :
- Stockage de la liste des utilisateurs autorisés
- Stockage des requêtes effectuées (pour éviter une surcharge provenant d'un utilisateur unique)
- Stockage des résultats de base préprocessés pour économiser du temps de calcul (utile si la population est grande)

### **users**

Cette table contient les emails des usagers valides.  Elle contient une colonne, "email", qui représente l'email de l'usager.

La liste des emails est régulièrement mise à jour par une demande auprès du SSI ou de parties prenantes de l'institution concernée (Assemblée nationale ou Sénat)

- Etape 1 : concaténer les fichiers  export_deputes.csv et export_employes.csv dans un fichier nommé users.csv  contenant une colonne "email" avec le titre de la colonne en en-tête en haut.
- Etape 1.5 (optionnelle): Une liste d'adresses supplémentaires est présente dans [ce gdoc](https://docs.google.com/spreadsheets/d/1QSRJJQWn13hYqcPzGsorFOifFGgodLHYnn-nWFDons0/edit#gid=448820835). Cette liste peut être concaténée au fichier créé à l'Etape 1

- Etape 2 : uploader ce fichier et run le script preload.py dessus :

```
    .\scalingo -a leximpact-server --region osc-fr1 run --file users.csv bash
    pip install tables
    python ./repo/preload.py
```

- Etape 3 : Si l'étape 1.5 n'a pas été exécutée, ou si des adresses sont rajoutées à la liste, il est possible de les inclure dans la liste en exécutant dans le CLI Scalingo une ligne à base de 

```sql
   INSERT INTO users values ('paul.poule@example.org'),('jean-marie.myriam@example.org');
```

### **requests**

Contient la liste des requêtes simpop effectuées (timestamp et origine).

Description des colonnes :

| nom colonne| type       | Description                      |
|------------|------------|----------------------------------|
| id         | Number     | Identifiant unique de la requête |
| email      | text (256) | adresse email de l'usager        |
| timestamp  | timestamp  | timestamp de la requête          |
|            |            |                                  |

Création / remplissage de la table : la table est créée automatiquement au lancement du serveur via alchemy, et son remplissage est automatique

### **suspended**

Contient la liste des gens blacklistes avec date d'expiration du ban. Le blacklisting arrive quand les requêtes de simpop sont effectués en trop grand nombre, laissant supposer un objectif malveillant de la part de l'usager.

Description des colonnes :

| nom colonne     | type       | Description                      |
|-----------------|------------|----------------------------------|
| id              | Number     | Identifiant unique de la suspension |
| email           | text (256) | adresse email de l'usager        |
| end_suspension  | timestamp  | timestamp de fin de la suspension          |
|                 |            |                                  |

Création / remplissage de la table : la table est créée automatiquement au lancement du serveur via alchemy, et son remplissage est automatique


### **data_erfs**

Fichier contenant les données agrégées de la population française, construites, par exemple, à partir des données de l'ERFS FPR au format openfisca. C'est le fichier décrit plus haut dans la partie Mode agrégats de population.

Le fichier est uploadé dans la base de données, par exemple via preload.py. Le nom de la table dans la base postgresql doit correspondre avec la variable d'environnement nommée `POPULATION_TABLE_PATH`. 

### **base_results**

Table contenant les résultats sur la population du code existant et du code 

Remplie et créée en lançant le script ./scripts/generate_base_results.py via l'interface Scalingo. Le nom de la table doit correspondre avec la variable d'environnement nommée NAME_TABLE_BASE_RESULT


## Insertion/Suppression  du Projet de loi de finances

Le projet de loi de finances est chaque année l'occasion pour le gouvernement et les députés d'amender la loi afférente aux prélèvements obligatoires. LexImpact dispose de la possibilité de faire figurer dans les résultats de l'API (et de l'interface) les impacts des changements prévus par le PLF. 

### **Rajouter le PLF dans leximpact-server**

### Impôt sur le revenu : 

- Obtenir les éléments de la réforme dans le PLF. En l'absence de réforme majeure de l'impôt sur le revenu, les paramètres étant modifiés seront principalement un accroissement des seuils et plafonds par un facteur fixe correspondant à l'inflation estimée par le législateur.

- Transcrire la réforme en paramètres openfisca (si c'est une réforme paramétrique, sinon il faut déclarer une réforme non paramétrique qui n'est pas expliqué ici parce qu'on ne l'a jamais fait).

Exemple : pour le PLF 2021,  un fichier intitulé reformes/reformes_2021.py a été créé dans le repo qui contient

```
reforme_PLF_2021 = {
    "impot_revenu": {
        "bareme": {
            "seuils": [10084, 25710, 73516, 158122],
            "taux": [0.11, 0.3, 0.41, 0.45],
        },
        "decote": {"seuil_celib": 779, "seuil_couple": 1289, "taux": 0.4525},
        "plafond_qf": {
            "abat_dom": {
                "plaf_GuadMarReu": 2450,
                "plaf_GuyMay": 4050,
                "taux_GuadMarReu": 0.3,
                "taux_GuyMay": 0.4,
            },
            "celib": 938,
            "celib_enf": 3704,
            "maries_ou_pacses": 1570,
            "reduc_postplafond": 1565,
            "reduc_postplafond_veuf": 1748
        },
    }
}
```

 - Décrire dans les variables d'environnement l'endroit où se trouve la réforme du PLF :

```
PLF_PATH="reformes.reformePLF_2021.reforme_PLF_2021"
```

### dotations

- Obtenir les éléments de la réforme dans le PLF. En l'absence de changement majeur, la réforme devrait être limitée au montant d'accroissement minimal des DSU et DSR. Dans ce cas, le PLF apparaît dans le code, également dans le fichier simulate_dotations.py

- Mettre la variable ACTIVATE_PLF  à True  dans le fichier Simulation_engine/simulate_dotations.py  Dans le même fichier, un PLF doit être déclaré en utilisant la syntaxe suivante.

```
if ACTIVATE_PLF:
        plf_body_2021 = {
            "dotations": {
                "montants" : {
                    "dsu": {"variation": 90_000_000},
                    "dsr": {"variation": 90_000_000}
                }
                # nothing to update on "communes" key
            }
        }
        # dict_ref = {"amendement" : reforme, "plf": plf}
        plf = format_reforme_openfisca(plf_body_2021)
        dict_ref["plf"] = plf
```



### **Retirer le PLF de leximpact-server**

Après les discussions du PLF, en règle générale, une version potentiellement amendée du PLF sera rentrée dans la loi. A ce moment là, il convient de retirer le PLF de l'interface une fois que la loi a été modifiée pour prendre en compte les novueaux textes. 

### Impôt sur le revenu : 

supprimer la variable d'environnement "PLF_PATH"

### dotations :

mettre la variable ACTIVATE_PLF  à False  dans le fichier Simulation_engine/simulate_dotations.py


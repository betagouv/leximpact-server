# LexImpact-Server

## [EN] Introduction
LexImpact allows civil servants, policy makers and citizens to simulate the _ex ante_ impact of a reform to a country's tax-benefit system.
* [Call for candidates (FR)](https://entrepreneur-interet-general.etalab.gouv.fr/defis/2019/leximpact.html)
* [Elevator pitch (FR)](https://beta.gouv.fr/startups/leximpact.html)
* [LexImpact Beta](https://leximpact.beta.gouv.fr)

## [FR] Introduction
LexImpact permet aux administrations, aux parlementaires et à la société civile de simuler l'impact _ex ante_ des réformes au système socio-fiscal.
* [Appels à candidatures](https://entrepreneur-interet-general.etalab.gouv.fr/defis/2019/leximpact.html)
* [Fiche produit](https://beta.gouv.fr/startups/leximpact.html)
* [LexImpact Beta](https://leximpact.beta.gouv.fr)

## Installation

Cette application requiert [Python 3.7](https://www.python.org/downloads/release/python-370/) et [pip](https://pip.pypa.io/en/stable/installing/).

Plateformes supportées :
- distributions GNU/Linux (en particulier Debian and Ubuntu) ;
- Mac OS X ;
- Windows (nous recommandons d'utiliser [ConEmu](https://conemu.github.io/) à la place de la console par défaut) ;

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

Le  _virtualenv_ **leximpact-server** sera alors activé, c'est-à-dire que les commandes suivantes s'exécuteront directement dans l'environnement virtuel. Vous verrez dans votre terminal. :

Bravo :tada: Vous êtes prêt·e à installer LexImpact-Server !

### Installez LexImpact-Server

Pour installer LexImpact-Server, dans votre fenêtre de terminal :

```sh
make install
```

Félicitations :tada: LexImpact-Server est prêt à être utilisé !

## Lancez l'API Web LexImpact

### Fichier de configuration `.env`

Pour lancer LexImpact-Server, vous devez tout d'abord créer un fichier de configuration `.env`. Dans votre fenêtre de terminal :

```sh
echo DATABASE_USER=\"asdf\" >> .env
echo DATABASE_PASS=\"1234\" >> .env
echo DATABASE_HOST=\"localhost\" >> .env
echo DATABASE_PORT=\"5432\" >> .env
echo DATABASE_NAME=\"leximpact\" >> .env
echo JWT_AUDIENCE=\"Toi\" >> .env
echo JWT_ISSUER=\"Moi\" >> .env
echo JWT_SECRET=\"$(python -c 'from server.services.auth import create_nonce; print(create_nonce().decode("ascii"))')\" >> .env
```

Regardez le fichier `.env.example` pour avoir un exemple de fichier de configuration `.env`.

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

Félicitations :tada: LexImpact-Server est en train de tourner !

### Mode agrégats de population

Par défaut, seul de résultats à partir de cas-types sont présents dans l'API.

Dans le cas où une base de données représentant la population française (non incluse dans la bibliothèque) est présente sur l'ordinateur d'exécution, des agrégats d'impact (budgétaire, redistributif...) seront inclus dans les réponses de l'API.

Pour ce faire, modifiez le fichier suivant :

```python
# Simulation_engine/simulate_pop_from_reform.py
version_beta_sans_graph_pop = False  # Au lieu de True par défaut
```

_**Note :** les instructions supra vous sont fournies à caractère indicatif, l'équipe de développement LexImpact ne disposant pas à ce stade de véritable jeu de données._

Félicitations :tada: Vous-êtes en train de réformer le système socio-fiscal français !

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


## Endpoints de l'API Web

L'API Web dispose des itinéraires suivants :

* `/`
* `/metadata/description_cas_types`
* `/auth/login`
* `/calculate/compare`
* `/calculate/simpop`

Parmi ces itinéraires, trois nécessitent une vérification de l'identité de l'appelant :

* `/auth/login`
* `/calculate/compare`
* `/calculate/simpop`

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
- Description : Soumet un email au serveur. Si cet email est dans la liste des adresses autorisées, un lien de connexion au service LexImpact Pop est envoyé à l'adresse email spécifiée.
- Requête - contenu du body : Ne contient qu'un champ tel que décrit dans l'exemple suivant.

    ```json
    {
        "email" : "email@tester.io"
    }
    ```

- Réponse - contenu du body :  La réponse renvoyée sera toujours la même, afin d'éviter de donnner des informations sur la validité des adresses mail : juste une chaîne de caractères qui contient `Bien reçu! Si l'email est valide, nous avons envoyé un mail de confirmation`.

###  /calculate/compare

- Type : POST
- Description : On décrit au serveur une description de cas-types, et une réforme, et ce dernier nous renvoie l'effet de la réforme sur ces cas-types.
- Requête - contenu du body :

    ```
    {
        "reforme" : décrit la réforme,
        "deciles": deprecated - n'a plus d'impact,
        "description_cas_types": array de descriptions de cas-types (pour la structure, cf le guide du endpoint /   metadata/description_cas_types). Champ optionnel, si non fourni, utilise les descriptions de cas types     par défaut,
        "timestamp" : chaîne de caractères qui sera renvoyé tel quel par le programme. Champ optionnel, si non fourni, la     réponse ne contiendra pas de champ "timestamp"
    }
    ```

En date du 2019-10-07, la structure de la réforme est la suivante. Elle reproduit presque la structure d'OpenFisca. Si un paramètre est omis, il est remplacé par la version par défaut d'OpenFisca (donc le code existant) :


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
        }
    }
}
```


- Réponse - contenu du body : 
  - res_brut : Impôts payés par les cas-types : 
    - res_brut.avant : Impôt payé avec le code existant 
    - res_brut.plf : Impôt payé avec le PLF 
    - res_brut.apres : Impot payé avec la réforme sépcifiée par la requête.
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
          },
          "wprm":{
             "0":1,
             "1":1,
             "2":1,
             "3":1,
             "4":1,
             "5":1
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
        "reforme" : décrit la réforme,
        "timestamp" : chaîne de caractères qui sera renvoyée telle quelle par le programme. Champ optionnel, si non fourni, la réponse ne contiendra pas de champ "timestamp",
        "token" : le token d'authentification temporaire qui a été fourni dans l'email
    }
    ```

- Réponse - contenu du body :
  - timestamp : chaîne de caractères reçue dans la requête
  - total : somme des impots payés par la population dans les trois scénarios. 
  - frontieres_deciles : limites supérieures des RFR des 10 déciles de foyers fiscaux (classés par RFR total par foyer fiscal)
  - foyers_fiscaux_touches : dictionnaire contenant les clefs `avant_to_plf`, `avant_to_apres`, `plf_to_apres`. Chaque élément du dictionnaire divise les foyers fiscaux en 5 catégories : `gagnant`, `perdant`, `neutre`, `neutre_zero`, `perdant_zero` : Ils décrivent si les foyers fiscaux payent plus ou moins d'impôts à l'arrivée qu'au départ. Les catégories finissant par `_zero` décrivent le foyers fiscaux qui étaient exonérés d'impôt au départ.
 Par exemple, `neutre_zero` désigne le nombre de personnes pour lesquelles l'impact est neutre (avant = après) et qui sont exonérées d'impôt (donc, avant = après = 0).



## Base de données

Leximpact-server conserve l'ensemble des données qu'il utilise et qui ne sont pas ouvertes dans une base de données sécurisée en postgresql. Cette partie décrit les différentes tables nécessaire au fonctionnement du site, et la manière de les créer.

### **users**

Cette table contient les emails des usagers valides.  Elle contient une colonne, "email", qui représente l'email de l'usager.

La liste des emails est déposée et régulièrement updatée par le SSI de l'AN dans le serveur ssian@eig.etalab.gouv.fr

- Etape 1 : concaténer les fichiers  export_deputes.csv et export_employes.csv dans un fichier nommé users.csv  contenant une colonne "email" avec le titre de la colonne en en-tête en haut.
- Etape 1.5 (optionnelle): Une liste d'adresses supplémentaires est présente dans [ce gdoc](https://docs.google.com/spreadsheets/d/1QSRJJQWn13hYqcPzGsorFOifFGgodLHYnn-nWFDons0/edit#gid=448820835). Cette liste peut être concaténée au fichier créé à l'Etape 1

- Etape 2 : uploader ce fichier et run le script preload.py dessus :

```
    .\scalingo -a leximpact-server run --file users.csv bash    pip install tables    python ./repo/preload.py
```

- Etape 3 : Si l'étape 1.5 n'a pas été exécutée, ou si des adresses sont rajoutées à la liste, il est possible de les inclure dans la liste en exécutant une ligne à base de 

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

Fichier contenant les données agrégées de la population française, construites, par exemple, à partir des données de l'ERFS FPR au format openfisca. C'est l'output de la phase transform_data (insérer lien vers la doc de la transformation des données).  

Le fichier est uploadé dans la base de données, par exemple via preload.py . Le nom de la table dans la base postgresql doit correspondre avec la variable d'environnement nommée DATA_PATH 

### **base_results**

Table contenant les résultats sur la population du code existant et du code 

Remplie et créée en lançant le script ./scripts/generate_base_results.py via l'interface Scalingo. Le nom de la table doit correspondre avec la variable d'environnement nommée NAME_TABLE_BASE_RESULT

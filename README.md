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

## Lancez l'API LexImpact

**Mode demo**

Pour lancer LexImpact-Server, dans votre fenêtre de terminal :

```sh
make run
```

Pour s'assurer que tout marche bien :

```sh
./test/stress/test.sh
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

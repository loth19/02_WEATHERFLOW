# WeatherFlow

Projet data meteo de bout en bout:

- collecte des donnees OpenWeather API
- transformation en table analytique avec pandas
- visualisations (Matplotlib + Plotly)
- dashboard interactif Streamlit

## Objectif

Comparer la meteo de 5 villes europeennes (Paris, Londres, Madrid, Rome, Berlin),
calculer un indice de confort, puis exposer les resultats dans une application web.

## Dashboard en ligne

Acces public recruteur:

- https://loth19-02-weatherflow-app-ipynbstreamlit-app-t6edkk.streamlit.app

## Stack technique

- Python 3.12
- requests
- pandas
- matplotlib
- plotly
- streamlit
- python-dotenv

Dependances dans requirements:

- requests
- pandas
- matplotlib
- plotly
- streamlit
- python-dotenv

## Structure du projet

- .env: cle API (non versionnee)
- .gitignore: exclusions Git
- requirements.txt: dependances Python
- src/fetch_data.ipynb: extraction API vers JSON bruts
- src/tansform.ipynb: transformation vers table propre + indice_confort
- src/df.csv: donnees transformees (sortie pipeline)
- data/raw/: JSON bruts par ville
- outputs/: graphiques exportes
- app.ipynb/streamlit_app.py: application Streamlit principale

## Pipeline utilisee

Pipeline ETL + presentation, en 4 etapes:

1. Extract (API)
	- Appel OpenWeather endpoint current weather
	- Parametres utilises: q, appid, units=metric, lang=fr
	- Sauvegarde d un JSON brut par ville dans data/raw

2. Transform (pandas)
	- Chargement des JSON de data/raw
	- Extraction des champs:
	  - ville
	  - temperature
	  - ressenti
	  - humidite
	  - vitesse_vent
	  - description_meteo
	- Calcul de indice_confort (score 0 a 10)
	- Export CSV consolide (src/df.csv)

3. Visualize
	- Generation des graphiques Matplotlib dans outputs
	- Graphique Plotly dans le dashboard

4. Serve (Streamlit)
	- Affichage tableau global
	- Detail par ville
	- Recommandation automatique
	- Rafraichissement possible depuis l API

## Logique des donnees dans l app

L app suit une logique robuste:

1. Source principale: src/df.csv (sortie transform)
2. Si le CSV est absent: fallback API directe (si cle disponible)
3. Bouton Rafraichir: recharge API et met a jour src/df.csv

Ce choix garde la coherence avec le travail initial tout en permettant un mode live.

## Securite et configuration

Creer un fichier .env a la racine:

OPENWEATHER_API_KEY=ta_cle_ici

Points importants:

- Ne jamais commiter .env
- Verifier que .env et .venv sont ignores par .gitignore

## Installation

1. Creer et activer un environnement virtuel
2. Installer les dependances

Commandes PowerShell:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

## Execution du projet

### Etape A - Extraction API

Executer les cellules de src/fetch_data.ipynb pour produire data/raw/*.json

### Etape B - Transformation

Executer les cellules de src/tansform.ipynb pour produire src/df.csv

### Etape C - Dashboard Streamlit

Lancer l application:

streamlit run app.ipynb/streamlit_app.py

Note:

- Ne pas lancer avec python app.ipynb/streamlit_app.py
- Streamlit doit etre lance avec la commande streamlit run

## Deploiement pour le recruteur

L objectif final est de publier le dashboard sur une URL publique pour qu un recruteur puisse y acceder sans installer le projet.

Option recommandee: Streamlit Community Cloud.

Etapes:

1. Pousser le projet sur GitHub
2. Relier le depot a Streamlit Community Cloud
3. Choisir comme fichier d entree: app.ipynb/streamlit_app.py
4. Ajouter la variable d environnement OPENWEATHER_API_KEY dans les secrets Streamlit
5. Recuperer l URL publique fournie par Streamlit et la partager au recruteur

Resultat attendu:

- une URL web accessible depuis n importe quel navigateur
- un dashboard interactif sans installation locale
- la possibilite pour le recruteur de tester les filtres, le tableau et les graphiques en direct

## Resultats obtenus

Le pipeline produit une base propre de 5 villes europeennes avec les champs suivants:

- ville
- temperature
- ressenti
- humidite
- vitesse_vent
- description_meteo
- indice_confort

Extrait du CSV final `src/df.csv`:

| ville | temperature | ressenti | humidite | vitesse_vent | description_meteo | indice_confort |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Paris | 17.81 | 16.66 | 39 | 2.57 | ciel dégagé | 6.5 |
| Londres | 16.59 | 15.51 | 46 | 5.36 | couvert | 8.0 |
| Rome | 20.12 | 19.91 | 66 | 7.72 | partiellement nuageux | 8.5 |
| Madrid | 18.99 | 17.94 | 38 | 4.12 | partiellement nuageux | 8.5 |
| Berlin | 13.53 | 12.64 | 65 | 4.02 | ciel dégagé | 6.5 |

### Observations principales

- Rome et Madrid ressortent comme les villes les plus confortables sur cet instant de collecte.
- Londres reste interessante grace a une temperature moderee, mais le vent est plus present.
- Berlin et Paris restent correctes, avec un indice de confort plus moyen.

### Livrables generes

- `outputs/temperatures.png` : comparaison des temperatures entre les 5 villes
- `outputs/confort.png` : nuage de points temperature vs humidite
- `app.ipynb/streamlit_app.py` : dashboard interactif Streamlit

Lien de partage a fournir au recruteur une fois deploye:

- https://loth19-02-weatherflow-app-ipynbstreamlit-app-t6edkk.streamlit.app

### Interpretation

Les resultats montrent que l indice de confort depend surtout:

- de la temperature ressentie
- de l humidite
- de la vitesse du vent

Cet indice permet de comparer rapidement plusieurs villes sur un seul score, au lieu de lire plusieurs colonnes meteorologiques separement.

## Indice confort (resume)

Score de base: 10

- penalite temperature trop froide/chaude
- penalite humidite trop basse/haute
- penalite vent fort
- borne finale entre 0 et 10

Si une donnee est manquante (NaN), le score retourne 0.0 pour eviter les crashes.

## Gestion des erreurs

- Erreurs reseau API capturees (requests)
- Reponses API invalides converties en lignes avec message d erreur
- Protection sur donnees manquantes avant affichage detail ville

## Workflow Git recommande

1. Initialiser
	- git init
2. Ajouter et commiter
	- git add .
	- git commit -m "feat: WeatherFlow pipeline + dashboard"
3. Workflow branches
	- git checkout -b dev
	- travail sur dev
	- merge dans main quand stable
4. Push GitHub
	- git remote add origin https://github.com/TON_USERNAME/02-WeatherFlow.git
	- git branch -M main
	- git push -u origin main

## Usage de l IA (transparence)

Ce projet a utilise une assistance IA comme outil d appui pour:

- clarifier la structure de la pipeline
- proposer des corrections de bugs et de robustesse
- accelerer la redaction/refactor de certaines parties
- verifier la coherence des etapes fetch -> transform -> app

Le developpement, les choix finaux, les tests et la validation restent sous controle humain.

## Limites et pistes d amelioration

- Ajouter des tests unitaires (indice_confort, normalisation)
- Ajouter un script Python fetch_data.py et transform.py en plus des notebooks
- Ajouter un scheduler pour refresh automatique
- Ajouter des retries API et logs plus detailles


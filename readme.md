# Deployer l'API de récupération des mesures d'un .usdz sur Google Cloud

## Etapes de déploiement

### Créer un compte google cloud et installer Google cloud sdk
Compte actuel sur l'adresse gmail poubelle : hadri.carad@gmail.com
TODO : créer un compte google cloud WonderWalls avec l'adresse dev@wonderwalls.systems

Google cloud sdk à installer : https://cloud.google.com/sdk/docs/install

### Créer un projet et authoriser l'api cloud build

SUivre le tutoriel ici pour créer un projet et activer l'API CLoud build : 
https://www.youtube.com/watch?v=3fsIcMgUOY8&t=3s

### créer un fichier requirements.txt et app.yaml

- requirements.txt reprend tous les packages python nécessaires à l'exécution du script et les installent sur la machine sur laquelle le code est exécuté. 
- app.yaml spécifie les paramètres de l'app, comme la version du coeur qui exécute l'application (python 3.9 dans notre cas, soit python39)

### Tester l'application sur une machine virtuelle

- Créer un environnement sur une machine virtuelle venv
- Installer les packages de requirements avec pip install -r requirements.txt
- run la commande d'exécution python main.py

### Deployer l'app sur google cloud

- Se connecter à google cloud : gcloud auth login
- Selectionner le projet : gcloud config set project api-wall-measures-391914
- deployer l'app sur le projet dans App engine : gcloud app deploy

### Tester l'API

- Le service est disponible dans l'URL de sortie de la commande ou en entrant la commande suivante : gcloud app browse --project=api-wall-measures-391914
- Le resultat est accessible à l'adresse : https://api-wall-measures-391914.ew.r.appspot.com/WallMeasures

## Bugs à éviter 

### 1er deploiement
Le code suivant a bloqué le déploiement de l'API sur google cloud : 

with open("./templates/resultMeasurement.json", "w") as file: file.write(result)

## Accéder aux résultat
Dans test.py, on utilise la library request pour requêter l'API et récupérer l'ensemble des données.


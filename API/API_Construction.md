# Déploiement d'une API sur Google Cloud & Intégration d'OpenAPI

## Objectifs

Le configurateur de Wonderwalls fait appel à plusieurs microservices pour effectuer des calculs internes avant d'acfficher les résultats dans un environnement 3D en Vue.js. 
Pour prototyper ces microservices nous avons utilisé une API Flask avec plusieurs endpoints. L'un des endpoint (MeasurmeentCalculation) permet de lire un fichier USDZ stocké sur google drive et d'en déduire les dimensions des murs d'une pièce. C'est ce endpoint que nous avons décidé de déployer. 

## Architecture du projet une fois déployé

![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/e776ef23-9d49-4c22-92a1-c50a265071f7)

- 1 : localisation de l'API. Pour lancer l'API en local, il faut se trouver dans le dossier api-config-online/API (idem pour déployer l'API sur google cloud)
- 2 : main.py est le fichier à exécuter pour créer le microservice. EN local, lancer python main.py
- 3 : Dossier controller avec l'ensemble des fonctions utiles pour l'exécution des endpoints.
- 4 : Dossier model avec toutes les classes d'objet utilisées pour l'API. 1 classe par fichier maximum.
- 5 : fichiers utiles pour le déploiement sur google cloud :
  - app.yaml : synthétise les caractéristiques de l'environnement avec lequel l'API peut s'exécuter (version de python par exemple)
  - requirements.txt : synthétise l'ensemble des packages à télécharger et importer pour pouvoir exécuter le code de l'API.
  - .gcloudignore : fichier généré par google cloud.
- 6 : Dossier static : utilisé pour OpenAPI et générer la documentation rapidoc.

### 2- main.py

![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/587a49df-aabb-4e47-b45e-eacdad756511)

- 1 : Le endpoint exécuté sur google cloud, sans utiliser le format OpenAPI
- 2 : le endpoint (commenté) pouvant être utilisé en local pour générer la documentation OpenAPI

### 3- Controller

Nous avons 3 fichiers .py pur nos controller. Ces controllers permettent d'accéder à des fonctions dans l'API. 

![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/208ccfed-22fb-437d-bf5f-c934e31d9f2b)

- 1 : fonctions permettant de traiter les informations des fichiers sur Google storage
- 1' : fonctions permettant de lire le fichier et extraire des données sous forme d'objets
- 1'' : fonctions permettant de traiter des format json. Pour importer ces fonctions, il est nécessaire de le déclarer en début de programme

### 4- Model

![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/5cf9de9b-8478-4870-a1e8-d4ab6ee08ddc)

- Point est un objet de type point en 3D
- Corners est un objet stockant 5 points sur un mur (4 angles et le milieu du bord gauche du mur)
- Obstacles est un objet caractérisant les obstacles dans le mur (dimensions, positions et Corners)
- Wall  est un bjet mur avec tourtes les caractéristiques de mur
- Room est un objet stockant une liste de mur et des variables relatives à la pièce.

Pour utiliser la génération automatique de documentation OpenAPI, toutes les fonctions dans les controllers doivent renvoyer des objets définis dans les model (ou des objets de base (int, str)). Pour cette raison, la fonction getMeasures ne peut pas renvoyer une liste de Wall.

Les classes doivent être des dataclass, avec un constructeur 'vide'. VOici un exemple avec la classe Point : 
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/c8b0489e-28ee-429e-b169-9e5a16472f91)

L'objet Point est créé vide et modifié ittérativement  : 
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/52b88395-c814-4579-b405-4882c500a212)
- 1 : bottomleftCorner a été créé vide
- 2 : ensuite bottomleftCorner a été rempli succéssivement.


### 5- Déploiement sur Google Cloud

Le déploiement sur google cloud nécessite de modifier le code des fonctions pour : 
- récupérer les fichiers depuis Cloud storage (et plus Google drive)
- La création de fichiers spécifiques au déploiement sur Cloud Engine (app.yaml & requirements.txt)

#### Les modifications du code. 

- Les objets ne sont plus définis dans la fonction getMeasures mais en dehors.
- l'import de fichier depuis cloud storage se fait en deux temps :
  - d'abord le fichier doit être identifié sur l'espace de stockage (via le bucket name et le blob name)
  - Ensuite le fichier doit être téléchargé dans un fichier temporaire (/tmp sur google cloud) pour pouvoir être ouvert dans un programe
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/b8c60bd8-9000-42f4-83d9-e4eb8cf24741)
- Création du fichier app.yaml : Ce fichier permet à n'importe quelle machine virtuelle de savoir le kernel et les dépendances nécessairte pour exécuter le code d'une application. Dans notre cas, nous utilisons python 3.9 à l'exécution. Les autres paramêtres sont proposés par Google par défaut.
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/87df1c37-0cb9-49d3-9745-b9c6f0382794)
- requirements.txt liste tous les packages que la machine virtuelle va installer via la fonction "pip install" 
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/c1897b7b-ca7c-4a96-be47-f6bb753fc722)

#### La préparation du déploiement
Les fichiers .usdz lu doivent être uploadés manuellement dans le projet, sous le service cloud storage. Nous utilisons le bucket staging par défaut. 
Dans ce bucket, j'ai créé manuellement un dossier 'template' dans lequel j'ai uploadé 3 fichiers. 
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/59f12b4b-02b1-40dd-8f73-9c9caade7825)
![image](https://github.com/HadrienWonderwalls/api-config-online/assets/120031854/04062194-a60d-46b1-abfa-1171e1b0bf80)

Depuis visual studio code, j'utilise les ligne de code suivantes : 
- "gcloud config set project api-wall-measures-391914" pour définir mon projet de déploiement
- "gcloud app deploy" pour déployer le code actuel sur le projet de déploiement.
- Une fois le code uploadé, l'url suivante doit renvoyer un objet room : https://api-wall-measures-391914.ew.r.appspot.com/WallMeasures/chambre308.usdz/




### 6- Static


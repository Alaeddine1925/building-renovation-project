# Variables d'environnement
#DEPLOY = "GCP"  # when we run APIs after deployment on GCP
DEPLOY = "Local"  # when we run APIs on our machine (Localhost)

# Variables business

STANDARD_BEAM_WIDTH = 6 / 100
STANDARD_BEAM_LENGTH = 180 / 100
STANDARD_DISTANCE_BTW_TWO_HOLES = 6 / 100
STANDARD_PANEL_WIDTH = 60 / 100  # largeur standarde d'un panneau (en cm)
STANDARD_PANEL_HEIGHT = 240 / 100  # hauteur standarde d'un panneau (en cm)
MIN_PANEL_FULLWIDTH = (
    18 / 100
)  # largeur minimale autorisée pour la partie pleine d'un panneau L ou C (en cm)

LEFT_JOIN_WIDTH = 0.3 / 100  # taille d'un joint unilin à gauche du panneau (en cm)
RIGHT_JOIN_WIDTH = 3 / 100  # taille d'un joint unilin à droite du panneau (en cm)

STANDARD_BEAM_WIDTH = 6 / 100  # largeur standard d'une beam (en cm)
STANDARD_DISTANCE_BTW_TWO_HOLES = (
    6 / 100
)  # distance standard entre deux cercles (en cm)


# Variables déploiement sur Google Cloud Platform

GCP_PROGECT = "api-wall-measures-391914"
GCP_BUCKETNAME = "staging.api-wall-measures-391914.appspot.com"

GCP_FOLDER_USDZ = "template/"

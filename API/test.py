import requests

# URL de l'API Flask
url = 'http://127.0.0.1:5000/PanelWidth'  # Assurez-vous de remplacer l'URL par la vôtre si différente

# Exemple de l'objet Wall à envoyer dans la requête
wall_data = {
  "center": {
    "x": 1.1463713645935059,
    "y": 0.28716200590133667,
    "z": -0.6001477837562561
  },
  "corners": {
    "bottomLeft": {
      "x": 0.5930581398367707,
      "y": -1.2570084929466248,
      "z": -0.6789379542647254
    },
    "bottomRight": {
      "x": 1.699684589350241,
      "y": -1.2570084929466248,
      "z": -0.5213576132477868
    },
    "middleLeft": {
      "x": 1.699684589350241,
      "y": 0.28716200590133667,
      "z": -0.5213576132477868
    },
    "topLeft": {
      "x": 0.5930581398367707,
      "y": 1.831332504749298,
      "z": -0.6789379542647254
    },
    "topRight": {
      "x": 1.699684589350241,
      "y": 1.831332504749298,
      "z": -0.5213576132477868
    }
  },
  "height": 3.088340997695923,
  "listObstacles": [],
  "name": "Wall7",
  "nbObstacles": 0,
  "transform": [
    [0.990013062953949, 0.0, 0.14097493886947632, 0.0],
    [0.0, 0.9999998807907104, 0.0, 0.0],
    [-0.14097493886947632, 0.0, 0.9900131225585938, 0.0],
    [
      1.1463713645935059, 0.28716200590133667, -0.6001477837562561,
      0.9999999403953552
    ]
  ],
  "width": 1.1177897453308105
}

# Effectuer la requête POST avec l'objet JSON en tant que payload
response = requests.post(url, json=wall_data)

# Vérifier la réponse de l'API

data = response.json()
print('Réponse de l\'API:', data)

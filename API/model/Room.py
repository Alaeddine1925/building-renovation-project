from typing import List
from marshmallow_dataclass import dataclass

import re
from pxr import Usd, UsdGeom
import math
from google.cloud import storage

from model.Point import Point
from model.Corners import Corners
from model.Obstacle import Obstacle
from model.Wall import Wall
from model.constantesGlobales import (
    GCP_PROGECT,
    GCP_BUCKETNAME,
    GCP_FOLDER_USDZ,
    DEPLOY,
)


@dataclass
class Room:
    id: str = None
    listWall: List[Wall] = None
    nbWall: int = None

    def update_from_dict(self, usdzFile):
        self.id = usdzFile
        self.listWall = []
        self.nbWall = 0
        self._setMeasurement(usdzFile)

    ## La fonction calculateMeasurement permet de lire un fichier usdz et le traduire en Json.
    ## En output, nous avons une liste de murs avec les coordonnées 3D du centre & des coins, la lsite des obstacles
    ## sur le mur, les infos scale & transform issues de l'usdz.
    def _setMeasurement(self, usdzFile):
        ############################
        ##### Début de la fonction #
        ############################

        ##
        # get the usdz file from google cloud
        ##
        if DEPLOY == "GCP":
            # Create a client using your Google Cloud project ID
            client = storage.Client(project=GCP_PROGECT)

            # Name of the bucket where the USD file is stored
            bucket_name = GCP_BUCKETNAME

            # Name of the USD file
            blob_name = GCP_FOLDER_USDZ + str(usdzFile)

            # Get a reference to the blob
            bucket = client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Download the blob to a local file
            # --> file must be downloaded in /tmp folder otherwise error 500 : https://cloud.google.com/appengine/docs/standard/using-temp-files?&tab=python
            local_file_path = "/tmp/localusdz.usdz"
            blob.download_to_filename(local_file_path)

            stage = Usd.Stage.Open(local_file_path)  # lecture du fichier usdz
        else:
            ### La ligne ci dessous doit remplacer le code ci-dessus pour run l'api en local
            stage = Usd.Stage.Open(usdzFile)  # lecture du fichier usdz

        wallDict = {}
        previousObstacles = []

        # Browse the USDZ file to find walls and obstacles
        for prim in stage.Traverse():
            if UsdGeom.Imageable(prim):
                object_name = (
                    prim.GetPath().pathString
                )  # object_name est le chemin vers chaque fichiers de l'usdz. Exemple :
                """
                    /test2
                    /test2/Parametric_grp
                    /test2/Parametric_grp/Arch_grp
                    /test2/Parametric_grp/Arch_grp/Wall_0_grp
                    /test2/Parametric_grp/Arch_grp/Wall_0_grp/Wall0
                """

                # When we find a Wall :
                if re.search(r"Wall\d", object_name):
                    scaleWall = prim.GetAttribute("xformOp:scale").Get(
                        Usd.TimeCode.Default()
                    )
                    wall = Wall()
                    wall.width = scaleWall[0]
                    wall.height = scaleWall[1]
                    wallTransform = prim.GetAttribute("xformOp:transform").Get(
                        Usd.TimeCode.Default()
                    )
                    wallCorners = self.getCorners(scaleWall, wallTransform)

                    wallDict[object_name] = [wall.width, wall.height, 0, []]

                    ListObstacles = []

                    # Dans le cas où le mur a des obstacles, on récupère les caractéristiques des obstacles
                    for previousObstacle in previousObstacles:
                        scaleObstacle = previousObstacle.GetAttribute(
                            "xformOp:scale"
                        ).Get(Usd.TimeCode.Default())
                        obstacleWidth = scaleObstacle[0]
                        obstacleHeight = scaleObstacle[1]
                        obstacleTransform = previousObstacle.GetAttribute(
                            "xformOp:transform"
                        ).Get(Usd.TimeCode.Default())
                        obstacleTransformArray = [
                            list(row) for row in obstacleTransform
                        ]
                        obstacleCenter = Point()
                        obstacleCenter.x = obstacleTransform[3][0]
                        obstacleCenter.y = obstacleTransform[3][1]
                        obstacleCenter.z = obstacleTransform[3][2]
                        # obstacleCenterDict = obstacleCenter.to_dict()
                        obstacleCenterDict = Point.Schema().dump(obstacleCenter)

                        obstacleCorners = self.getCorners(
                            scaleObstacle, obstacleTransform
                        )

                        obstacleCornersDict = {
                            "bottomLeft": Point.Schema().dump(obstacleCorners),
                            "bottomRight": Point.Schema().dump(
                                obstacleCorners.bottomRight
                            ),
                            "topLeft": Point.Schema().dump(obstacleCorners.topLeft),
                            "topRight": Point.Schema().dump(obstacleCorners.topRight),
                        }

                        # number of obstacles within the current wall is increased by 1
                        wallDict[object_name][2] += 1

                        # Calculate the distance between two points (AB = SQRT((Xb - Xa)²+(Yb-Ya)²))
                        xLeft = math.sqrt(
                            (obstacleCorners.bottomLeft.x - wallCorners.bottomLeft.x)
                            ** 2
                            + (obstacleCorners.bottomLeft.z - wallCorners.bottomLeft.z)
                            ** 2
                        )

                        xRight = xLeft + obstacleWidth
                        yBottom = (
                            obstacleCorners.bottomLeft.y - wallCorners.bottomLeft.y
                        )
                        yTop = obstacleCorners.topLeft.y - wallCorners.bottomLeft.y

                        obstacle = Obstacle()
                        obstacle.width = obstacleWidth
                        obstacle.height = obstacleHeight
                        obstacle.xLeft = xLeft
                        obstacle.xRight = xRight
                        obstacle.yBottom = yBottom
                        obstacle.yTop = yTop
                        obstacle.topDistanceFromTopWall = wall.height - yTop
                        obstacle.center = obstacleCenterDict
                        obstacle.transform = obstacleTransformArray
                        obstacle.corners = obstacleCornersDict
                        obstacle.id = previousObstacle.GetPath().pathString.split("/")[
                            -1
                        ]

                        ListObstacles.append(obstacle)

                    wallTransformArray = [list(row) for row in wallTransform]

                    wallCenter = Point(
                        wallTransform[3][0], wallTransform[3][1], wallTransform[3][2]
                    )

                    wall.id = object_name.split("/")[-1]
                    wall.nbObstacles = wallDict[object_name][2]
                    wall.transform = wallTransformArray
                    wall.obstacles = ListObstacles
                    wall.center = wallCenter
                    wall.corners = wallCorners

                    self.nbWall += 1
                    self.listWall.append(wall)

                    # réinitialisation des listes d'obstacles pour le prochain mur
                    ListObstacles = []
                    previousObstacles = []

                # Browse for obstacles(openings, doors or windows) in the current Wall.
                elif (
                    re.search(r"Window\d", object_name)
                    or re.search(r"Opening\d", object_name)
                    or re.search(r"Door\d", object_name)
                ):
                    previousObstacles.append(prim)

    # Return the Corners of an object (obstacle or wall).
    def getCorners(self, scale, transform):
        width = scale[0]
        height = scale[1]

        x_left = transform[3][0] - (width / 2) * transform[0][0]
        z_left = transform[3][2] - (width / 2) * transform[0][2]

        x_right = transform[3][0] + (width / 2) * transform[0][0]
        z_right = transform[3][2] + (width / 2) * transform[0][2]

        y_bottom = transform[3][1] - (height / 2)
        y_top = transform[3][1] + (height / 2)

        bottomLeftCorner = Point(x_left, y_bottom, z_left)
        topLeftCorner = Point(x_left, y_top, z_left)
        bottomRightCorner = Point(x_right, y_bottom, z_right)
        topRightCorner = Point(x_right, y_top, z_right)

        corners = Corners(
            bottomLeft=bottomLeftCorner,
            bottomRight=bottomRightCorner,
            topLeft=topLeftCorner,
            topRight=topRightCorner,
        )

        return corners

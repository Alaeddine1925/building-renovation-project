from typing import List
from marshmallow_dataclass import dataclass
import numpy as np
import math
from model.Point import Point
from model.Obstacle import Obstacle
from model.Panel import Panel
from model.Layout import Layout
from model.WallFixationPoint import WallFixationPoint
from model.BeamAssembly import BeamAssembly
from model.Point2D import Point2D
from model.Moulding import Moulding
from model.constantesGlobales import (
    STANDARD_PANEL_WIDTH,
    MIN_PANEL_FULLWIDTH,
    STANDARD_BEAM_WIDTH,
    STANDARD_DISTANCE_BTW_TWO_HOLES,
)


@dataclass
class Wall:
    # Base attributes :
    id: str = None
    width: float = None
    height: float = None
    center: Point = Point()
    obstacles: List[Obstacle] = None

    # Computed attributes :
    bestLayout: Layout = None
    panels: List[Panel] = None
    wallFixationMatrix: List[List[WallFixationPoint]] = None
    beamAssemblies: List[BeamAssembly] = None
    mouldings: List[Moulding] = None

    # 3D matrix4 :
    transform: List[List[float]] = None

    # Initialize computed attributes if they didn't have been provided by the json/dict
    def update_from_dict(self):
        if not self.bestLayout:
            self._setBestLayout()
        if not self.panels:
            self._setPanels()
        if not self.wallFixationMatrix:
            self._setAvailableFixationList(
                Point2D(self.bestLayout.jointsList[1], STANDARD_BEAM_WIDTH / 2)
            )
        if not self.beamAssemblies:
            self._setBeamAssemblies()
        if not (self.mouldings):
            self.setMouldings()

    def _setBestLayout(self):
        leftPanelWidth = [
            0 + 0.1 * i for i in range(1, 10 * int(STANDARD_PANEL_WIDTH * 100) + 1)
        ]
        # leftPanelWidth = range(1,int(STANDARD_PANEL_WIDTH*100)+1)
        layoutList = []
        errorList = []
        nbPanelList = []

        for k in leftPanelWidth:
            nbPanels = int(math.ceil((self.width - k / 100) / STANDARD_PANEL_WIDTH)) + 1
            xPanel = [
                round(k / 100 + i * STANDARD_PANEL_WIDTH, 4) for i in range(0, nbPanels)
            ]
            xPanel.insert(0, 0)
            xPanel[-1] = round(self.width, 4)

            tryLayout = Layout(jointsList=xPanel)
            tryLayout.error = self.getLayoutError(tryLayout)
            layoutList.append(tryLayout)
            nbPanelList.append(nbPanels)
            errorList.append(tryLayout.error)
        minError = min(errorList)
        minErrorIndex = []
        for index, value in enumerate(errorList):
            if value == minError:
                minErrorIndex.append(index)
        minNbPanel = min(nbPanelList)
        minNbPanelIndex = []
        for index, value in enumerate(nbPanelList):
            if value == minNbPanel:
                minNbPanelIndex.append(index)

        # find the common values using set intersection (l'erreur la plus faible prévaut sur le nombre de panneaux)
        minErrorAndNbPanelIndex = []
        minErrorAndNbPanelIndex = list(
            set(minErrorIndex).intersection(set(minNbPanelIndex))
        )
        if minErrorAndNbPanelIndex == []:
            minErrorAndNbPanelIndex = minErrorIndex

        # In case of multiple scenario, take a standard width for the left pannel (if it has the minimal error)
        if STANDARD_PANEL_WIDTH in minErrorAndNbPanelIndex:
            self.bestLayout = layoutList[STANDARD_PANEL_WIDTH]
        # If standard width does not have the minimal error, try to have left and right panels as big as possible
        else:
            bestLeftWidth = round(
                (
                    layoutList[0].jointsList[1]
                    - layoutList[0].jointsList[0]
                    + layoutList[0].jointsList[-1]
                    - layoutList[0].jointsList[-2]
                )
                / 2,
                4,
            )

            self.bestLayout = layoutList[
                minErrorAndNbPanelIndex[
                    min(
                        range(len(minErrorAndNbPanelIndex)),
                        key=lambda i: abs(minErrorAndNbPanelIndex[i] - bestLeftWidth),
                    )
                ]
            ]

    def getBestLayout(self):
        return self.bestLayout

    def getLayoutError(self, layout):
        error = 0

        for j in range(0, len(self.obstacles)):
            currentObstacle = Obstacle()
            currentObstacle.yBottom = self.obstacles[j].yBottom
            currentObstacle.xLeft = self.obstacles[j].xLeft
            currentObstacle.yTop = self.obstacles[j].yTop
            currentObstacle.width = self.obstacles[j].width
            currentObstacle.height = self.obstacles[j].height
            currentObstacle.topDistanceFromTopWall = self.obstacles[
                j
            ].topDistanceFromTopWall
            for i in range(0, len(layout.jointsList) - 1):
                # Error on left side of the obstacle
                if (
                    currentObstacle.xLeft < layout.jointsList[i + 1]
                    and currentObstacle.xLeft >= layout.jointsList[i]
                ):
                    if (
                        currentObstacle.xLeft - layout.jointsList[i]
                        < MIN_PANEL_FULLWIDTH
                    ):
                        error += (
                            MIN_PANEL_FULLWIDTH
                            - currentObstacle.xLeft
                            + layout.jointsList[i]
                        )
                # Error on right side of the obstacle
                if (
                    (currentObstacle.xLeft + currentObstacle.width)
                    < layout.jointsList[i + 1]
                ) and (
                    (currentObstacle.xLeft + currentObstacle.width)
                    >= layout.jointsList[i]
                ):
                    if (
                        layout.jointsList[i + 1]
                        - (currentObstacle.xLeft + currentObstacle.width)
                        < MIN_PANEL_FULLWIDTH
                    ):
                        error += (
                            MIN_PANEL_FULLWIDTH
                            - layout.jointsList[i + 1]
                            + (currentObstacle.xLeft + currentObstacle.width)
                        )
        return error

    def _setPanels(self):
        panels = []
        panelsCount = len(self.bestLayout.jointsList) - 1

        for i in range(panelsCount):
            panel = Panel(
                xLeft=self.bestLayout.jointsList[i],
                xRight=self.bestLayout.jointsList[i + 1],
                width=self.bestLayout.jointsList[i + 1] - self.bestLayout.jointsList[i],
                height=self.height,
                id=f"Panel {i}",
            )
            panel.update_from_dict(self.obstacles)
            panel.center3D = self.set3DCenterForChild(panel)
            # if Panel.shape is I2 we need to split the Panel into two Panels: I2Top and I2Bottom.
            if panel.shape == "i2":
                panel.shape = "i2t"
                i2bPanel = Panel(
                    xLeft=self.bestLayout.jointsList[i],
                    xRight=self.bestLayout.jointsList[i + 1],
                    width=self.bestLayout.jointsList[i + 1]
                    - self.bestLayout.jointsList[i],
                    height=self.height,
                    id=f"Panel {i}",
                    isI2bottom=True,
                )
                i2bPanel.update_from_dict(self.obstacles)
                i2bPanel.shape = "i2b"
                i2bPanel.center3D = self.set3DCenterForChild(i2bPanel)
                panels.append(i2bPanel)
            panels.append(panel)

        self.panels = panels

    def getPanels(self):
        return self.panels

    def _setAvailableFixationList(self, pointRef):
        # point de réference
        xref = pointRef.x
        yref = pointRef.y
        available = True

        x, y = np.mod(xref, STANDARD_DISTANCE_BTW_TWO_HOLES), np.mod(
            yref, STANDARD_DISTANCE_BTW_TWO_HOLES
        )
        xIndex = 0
        yIndex = 0

        availableFixationList = []
        while x <= self.width:
            while y <= self.height:  # Continue jusqu'à atteindre le haut du mur
                # Continue jusqu'à atteindre le bord droit du mur
                point = WallFixationPoint()
                point.x = x
                point.y = y
                point.available = available
                point.xIndex = xIndex
                point.yIndex = yIndex
                availableFixationList.append(point)
                y += STANDARD_DISTANCE_BTW_TWO_HOLES  # Se déplacer vers la droite de 6 cm
                yIndex += 1
            x += STANDARD_DISTANCE_BTW_TWO_HOLES  # Monter de 6 cm
            xIndex += 1
            y = np.mod(
                yref, STANDARD_DISTANCE_BTW_TWO_HOLES
            )  # Réinitialiser x à 0 pour le prochain niveau de y

            yIndex = 0

        for i in range(len(availableFixationList)):
            for obstacle in self.obstacles:
                if (
                    availableFixationList[i].x
                    >= obstacle.xLeft - STANDARD_DISTANCE_BTW_TWO_HOLES / 2
                    and availableFixationList[i].x
                    <= obstacle.xRight + STANDARD_DISTANCE_BTW_TWO_HOLES / 2
                    and availableFixationList[i].y
                    >= obstacle.yBottom - STANDARD_DISTANCE_BTW_TWO_HOLES / 2
                    and availableFixationList[i].y
                    <= obstacle.yTop + STANDARD_DISTANCE_BTW_TWO_HOLES / 2
                ):
                    availableFixationList[i].available = False

        # Déterminer le nombre de lignes et de colonnes
        nbLignes = availableFixationList[-1].yIndex + 1
        nbColonnes = availableFixationList[-1].xIndex + 1

        # Création d'une matrice vide
        matrice = [[None] * nbLignes for _ in range(nbColonnes)]
        # Remplissage de la matrice à partir de la liste
        for point in availableFixationList:
            matrice[point.xIndex][point.yIndex] = point

        # Maintenant, matrice est une matrice 2D contenant vos points de fixation
        # Affichage de la matrice
        self.wallFixationMatrix = matrice
        # Supprimer la première colonne si x < 0.03
        if self.wallFixationMatrix[0][0].x < 0.03:
            self.wallFixationMatrix = self.wallFixationMatrix[1:]

        # Supprimer la dernière colonne si wall.width - x < 0.03
        if self.width - self.wallFixationMatrix[-1][0].x < 0.03:
            self.wallFixationMatrix = self.wallFixationMatrix[:-1]

        # Supprimer la première ligne si y < 0.03
        if self.wallFixationMatrix[0][0].y < 0.03:
            self.wallFixationMatrix = [col[1:] for col in self.wallFixationMatrix]
            # a voir
            # self.wallFixationMatrix= self.wallFixationMatrix[:][1:]

        # Supprimer la dernière ligne si wall.height - y < 0.03
        if self.height - self.wallFixationMatrix[0][-1].y < 0.03:
            self.wallFixationMatrix = [col[:-1] for col in self.wallFixationMatrix]
        # updateIndex
        for x, row in enumerate(self.wallFixationMatrix):
            for y, fixation_point in enumerate(row):
                fixation_point.xIndex = x
                fixation_point.yIndex = y

    def findClosestPoint(self, point, direction):
        num_rows = self.wallFixationMatrix[-1][-1].xIndex
        num_columns = self.wallFixationMatrix[-1][-1].yIndex

        if direction == "TopRight":
            xIndex = min(
                max(
                    0,
                    int(
                        (point.x - self.wallFixationMatrix[0][0].x)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                        + 1
                    ),
                ),
                num_rows,
            )
            yIndex = min(
                max(
                    0,
                    int(
                        (point.y - self.wallFixationMatrix[0][0].y)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                        + 1
                    ),
                ),
                num_columns,
            )

        elif direction == "TopLeft":
            xIndex = min(
                max(
                    0,
                    int(
                        (point.x - self.wallFixationMatrix[0][0].x)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                    ),
                ),
                num_rows,
            )
            yIndex = min(
                max(
                    0,
                    int(
                        (point.y - self.wallFixationMatrix[0][0].y)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                        + 1
                    ),
                ),
                num_columns,
            )

        elif direction == "BottomRight":
            xIndex = min(
                max(
                    0,
                    int(
                        (point.x - self.wallFixationMatrix[0][0].x)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                        + 1
                    ),
                ),
                num_rows,
            )
            yIndex = min(
                max(
                    0,
                    int(
                        (point.y - self.wallFixationMatrix[0][0].y)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                    ),
                ),
                num_columns,
            )

        elif direction == "BottomLeft":
            xIndex = min(
                max(
                    0,
                    int(
                        (point.x - self.wallFixationMatrix[0][0].x)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                    ),
                ),
                num_rows,
            )
            yIndex = min(
                max(
                    0,
                    int(
                        (point.y - self.wallFixationMatrix[0][0].y)
                        // STANDARD_DISTANCE_BTW_TWO_HOLES
                    ),
                ),
                num_columns,
            )

        else:
            print("Invalid direction")

        return self.wallFixationMatrix[xIndex][yIndex]

    def set_available(self, points):
        for point in points:
            self.wallFixationMatrix[point.xIndex][point.yIndex].available = False

    def createBeamAssembly(
        self, category, startingPoint, pointRefEnd, openingDirection
    ):
        fixationPoints = self._getFixationPointsBetweenTwoPoints(
            startingPoint, pointRefEnd
        )
        # This logic shouldn't be handled in Wall...
        while fixationPoints and not fixationPoints[-1].available:
            fixationPoints.pop()
        while fixationPoints and not (fixationPoints[-1].available):
            fixationPoints.pop(0)

        if not self.beamAssemblies:
            self.beamAssemblies = []

        if len(fixationPoints) > 0:
            endPoint = fixationPoints[-1]
            while True:
                beamAssembly = BeamAssembly(
                    category=category,
                    wallFixationPoints=fixationPoints,
                    openingDirection=openingDirection,
                )
                beamAssembly.update_from_dict()
                self.beamAssemblies.append(beamAssembly)
                beamAssembly.category = category
                for beam in beamAssembly.beamList:
                    beam.center3D = self.set3DCenterForChild(beam)
                self.set_available(beamAssembly.wallFixationPoints)

                startingPoint = beamAssembly.wallFixationPoints[-1]
                if startingPoint == endPoint:
                    break

    # Return the list of all fixation points from self.wallFixationMatrix between two points (included) on the same axis.
    def _getFixationPointsBetweenTwoPoints(self, pointA, pointB):
        # DEBUG
        # print(f"\n_getFixationPointsBetweenTwoPoints(\n\t{pointA }\n\t{pointB}\n)")

        fixationPoints = []
        if pointA.xIndex == pointB.xIndex:
            for y in range(pointA.yIndex, pointB.yIndex + 1):
                fixationPoints.append(self.wallFixationMatrix[pointA.xIndex][y])
        if pointA.yIndex == pointB.yIndex:
            for x in range(pointA.xIndex, pointB.xIndex + 1):
                fixationPoints.append(self.wallFixationMatrix[x][pointA.yIndex])
        return fixationPoints

    def _setBeamAssemblies(self):
        # BeamBottom
        startingPoint = self.findClosestPoint(Point2D(0, 0), "TopRight")
        pointRefEnd = self.findClosestPoint(Point2D(self.width, 0), "TopLeft")
        self.createBeamAssembly("bottomWallBeams", startingPoint, pointRefEnd, "Top")

        # BeamTop
        startingPoint = self.findClosestPoint(Point2D(0, self.height), "BottomRight")
        pointRefEnd = self.findClosestPoint(
            Point2D(self.width, self.height), "BottomLeft"
        )
        self.createBeamAssembly("topWallBeams", startingPoint, pointRefEnd, "Bottom")

        # BeamLeft
        startingPoint = self.findClosestPoint(Point2D(0, 0), "TopRight")
        pointRefEnd = self.findClosestPoint(Point2D(0, self.height), "BottomRight")
        self.createBeamAssembly("leftWallBeams", startingPoint, pointRefEnd, "Right")

        # BeamRight
        startingPoint = self.findClosestPoint(Point2D(self.width, 0), "TopLeft")
        pointRefEnd = self.findClosestPoint(
            Point2D(self.width, self.height), "BottomLeft"
        )
        self.createBeamAssembly("rightWallBeams", startingPoint, pointRefEnd, "Left")

        # Beam Obstacle
        for obstacle in self.obstacles:
            # Beam Top Obstacle
            startingPoint = self.findClosestPoint(
                Point2D(
                    obstacle.xLeft - STANDARD_BEAM_WIDTH / 2,
                    obstacle.yTop + STANDARD_BEAM_WIDTH / 2,
                ),
                "TopLeft",
            )
            pointRefEnd = self.findClosestPoint(
                Point2D(
                    obstacle.xRight + STANDARD_BEAM_WIDTH / 2,
                    obstacle.yTop + STANDARD_BEAM_WIDTH / 2,
                ),
                "TopRight",
            )
            self.createBeamAssembly(
                "topObstacleBeams", startingPoint, pointRefEnd, "Top"
            )

            # Beam Bottom Obstacle
            startingPoint = self.findClosestPoint(
                Point2D(
                    obstacle.xLeft - STANDARD_BEAM_WIDTH / 2,
                    obstacle.yBottom - STANDARD_BEAM_WIDTH / 2,
                ),
                "BottomLeft",
            )
            pointRefEnd = self.findClosestPoint(
                Point2D(
                    obstacle.xRight + STANDARD_BEAM_WIDTH / 2,
                    obstacle.yBottom - STANDARD_BEAM_WIDTH / 2,
                ),
                "BottomRight",
            )
            self.createBeamAssembly(
                "bottomObstacleBeams", startingPoint, pointRefEnd, "Bottom"
            )

            # Beam Left Obstacle
            startingPoint = self.findClosestPoint(
                Point2D(
                    obstacle.xLeft - STANDARD_BEAM_WIDTH / 2,
                    obstacle.yBottom - STANDARD_BEAM_WIDTH / 2,
                ),
                "TopLeft",
            )
            pointRefEnd = self.findClosestPoint(
                Point2D(
                    obstacle.xLeft - STANDARD_BEAM_WIDTH / 2,
                    obstacle.yTop + STANDARD_BEAM_WIDTH / 2,
                ),
                "BottomLeft",
            )
            self.createBeamAssembly(
                "leftObstacleBeams", startingPoint, pointRefEnd, "Left"
            )

            # Beam Right Obstacle
            startingPoint = self.findClosestPoint(
                Point2D(
                    obstacle.xRight + STANDARD_BEAM_WIDTH / 2,
                    obstacle.yBottom - STANDARD_BEAM_WIDTH / 2,
                ),
                "TopRight",
            )
            pointRefEnd = self.findClosestPoint(
                Point2D(
                    obstacle.xRight + STANDARD_BEAM_WIDTH / 2,
                    obstacle.yTop + STANDARD_BEAM_WIDTH / 2,
                ),
                "BottomRight",
            )
            self.createBeamAssembly(
                "rightObstacleBeams", startingPoint, pointRefEnd, "Right"
            )

        # verticale  Beams
        for i in range(1, len(self.bestLayout.jointsList) - 1):
            # point start et point End
            for ligne in self.wallFixationMatrix:
                for case in ligne:
                    if (
                        round(case.x, 3) == round(self.bestLayout.jointsList[i], 3)
                        and case.y == 0.09
                    ):
                        startingPoint = case
                        pointRefEnd = self.wallFixationMatrix[case.xIndex][-2]
            self.createBeamAssembly(
                "verticalWallBeams", startingPoint, pointRefEnd, "Right"
            )

        return self

    def getBeamAssemblies(self):
        return self.beamAssemblies

    def setMouldings(self):
        mouldings = []
        if len(self.obstacles) == 0:
            PointStartMoulding = 0
            PointEndMoulding = self.width
            moulding = Moulding(
                position="Bottom",
                xLeft=PointStartMoulding,
                xRight=PointEndMoulding,
                heightWall=self.height,
            )

            moulding.update_from_dict()
            moulding.center = self.set3DCenterForChild(moulding)
            mouldings.append(moulding)
            print("Top moulding with no obstacles\n")
            moulding = Moulding(
                position="Top",
                xLeft=PointStartMoulding,
                xRight=PointEndMoulding,
                heightWall=self.height,
            )

            moulding.update_from_dict()
            moulding.center = self.set3DCenterForChild(moulding)
            mouldings.append(moulding)
        else:
            PointStartMouldingBottom = 0
            PointStartMouldingTop = 0
            for index in range(0, len(self.obstacles)):
                if index != len(self.obstacles) - 1:
                    indexObstacle = index
                else:
                    indexObstacle = -1
                if round(self.obstacles[indexObstacle].yBottom) == 0:
                    PointEndMouldingBottom = self.obstacles[indexObstacle].xLeft
                    moulding = Moulding(
                        position="Bottom",
                        xLeft=PointStartMouldingBottom,
                        xRight=PointEndMouldingBottom,
                        heightWall=self.height,
                    )
                    moulding.update_from_dict()
                    moulding.center = self.set3DCenterForChild(moulding)
                    mouldings.append(moulding)
                    PointStartMouldingBottom = (
                        PointEndMouldingBottom + self.obstacles[indexObstacle].width
                    )
                else:
                    PointEndMouldingBottom = self.obstacles[indexObstacle + 1].xLeft

                if self.obstacles[indexObstacle].yTop == self.height:
                    PointEndMouldingTop = self.obstacles[indexObstacle].xLeft
                    print("Top moulding with obstacle on top.\n")
                    moulding = Moulding(
                        position="Top",
                        xLeft=PointStartMouldingTop,
                        xRight=PointEndMouldingTop,
                        heightWall=self.height,
                    )
                    print(moulding, "\n")
                    moulding.update_from_dict()
                    print(moulding, "\n")
                    moulding.center = self.set3DCenterForChild(moulding)
                    mouldings.append(moulding)
                    PointStartMouldingTop = (
                        PointEndMouldingTop + self.obstacles[indexObstacle].width
                    )
                else:
                    PointEndMouldingTop = self.obstacles[indexObstacle + 1].xLeft

            PointEndMouldingBottom = self.width
            moulding = Moulding(
                position="Bottom",
                xLeft=PointStartMouldingBottom,
                xRight=PointEndMouldingBottom,
                heightWall=self.height,
            )

            moulding.update_from_dict()
            moulding.center = self.set3DCenterForChild(moulding)
            mouldings.append(moulding)
            PointEndMouldingTop = self.width

            print("Top moulding with obstacle not on top.\n")
            moulding = Moulding(
                position="Top",
                xLeft=PointStartMouldingTop,
                xRight=PointEndMouldingTop,
                heightWall=self.height,
            )
            print("moulding bedore update:", moulding, "\n")
            moulding.update_from_dict()
            print("moulding after update", moulding, "\n")
            moulding.center = self.set3DCenterForChild(moulding)
            mouldings.append(moulding)
        self.mouldings = mouldings
        print("\n", self.mouldings)

    def set3DCenterForChild(self, child):
        # TODO: RENAME ! What is "D" and "E"?
        D = -self.width / 2 + child.center2D.x
        E = -self.height / 2 + child.center2D.y
        center3D = Point()
        center3D.x = (
            (D * self.transform[0][0]) + (E * self.transform[1][0]) + self.center.x
        )
        center3D.y = (
            (D * self.transform[0][1]) + (E * self.transform[1][1]) + self.center.y
        )
        center3D.z = (
            (D * self.transform[0][2]) + (E * self.transform[1][2]) + self.center.z
        )
        return center3D

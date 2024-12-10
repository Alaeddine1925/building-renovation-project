from typing import List
from marshmallow_dataclass import dataclass
from dataclasses import field

from model.Beam import Beam
from model.WallFixationPoint import WallFixationPoint
from model.constantesGlobales import (
    STANDARD_BEAM_LENGTH,
    STANDARD_DISTANCE_BTW_TWO_HOLES,
)


@dataclass
class BeamAssembly:
    category: str = None
    orientation: str = None
    openingDirection: str = None
    wallFixationPoints: List[WallFixationPoint] = field(default_factory=list)
    startingPoint: WallFixationPoint = None
    endPoint: WallFixationPoint = None
    beamList: List[Beam] = field(default_factory=list)

    # def __init__(
    #     self,
    #     wallFixations: [WallFixationPoint] = None,
    #     openingDirection: str = "Top",
    #     orientation: str = None,
    # ):
    #     # Setting openingDirection, which is an enum to display which direction the U shape of the beams looks toward.
    #     self.openingDirection = openingDirection

    #     # Setting orientation(horizontal or vertical) of the beams,
    #     # if it's not set by the user it will be calculated using wallFixations list.
    #     if orientation != None:
    #         self.orientation = orientation
    #     elif wallFixations != None:
    #         self._setOrientation(wallFixations[0], wallFixations[-1], orientation)

    #     # Setting wallFixations, starting and end points and generating the beamsList
    #     if wallFixations != None:
    #         self._setPoints(wallFixations[0], wallFixations[-1])
    #         self._setWallFixationPoints(wallFixations)
    #         self._setBeamList()

    def update_from_dict(self):
        self._setOrientation(self.wallFixationPoints[0], self.wallFixationPoints[-1])
        self._setPoints(self.wallFixationPoints[0], self.wallFixationPoints[-1])
        self._setWallFixationPoints(self.wallFixationPoints)
        self._setBeamList()

    def _setBeamList(self):
        self.beamList = []
        holesPerBeam = int(STANDARD_BEAM_LENGTH / STANDARD_DISTANCE_BTW_TWO_HOLES)
        splitWallFixationPoints = [
            self.wallFixationPoints[j : j + holesPerBeam]
            for j in range(0, len(self.wallFixationPoints), holesPerBeam)
        ]
        for index, beam in enumerate(splitWallFixationPoints):
            beam = Beam(
                orientation=self.orientation,
                opening=self.openingDirection,
                wallFixations=beam,
            )
            beam.update_from_dict()
            self.beamList.append(beam)

    def _setOrientation(
        self, pointA: WallFixationPoint, pointB: WallFixationPoint, orientation=None
    ):
        # If the BeamAssembly is one hole long, we must specify the orientation manually.
        if pointA == pointB:
            if orientation == None:
                raise ValueError(
                    "Orientation must be define manually if BeamAssembly is only one hole long."
                )
            else:
                self.orientation = orientation
        # If pointA and pointB are on the same abscissa the BeamAssembly is vertical...
        elif pointA.xIndex == pointB.xIndex:
            self.orientation = "Vertical"
        # ... else if pointA and pointB are on the same ordinate the BeamAssembly is horizontal...
        elif pointA.yIndex == pointB.yIndex:
            self.orientation = "Horizontal"
        else:
            # ... Otherwise the points are not on the same line.
            raise ValueError(
                "wallFixationPointA and wallFixationPointB must be on the same line."
            )

    def _setPoints(self, pointA: WallFixationPoint, pointB: WallFixationPoint):
        # If the beamAssembly is horizontal, the startingPoint is the point on the Left and the endPoint is the point on the right
        if self.orientation == "Horizontal":
            if pointA.xIndex <= pointB.xIndex:
                self.startingPoint = pointA
                self.endPoint = pointB
            else:
                self.startingPoint = pointB
                self.endPoint = pointA
        # If the beamAssembly is vertical, the startingPoint is the point on the bottom and the endPoint is the point on the top
        if self.orientation == "Vertical":
            if pointA.yIndex <= pointB.yIndex:
                self.startingPoint = pointA
                self.endPoint = pointB
            else:
                self.startingPoint = pointB
                self.endPoint = pointA

    def _setWallFixationPoints(self, wallFixations):
        fixationPoints = []

        currentPoint = self.startingPoint
        indice = 0
        while indice < len(wallFixations) and not (currentPoint.available):
            indice += 1
            if indice < len(wallFixations):
                currentPoint = wallFixations[indice]
        while (indice < len(wallFixations)) and (currentPoint.available):
            fixationPoints.append(currentPoint)
            indice += 1
            if indice < len(wallFixations):
                currentPoint = wallFixations[indice]
        self.wallFixationPoints = fixationPoints

from typing import List
from marshmallow_dataclass import dataclass
from dataclasses import field

from model.Point import Point
from model.Point2D import Point2D
from model.WallFixationPoint import WallFixationPoint
from model.constantesGlobales import (
    STANDARD_DISTANCE_BTW_TWO_HOLES,
    STANDARD_BEAM_WIDTH,
)


@dataclass
class Beam:
    id: str = None
    orientation: str = None
    opening: str = None
    wallFixations: List[WallFixationPoint] = field(default_factory=list)

    length: float = 0
    width: float = 0
    height: float = 0

    # Position in 2D relative to the Wall bottom left corner.
    xLeft: float = 0
    xRight: float = 0
    yTop: float = 0
    yBottom: float = 0

    center2D: Point2D = Point2D()
    center3D: Point = Point()

    def update_from_dict(self):
        self._setX()
        self._setY()
        self._setCenter()

        self.height = (
            STANDARD_BEAM_WIDTH
            if self.orientation == "Horizontal"
            else round((len(self.wallFixations) * STANDARD_DISTANCE_BTW_TWO_HOLES), 2)
        )
        self.width = (
            round((len(self.wallFixations) * STANDARD_DISTANCE_BTW_TWO_HOLES), 2)
            if self.orientation == "Horizontal"
            else STANDARD_BEAM_WIDTH
        )
        self.length = self.height if self.orientation == "Vertical" else self.width

        self.id = f"Beam {self.orientation} {int(self.length)}"

    # @staticmethod
    # def from_dict(data):
    #     beam = Beam()
    #     for field, value in data.items():
    #         setattr(beam, field, value)
    #     return beam

    # Set xLeft and xRight positions based on the orientation and the first and last WallFixationPoint of the Beam.
    def _setX(self):
        self.xLeft = self.wallFixations[0].x - (STANDARD_BEAM_WIDTH / 2)
        if self.orientation == "Vertical":
            self.xRight = self.wallFixations[0].x + (STANDARD_BEAM_WIDTH / 2)
        else:
            self.xRight = self.wallFixations[-1].x + (STANDARD_BEAM_WIDTH / 2)

    # Set yBottom and yTop positions based on the orientation and the first and last WallFixationPoint of the Beam.
    def _setY(self):
        self.yBottom = self.wallFixations[0].y - (STANDARD_BEAM_WIDTH / 2)
        if self.orientation == "Vertical":
            self.yTop = self.wallFixations[-1].y + (STANDARD_BEAM_WIDTH / 2)
        else:
            self.yTop = self.wallFixations[0].y + (STANDARD_BEAM_WIDTH / 2)

    # Set the center of the Beam.
    def _setCenter(self):
        xCenter = (self.xLeft + self.xRight) / 2
        yCenter = (self.yBottom + self.yTop) / 2
        self.center2D = Point2D(xCenter, yCenter)

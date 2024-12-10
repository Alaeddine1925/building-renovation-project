from marshmallow_dataclass import dataclass
from model.constantesGlobales import STANDARD_BEAM_WIDTH
from model.Point2D import Point2D
from model.Point import Point


@dataclass
class Moulding:
    id: str = None
    width: float = None
    height: float = None
    heightWall: float = None
    xLeft: float = None
    xRight: float = None
    yBottom: float = None
    yTop: float = None
    position: str = None
    center2D: Point2D = None
    center: Point = None

    def update_from_dict(self):
        self.width = self.xRight - self.xLeft
        self.height = STANDARD_BEAM_WIDTH
        if self.position == "Bottom":
            self.yBottom = 0
            self.yTop = STANDARD_BEAM_WIDTH
        elif self.position == "Top":
            self.yBottom = self.heightWall - STANDARD_BEAM_WIDTH
            self.yTop = self.heightWall
        self.center2D = Point2D(
            (self.xLeft + self.xRight) / 2, (self.yBottom + self.yTop) / 2
        )

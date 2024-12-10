from marshmallow_dataclass import dataclass

from model.Point import Point
from model.Point2D import Point2D


@dataclass
class Clip:
    center2D: Point2D = Point2D(0, 0)
    center3D: Point = Point(0, 0, 0)
    orientation: str = None

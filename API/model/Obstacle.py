from typing import List
from marshmallow_dataclass import dataclass
from dataclasses import field

from model.Point import Point

# from model.Corners import Corners


@dataclass
class Obstacle:
    id: str = None
    width: float = None
    height: float = None
    xLeft: float = None
    xRight: float = None
    yBottom: float = None
    yTop: float = None
    topDistanceFromTopWall: float = None
    center: Point = Point()
    transform: List[List[float]] = field(default_factory=list)
    # corners: Corners = Corners()

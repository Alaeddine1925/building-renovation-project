from typing import ClassVar, Type
from marshmallow_dataclass import dataclass
from dataclasses import field
from marshmallow import Schema

from model.Point import Point


# Un mur a 4 corners (rectangle). Ces corners sont utilisés pour définir les distances
@dataclass
class Corners:
    bottomLeft: Point = field(default=Point)
    topLeft: Point = field(default=Point)
    bottomRight: Point = field(default=Point)
    topRight: Point = field(default=Point)
    Schema: ClassVar[Type[Schema]] = Schema

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        corners = Corners()
        for field, value in data.items():
            setattr(corners, field, value)
        return corners

from marshmallow_dataclass import dataclass


@dataclass
class Point:
    x: float = 0
    y: float = 0
    z: float = 0

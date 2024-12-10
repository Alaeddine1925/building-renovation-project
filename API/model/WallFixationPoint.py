from marshmallow_dataclass import dataclass
from dataclasses import fields, field


@dataclass
class WallFixationPoint:
    x: float = field(default=None)
    y: float = field(default=None)
    xIndex: int = field(default=None)
    yIndex: int = field(default=None)
    available: bool = field(default=True)

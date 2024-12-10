from typing import List
from marshmallow_dataclass import dataclass
from dataclasses import field


@dataclass
class Layout:
    jointsList: List[float] = field(default_factory=list)
    error: float = None

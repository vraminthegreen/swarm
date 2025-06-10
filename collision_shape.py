from dataclasses import dataclass
from typing import Tuple

@dataclass
class CollisionShape:
    """Simple circular collision shape."""

    center: Tuple[float, float]
    radius: float

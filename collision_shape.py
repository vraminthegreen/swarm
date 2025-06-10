from dataclasses import dataclass
from typing import Tuple

@dataclass
class CollisionShape:
    """Simple circular collision shape."""

    center: Tuple[float, float]
    radius: float

    def collidesWith(self, other: "CollisionShape") -> bool:
        """Return ``True`` if this shape intersects ``other``."""
        if other is None:
            return False
        dx = self.center[0] - other.center[0]
        dy = self.center[1] - other.center[1]
        distance_sq = dx * dx + dy * dy
        return distance_sq <= (self.radius + other.radius) ** 2

import math
import pygame

from stage import Stage
from explosion import Explosion


class CannonBullet(Stage):
    """Projectile moving from start to end position with a pulsing size."""

    BASE_SPEED = 4

    def __init__(self, owner, pos1, pos2):
        super().__init__()
        self.owner = owner
        self.start = pos1
        self.end = pos2
        self.pos = pos1
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        self.distance = math.hypot(dx, dy)
        if self.distance == 0:
            self.dir = (0.0, 0.0)
        else:
            self.dir = (dx / self.distance, dy / self.distance)
        self.traveled = 0.0
        # Use a light blue "plasma" color for the projectile
        self.color = (150, 220, 255)

    def getPosition(self):
        return self.pos

    def _tick(self, dt):
        move = self.BASE_SPEED * dt
        self.traveled += move
        if self.traveled >= self.distance:
            self.pos = self.end
            parent = getattr(self, "_parent", None)
            if parent is not None:
                explosion = Explosion(self.pos)
                parent.add_stage(explosion)
                explosion.show()
                parent.remove_stage(self)
            return
        self.pos = (
            self.start[0] + self.dir[0] * self.traveled,
            self.start[1] + self.dir[1] * self.traveled,
        )

    def _draw(self, screen):
        if self.distance == 0:
            radius = 4
        else:
            frac = self.traveled / self.distance
            radius = 4 + 6 * (1 - 4 * (frac - 0.5) ** 2)
            if radius < 4:
                radius = 4
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), int(radius))

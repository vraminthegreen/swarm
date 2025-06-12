import math
import pygame

from stage import Stage


class ParticleArrow(Stage):
    """Moving line particle traveling from a start to end position."""

    def __init__(self, length=5, start_speed=10, end_speed=5, color=(255, 255, 150)):
        super().__init__()
        self.length = length
        self.start_speed = start_speed
        self.end_speed = end_speed
        self.color = color
        self._particles = []

    def addParticle(self, startingPos, endingPos):
        """Add a new arrow particle moving from ``startingPos`` to ``endingPos``."""
        dx = endingPos[0] - startingPos[0]
        dy = endingPos[1] - startingPos[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        direction = (dx / distance, dy / distance)
        self._particles.append(
            {
                "start": startingPos,
                "end": endingPos,
                "dir": direction,
                "distance": distance,
                "traveled": 0.0,
                "pos": startingPos,
            }
        )

    def _tick(self, dt):
        to_remove = []
        for p in self._particles:
            frac = p["traveled"] / p["distance"] if p["distance"] else 1.0
            speed = self.start_speed + (self.end_speed - self.start_speed) * frac
            move = speed * dt
            p["traveled"] += move
            if p["traveled"] >= p["distance"]:
                to_remove.append(p)
                continue
            nx = p["start"][0] + p["dir"][0] * p["traveled"]
            ny = p["start"][1] + p["dir"][1] * p["traveled"]
            p["pos"] = (nx, ny)
        for p in to_remove:
            self._particles.remove(p)

    def _draw(self, screen):
        for p in self._particles:
            x, y = p["pos"]
            dx, dy = p["dir"]
            start = (x, y)
            end = (x + dx * self.length, y + dy * self.length)
            pygame.draw.line(screen, self.color, start, end)

import random
import pygame
from stage import Stage
from collision_shape import CollisionShape


class Explosion(Stage):
    """Expanding circle animation used for cannon impacts."""

    EXPLOSION_KILL_PROBABILITY = 0.3

    def __init__(self, pos, max_radius=50, duration=15, owner=None):
        super().__init__()
        self.pos = pos
        self.max_radius = max_radius
        self.duration = duration
        self.age = 0
        self.start_radius = 4
        self.owner = owner
        self._collecting = False
        self._collisions = []
        self._processed = False

    def current_radius(self):
        """Return the current radius of the explosion."""
        frac = min((self.age * 2) / self.duration, 1)
        progress = 1 - (1 - frac) ** 2
        return self.start_radius + (self.max_radius - self.start_radius) * progress

    def _tick(self, dt):
        self.age += dt
        if self.age > self.duration:
            if not self._processed:
                for swarm in self._collisions:
                    if not swarm.ants:
                        continue
                    removed = []
                    for idx in range(len(swarm.ants)):
                        if random.random() < self.EXPLOSION_KILL_PROBABILITY:
                            removed.append(idx)
                    for idx in reversed(removed):
                        swarm.ants.pop(idx)
                    if removed:
                        swarm._invalidate_centroid_cache()
                self._processed = True
            parent = getattr(self, "_parent", None)
            if parent is not None:
                parent.remove_stage(self)
            return

        self._collecting = self.age >= self.duration - 1

    def getCollisionShape(self):
        if not self._collecting:
            return None
        return CollisionShape(self.pos, self.current_radius())

    def onCollision(self, stage):
        if not self._collecting:
            return
        if hasattr(stage, "ants") and self.owner and self.owner.isEnemy(stage):
            if stage not in self._collisions:
                self._collisions.append(stage)

    def _draw(self, screen):
        if self.age > self.duration:
            return
        frac = min((self.age * 2) / self.duration, 1)
        # Ease-out quadratic: fast start, slow end
        progress = 1 - (1 - frac) ** 2
        radius = self.start_radius + (self.max_radius - self.start_radius) * progress
        alpha = int(255 * (1 - frac))
        color = (255, 165, 0, alpha)
        surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.max_radius, self.max_radius), int(radius))
        screen.blit(surface, (self.pos[0] - self.max_radius, self.pos[1] - self.max_radius))

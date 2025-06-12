import pygame
from stage import Stage


class Explosion(Stage):
    """Expanding circle animation used for cannon impacts."""

    def __init__(self, pos, max_radius=50, duration=15):
        super().__init__()
        self.pos = pos
        self.max_radius = max_radius
        self.duration = duration
        self.age = 0
        self.start_radius = 4

    def current_radius(self):
        """Return the current radius of the explosion."""
        frac = min(self.age / self.duration, 1)
        progress = 1 - (1 - frac) ** 2
        return self.start_radius + (self.max_radius - self.start_radius) * progress

    def _tick(self, dt):
        self.age += dt
        if self.age >= self.duration:
            parent = getattr(self, "_parent", None)
            if parent is not None:
                parent.remove_stage(self)
            return

    def _draw(self, screen):
        if self.age > self.duration:
            return
        frac = min(self.age / self.duration, 1)
        # Ease-out quadratic: fast start, slow end
        progress = 1 - (1 - frac) ** 2
        radius = self.start_radius + (self.max_radius - self.start_radius) * progress
        alpha = int(255 * (1 - frac))
        color = (255, 165, 0, alpha)
        surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.max_radius, self.max_radius), int(radius))
        screen.blit(surface, (self.pos[0] - self.max_radius, self.pos[1] - self.max_radius))

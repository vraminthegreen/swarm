import pygame

from stage import Stage


class ParticleShot(Stage):
    """Stage element displaying temporary particle effects."""

    def __init__(self, cycles=3, visible_frames=3, hidden_frames=3, color=(255, 255, 150)):
        super().__init__()
        self.cycles = cycles
        self.visible_frames = visible_frames
        self.hidden_frames = hidden_frames
        self.color = color
        self._particles = []

    def addParticle(self, pos):
        """Add a particle at ``pos``."""
        particle = {
            "pos": pos,
            "cycles_left": self.cycles,
            "show_left": self.visible_frames,
            "hide_left": self.hidden_frames,
            "visible": True,
        }
        self._particles.append(particle)

    def _tick(self, dt):
        to_remove = []
        for p in self._particles:
            if p["visible"]:
                p["show_left"] -= 1
                if p["show_left"] <= 0:
                    p["visible"] = False
                    p["hide_left"] = self.hidden_frames
            else:
                p["hide_left"] -= 1
                if p["hide_left"] <= 0:
                    p["cycles_left"] -= 1
                    if p["cycles_left"] <= 0:
                        to_remove.append(p)
                    else:
                        p["visible"] = True
                        p["show_left"] = self.visible_frames
        for p in to_remove:
            self._particles.remove(p)

    def _draw(self, screen):
        for p in self._particles:
            if p["visible"]:
                x, y = p["pos"]
                pygame.draw.circle(screen, self.color, (int(x), int(y)), 2)

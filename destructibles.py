from stage import Stage
from player import Player
from collision_shape import CollisionShape
import random
import math
import pygame


class Tree(Stage):
    """Static destructible object with hit points."""

    MAX_HP = 50

    def __init__(self, pos, size, owner=None):
        super().__init__()
        self.base_pos = pos
        self.size = size
        self.hp = self.MAX_HP
        self.owner = owner
        self.offset = (0.0, 0.0)
        self._shake_steps = []

    def getPosition(self):
        return (self.base_pos[0] + self.offset[0], self.base_pos[1] + self.offset[1])

    def getCollisionShape(self):
        return CollisionShape(self.getPosition(), self.size)

    def onCollision(self, stage):
        if self.owner and self.owner.isEnemy(stage):
            hit_prob = getattr(stage, "kill_probability", 1.0)
            if random.random() < hit_prob:
                self.hp -= 1
                amplitude = 1
                for _ in range(3):
                    angle = random.uniform(0, 2 * math.pi)
                    dx = math.cos(angle) * amplitude
                    dy = math.sin(angle) * amplitude
                    self._shake_steps.extend([(dx, dy), (-dx, -dy)])
                if self.hp <= 0:
                    parent = getattr(self, "_parent", None)
                    if parent is not None:
                        parent.remove_stage(self)

    def _tick(self, dt):
        if self._shake_steps:
            self.offset = self._shake_steps.pop(0)
        else:
            self.offset = (0.0, 0.0)

    def _draw(self, screen):
        color = (34, 139, 34)
        pos = self.getPosition()
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), int(self.size))


class Destructibles(Player):
    """Player controlling stationary destructible trees."""

    def __init__(self, width, height, num_trees=20, occupied=None):
        super().__init__()
        self.width = width
        self.height = height
        self.trees = []
        occupied = occupied if occupied is not None else set()

        for _ in range(num_trees):
            size = random.randint(10, 20)
            # Ensure trees spawn within bounds
            pos = (
                random.uniform(size, width - size),
                random.uniform(size, height - size),
            )
            tree = Tree(pos, size, owner=self)
            self.trees.append(tree)
            self.add_stage(tree)
            tree.show()
            occupied.add((int(pos[0]), int(pos[1])))


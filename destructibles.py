from stage import Stage
from player import Player
from collision_shape import CollisionShape
import random
import pygame


class Tree(Stage):
    """Static destructible object with hit points."""

    MAX_HP = 20

    def __init__(self, pos, size, owner=None):
        super().__init__()
        self.pos = pos
        self.size = size
        self.hp = self.MAX_HP
        self.owner = owner

    def getPosition(self):
        return self.pos

    def getCollisionShape(self):
        return CollisionShape(self.pos, self.size)

    def onCollision(self, stage):
        if self.owner and self.owner.isEnemy(stage):
            # Register a hit for each collision with an enemy stage
            self.hp -= 1
            if self.hp <= 0:
                parent = getattr(self, "_parent", None)
                if parent is not None:
                    parent.remove_stage(self)

    def _draw(self, screen):
        color = (34, 139, 34)
        pygame.draw.circle(screen, color, (int(self.pos[0]), int(self.pos[1])), int(self.size))


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


import os
import sys
import pygame
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from stage import Stage
from swarm import Swarm

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def create_swarm(pos, group_id):
    swarm = Swarm((255, 0, 0), group_id, (255, 100, 100), width=100, height=100)
    swarm.ants = [list(pos)]
    swarm.show()
    return swarm


def test_swarms_detect_collision():
    root = Stage()
    s1 = create_swarm((10, 10), 1)
    s2 = create_swarm((10, 10), 2)
    root.add_stage(s1)
    root.add_stage(s2)
    root.show()
    root.tick(0)
    assert s2 in s1.colliding_swarms
    assert s1 in s2.colliding_swarms


def test_collision_cleared_after_draw():
    root = Stage()
    s1 = create_swarm((10, 10), 1)
    s2 = create_swarm((10, 10), 2)
    root.add_stage(s1)
    root.add_stage(s2)
    root.show()
    root.tick(0)
    screen = pygame.Surface((100, 100))
    root.draw(screen)
    assert s1.colliding_swarms == []
    assert s2.colliding_swarms == []

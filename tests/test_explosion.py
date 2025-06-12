import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

pygame = pytest.importorskip('pygame')

import random
from explosion import Explosion
from stage import Stage
from player import Player
from swarm import Swarm

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_explosion_expires():
    exp = Explosion((0, 0), max_radius=20, duration=5)
    root = Stage()
    root.add_stage(exp)
    root.show()
    for _ in range(6):
        root.tick(1)
    assert exp not in root._children


def test_explosion_radius_growth():
    exp = Explosion((0, 0), max_radius=20, duration=5)
    exp.show()
    exp.tick(1)
    r1 = exp.current_radius()
    exp.tick(1)
    r2 = exp.current_radius()
    assert r2 > r1


def test_explosion_has_owner():
    owner = object()
    exp = Explosion((0, 0), max_radius=10, duration=3, owner=owner)
    assert exp.owner is owner


def test_explosion_damage_enemy(monkeypatch):
    attacker = Player()
    defender = Player()
    attacker.enemies.append(defender)
    defender.enemies.append(attacker)

    swarm = Swarm((255, 0, 0), 1, (255, 100, 100), width=100, height=100)
    swarm.owner = defender
    swarm.ants = [[0, 0], [10, 0], [20, 0]]
    swarm.show()

    root = Stage()
    exp = Explosion((0, 0), max_radius=10, duration=1, owner=attacker)
    root.add_stage(swarm)
    root.add_stage(exp)
    root.show()

    monkeypatch.setattr(random, "random", lambda: 0.0)

    root.tick(1)
    assert len(swarm.ants) == 3

    root.tick(1)
    assert len(swarm.ants) == 0


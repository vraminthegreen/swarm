import os
import sys
import pytest
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from player import Player
from swarm import Swarm
from destructibles import Tree


@pytest.fixture(autouse=True)
def init_pygame():
    pygame = pytest.importorskip('pygame')
    pygame.init()
    yield
    pygame.quit()


def create_tree_and_swarm():
    owner = Player()
    enemy = Player()
    owner.enemies.append(enemy)
    enemy.enemies.append(owner)

    tree = Tree((10, 10), 5, owner=owner)
    swarm = Swarm((255, 0, 0), 1, (255, 100, 100), width=100, height=100)
    swarm.owner = enemy
    swarm.ants = [[10, 10]]
    swarm.kill_probability = 0.5
    return tree, swarm


def test_tree_hit_reduces_hp_and_shakes(monkeypatch):
    tree, swarm = create_tree_and_swarm()
    monkeypatch.setattr(random, "random", lambda: 0.4)
    monkeypatch.setattr(random, "uniform", lambda a, b: 0.0)
    hp_before = tree.hp
    tree.onCollision(swarm)
    assert tree.hp == hp_before - 1
    assert tree._shake_steps[0] == pytest.approx((0.5, 0.0))


def test_tree_miss_no_damage(monkeypatch):
    tree, swarm = create_tree_and_swarm()
    monkeypatch.setattr(random, "random", lambda: 0.6)
    hp_before = tree.hp
    tree.onCollision(swarm)
    assert tree.hp == hp_before
    assert not tree._shake_steps

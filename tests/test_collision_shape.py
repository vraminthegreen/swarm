import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from stage import Stage
from swarm import Swarm
from collision_shape import CollisionShape


def test_stage_collision_shape_none():
    stage = Stage()
    assert stage.getCollisionShape() is None


def test_swarm_collision_shape():
    swarm = Swarm((255, 0, 0), group_id=1, flag_color=(255, 100, 100), width=100, height=100)
    swarm.ants = [[0, 0], [0, 10]]
    shape = swarm.getCollisionShape()
    assert isinstance(shape, CollisionShape)
    assert shape.center == (0, 5)
    assert shape.radius == 5


def test_swarm_collision_shape_empty():
    swarm = Swarm((255, 0, 0), group_id=1, flag_color=(255, 100, 100), width=100, height=100)
    assert swarm.getCollisionShape() is None

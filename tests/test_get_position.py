import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from stage import Stage
from flag import NormalFlag
from swarm import Swarm


def test_stage_default_position_none():
    stage = Stage()
    assert stage.getPosition() is None


def test_flag_get_position():
    flag = NormalFlag((10, 20))
    assert flag.getPosition() == (10, 20)


def test_swarm_get_position():
    swarm = Swarm((255, 0, 0), group_id=1, flag_color=(255, 100, 100), width=100, height=100)
    swarm.ants = [[10, 20], [20, 30], [30, 40]]
    assert swarm.getPosition() == (20, 30)


def test_swarm_get_position_empty():
    swarm = Swarm((255, 0, 0), group_id=1, flag_color=(255, 100, 100), width=100, height=100)
    assert swarm.getPosition() is None

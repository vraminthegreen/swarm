import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from swarm import Swarm
from flag import NormalFlag


def create_swarm():
    swarm = Swarm((255, 0, 0), group_id=1, flag_color=(255, 100, 100), width=100, height=100)
    swarm.ants.append([50, 50])
    swarm.show()
    return swarm


def test_last_flag_not_removed():
    swarm = create_swarm()
    swarm.queue.add_flag_at((50, 50), NormalFlag)
    assert len(swarm.queue) == 1
    swarm._tick(0)
    assert len(swarm.queue) == 1

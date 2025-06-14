import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flow_field import FlowField
from collision_shape import CollisionShape


def test_obstacle_margin_blocks_cells():
    ff = FlowField(50, 50, cell_size=1)
    obstacle = CollisionShape((20, 20), 5)
    ff.compute((40, 40), [obstacle], margin=5.0)
    assert ff.get_distance((25, 20)) == ff.INF
    assert ff.get_distance((31, 20)) != ff.INF

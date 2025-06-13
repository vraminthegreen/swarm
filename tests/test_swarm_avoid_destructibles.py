import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from stage import Stage
from destructibles import Destructibles, Tree
from swarm import Swarm

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

@pytest.fixture(autouse=True)
def init_pygame():
    pygame = pytest.importorskip('pygame')
    pygame.init()
    yield
    pygame.quit()


def test_unit_avoids_tree():
    root = Stage()
    destruct = Destructibles(100, 100, num_trees=0)
    tree = Tree((20, 20), 5, owner=destruct)
    destruct.trees.append(tree)
    destruct.add_stage(tree)
    root.destructibles = destruct
    root.add_stage(destruct)

    swarm = Swarm((255, 0, 0), 1, (255, 100, 100), width=100, height=100)
    swarm.ants = [[10, 20]]
    root.add_stage(swarm)

    proposed = [(20, 20)]
    result = swarm._resolve_positions(swarm.ants, proposed)
    assert result[0] == (10, 20)

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

pygame = pytest.importorskip('pygame')

from explosion import Explosion
from stage import Stage

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


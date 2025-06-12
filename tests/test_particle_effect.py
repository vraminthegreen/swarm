import os
import sys
import math
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

pygame = pytest.importorskip('pygame')

from swarm import Swarm, PARTICLE_DISTANCE

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_particle_added_on_attack():
    attacker = Swarm((255, 0, 0), 1, (255, 100, 100), width=100, height=100, show_particles=True)
    defender = Swarm((0, 0, 255), 2, (255, 100, 100), width=100, height=100)
    attacker.ants = [[10, 10]]
    defender.ants = [[11, 10]]
    attacker.kill_probability = 0.0
    attacker.onCollision(defender)
    assert len(attacker.particle_shot._particles) == 1
    px, py = attacker.particle_shot._particles[0]['pos']
    expected_x = 10 + PARTICLE_DISTANCE
    expected_y = 10
    assert px == pytest.approx(expected_x)
    assert py == pytest.approx(expected_y)

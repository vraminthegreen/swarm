import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

pygame = pytest.importorskip('pygame')

from particle_arrow import ParticleArrow
from swarm import Swarm, ARCHER_ATTACK_RANGE

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_particlearrow_moves_and_expires():
    pa = ParticleArrow()
    pa.addParticle((0, 0), (20, 0))
    assert len(pa._particles) == 1
    pa.tick(1)
    # particle should have moved roughly start speed (10 units)
    x, y = pa._particles[0]['pos']
    assert x == pytest.approx(10)
    assert y == pytest.approx(0)
    # advance enough ticks to reach end and be removed
    for _ in range(5):
        pa.tick(1)
    assert len(pa._particles) == 0


def test_arrow_particle_added_on_attack():
    attacker = Swarm(
        (255, 0, 0),
        1,
        (255, 100, 100),
        width=100,
        height=100,
        attack_range=ARCHER_ATTACK_RANGE,
        arrow_particles=True,
    )
    defender = Swarm(
        (0, 0, 255),
        2,
        (255, 100, 100),
        width=100,
        height=100,
    )
    attacker.ants = [[10, 10]]
    defender.ants = [[20, 10]]
    attacker.kill_probability = 0.0
    attacker.onCollision(defender)
    assert len(attacker.particle_arrow._particles) == 1
    p = attacker.particle_arrow._particles[0]
    assert p["start"] == pytest.approx((15, 10))
    assert p["end"] == pytest.approx((20, 10))


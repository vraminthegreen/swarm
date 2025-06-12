import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from particle_shot import ParticleShot


def test_particle_removed_after_cycles():
    ps = ParticleShot(cycles=2, visible_frames=1, hidden_frames=1)
    ps.addParticle((10, 10))
    assert len(ps._particles) == 1

    # first cycle (show then hide)
    ps.tick(1)
    ps.tick(1)
    # second cycle
    ps.tick(1)
    ps.tick(1)
    assert len(ps._particles) == 0

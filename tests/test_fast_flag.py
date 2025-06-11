import os
import sys
import random
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame

from swarm import Swarm
from flag import FastFlag, NormalFlag
from game_field import GameField

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')


class CombatField(GameField):
    NUM_FOOTMEN = 0
    NUM_ARCHERS = 0
    NUM_ANTS_BLUE = 0
    NUM_ARCHERS_BLUE = 0


def create_swarm():
    swarm = Swarm((255, 0, 0), 1, (255, 100, 100), width=100, height=100)
    swarm.ants.append([10.0, 10.0])
    swarm.show()
    return swarm


def create_combat_field():
    field = CombatField(width=100, height=100)
    field.swarm_footmen.ants = [[50, 50]]
    field.ai_player.swarm_footmen.ants = [[52, 50]]
    field.show()
    return field


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_fast_flag_speeds_units():
    random.seed(0)
    normal = create_swarm()
    normal.queue.add_flag_at((90, 10), NormalFlag)
    normal._tick(1.0)
    dist_normal = normal.ants[0][0] - 10.0

    random.seed(0)
    fast = create_swarm()
    fast.queue.add_flag_at((90, 10), FastFlag)
    fast._tick(1.0)
    dist_fast = fast.ants[0][0] - 10.0

    assert dist_fast == pytest.approx(dist_normal * 1.5, rel=1e-6)


def test_fast_flag_disables_attack():
    field = create_combat_field()
    field.swarm_footmen.queue.add_flag_at((60, 50), FastFlag)
    initial = len(field.ai_player.swarm_footmen.ants)
    field._handle_combat(field.swarm_footmen, field.ai_player.swarm_footmen, 1.0)
    assert len(field.ai_player.swarm_footmen.ants) == initial

    field.swarm_footmen.queue.clear()
    field.swarm_footmen.queue.add_flag_at((60, 50), NormalFlag)
    field.ai_player.swarm_footmen.ants = [[52, 50]]
    field._handle_combat(field.swarm_footmen, field.ai_player.swarm_footmen, 1.0)
    assert len(field.ai_player.swarm_footmen.ants) == 0

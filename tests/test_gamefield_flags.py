import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

pygame = pytest.importorskip('pygame')

from game_field import GameField
from flag import NormalFlag, FastFlag

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

class MinimalGameField(GameField):
    NUM_FOOTMEN = 0
    NUM_ARCHERS = 0
    NUM_ANTS_BLUE = 0
    NUM_ARCHERS_BLUE = 0


def create_field():
    field = MinimalGameField(width=100, height=100)
    field.show()
    return field


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_click_adds_flag():
    field = create_field()
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=1)
    field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 1
    assert isinstance(queue[0], NormalFlag)


def test_shift_click_adds_fast_flag():
    field = create_field()
    pygame.key.set_mods(pygame.KMOD_SHIFT)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(20, 20), button=1)
    field.handleEvent(event)
    pygame.key.set_mods(0)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 1
    assert isinstance(queue[0], FastFlag)


def test_three_clicks_add_three_flags():
    field = create_field()
    positions = [(5, 5), (15, 15), (25, 25)]
    for pos in positions:
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
        field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 3


def test_clicking_existing_flag_removes_it():
    field = create_field()
    a, b, c = (5, 5), (15, 15), (25, 25)
    for pos in (a, b, c):
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
        field.handleEvent(event)
    # Click on the second flag again to remove it
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=b, button=1)
    field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    positions = [flag.pos for flag in queue]
    assert positions == [a, c]

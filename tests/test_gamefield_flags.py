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


def test_shift_click_appends_flag():
    field = create_field()
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(10, 10), button=1)
    field.handleEvent(event)
    pygame.key.set_mods(pygame.KMOD_SHIFT)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(20, 20), button=1)
    field.handleEvent(event)
    pygame.key.set_mods(0)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 2
    assert isinstance(queue[0], NormalFlag)
    assert isinstance(queue[1], NormalFlag)


def test_three_clicks_replace_queue():
    field = create_field()
    positions = [(5, 5), (15, 15), (25, 25)]
    for pos in positions:
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
        field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 1
    assert queue[0].pos == positions[-1]


def test_clicking_existing_flag_removes_it():
    field = create_field()
    pos = (10, 10)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
    field.handleEvent(event)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
    field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 0


def test_m_key_sets_fast_flag():
    field = create_field()
    pygame.mouse.set_pos((40, 40))
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)
    field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 1
    assert isinstance(queue[0], FastFlag)


def test_shift_m_appends_fast_flag():
    field = create_field()
    pygame.mouse.set_pos((10, 10))
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)
    field.handleEvent(event)
    pygame.mouse.set_pos((20, 20))
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m, mod=pygame.KMOD_SHIFT)
    field.handleEvent(event)
    queue = field.flag_queues[field.active_group]
    assert len(queue) == 2
    assert isinstance(queue[0], FastFlag)
    assert isinstance(queue[1], FastFlag)

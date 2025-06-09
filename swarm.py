import math
import random
import pygame

from stage import Stage
from order_queue import OrderQueue

DOT_SIZE = 4
BACKGROUND_COLOR = (0, 0, 0)


def lighten(color, factor=0.5):
    """Return a lighter variant of the given RGB color."""
    r, g, b = color
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return r, g, b


def compute_centroid(ants):
    """Return the centroid of ``ants`` or ``None`` if empty."""
    if not ants:
        return None
    x = sum(a[0] for a in ants) / len(ants)
    y = sum(a[1] for a in ants) / len(ants)
    return int(x), int(y)


def draw_ants(screen, ants, color, engaged=None, engaged_color=None, shape="circle"):
    """Draw ants on ``screen`` with optional highlighting for engaged ones."""
    for i, (x, y) in enumerate(ants):
        c = color
        if engaged and i in engaged:
            c = engaged_color if engaged_color else color
        center = (int(x), int(y))
        if shape == "semicircle":
            radius = DOT_SIZE // 2
            pygame.draw.circle(screen, c, center, radius)
            pygame.draw.rect(
                screen,
                BACKGROUND_COLOR,
                (center[0] - radius, center[1] - radius, radius, radius * 2),
            )
            pygame.draw.line(
                screen,
                c,
                (center[0] - radius, center[1] - radius),
                (center[0] - radius, center[1] + radius),
            )
        else:
            pygame.draw.circle(screen, c, center, DOT_SIZE // 2)


def draw_group_banner(screen, ants, color, number, active=False):
    """Draw control group banner with ``number`` at the ants' center of mass."""
    center = compute_centroid(ants)
    if center is None:
        return
    rect_width, rect_height = 14, 10
    rect = pygame.Rect(
        center[0] - rect_width // 2, center[1] - rect_height // 2, rect_width, rect_height
    )
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 1)
    if active:
        pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4), 1)
    font = pygame.font.Font(None, 16)
    text = font.render(str(number), True, (255, 255, 255))
    text_rect = text.get_rect(center=center)
    screen.blit(text, text_rect)


def draw_dashed_line(screen, start_pos, end_pos, color=(200, 200, 200), dash_length=5):
    """Draw a dashed line between ``start_pos`` and ``end_pos``."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    vx = dx / length
    vy = dy / length
    num_dashes = int(length // dash_length)
    for i in range(0, num_dashes, 2):
        start = (x1 + vx * i * dash_length, y1 + vy * i * dash_length)
        end = (
            x1 + vx * min((i + 1) * dash_length, length),
            y1 + vy * min((i + 1) * dash_length, length),
        )
        pygame.draw.line(screen, color, start, end)


def draw_flag_path(screen, start_pos, flags):
    """Draw a dashed path starting at ``start_pos`` through ``flags``."""
    current = start_pos
    for flag in flags:
        if flag.pos is None:
            continue
        draw_dashed_line(screen, current, flag.pos)
        current = flag.pos


class Swarm(Stage):
    """Group of units of one type belonging to a single player."""

    def __init__(self, color, group_id, flag_color, shape="circle"):
        super().__init__()
        self.ants = []
        self.color = color
        self.engaged_color = lighten(color)
        self.shape = shape
        self.group_id = group_id
        self.flag_color = flag_color
        self.active = False
        self.engaged = set()

        self.queue = OrderQueue()
        self.add_stage(self.queue)

    def compute_centroid(self):
        return compute_centroid(self.ants)

    def first_flag(self):
        return self.queue[0] if self.queue else None

    def spawn(self, count, x_range, y_range, occupied, width=640, height=480, min_distance=4):
        """Populate the swarm with ``count`` units randomly inside the area."""
        while len(self.ants) < count:
            x = random.uniform(*x_range)
            y = random.uniform(*y_range)
            if 0 <= x < width and 0 <= y < height:
                if all((x - ox) ** 2 + (y - oy) ** 2 >= min_distance ** 2 for ox, oy in occupied):
                    self.ants.append([x, y])
                    occupied.add((x, y))

    def _draw(self, screen):
        draw_ants(screen, self.ants, self.color, self.engaged, self.engaged_color, self.shape)
        draw_group_banner(screen, self.ants, self.color, self.group_id, self.active)
        if self.queue:
            start_center = self.compute_centroid()
            if start_center:
                draw_flag_path(screen, start_center, self.queue)
        for idx, flag in enumerate(self.queue, start=1):
            flag.number = idx
            flag.color = self.flag_color


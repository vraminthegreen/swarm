import math
import random
import pygame

from stage import Stage
from order_queue import OrderQueue
from flag import FastFlag
from collision_shape import CollisionShape

DOT_SIZE = 4
BACKGROUND_COLOR = (0, 0, 0)

# Combat configuration
ATTACK_RANGE = 12
KILL_PROBABILITY = 0.02
ARCHER_ATTACK_RANGE = 60
ARCHER_KILL_PROBABILITY = KILL_PROBABILITY / 3


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


def render_text_with_outline(font, text, text_color, outline_color):
    """Return a surface with ``text`` drawn in ``text_color`` with ``outline_color``."""
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    image = pygame.Surface((base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                image.blit(outline, (dx + 1, dy + 1))
    image.blit(base, (1, 1))
    return image


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

    # Display the size of the swarm just below the banner
    # Increase the font size for the swarm count by 20%
    count_font = pygame.font.Font(None, 17)
    count_surface = render_text_with_outline(
        count_font, str(len(ants)), (255, 255, 0), (0, 0, 0)
    )
    count_rect = count_surface.get_rect(midtop=(center[0], rect.bottom + 2))
    screen.blit(count_surface, count_rect)


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


def draw_dotted_circle(screen, center, radius, color=(255, 165, 0), segments=60):
    """Draw a dotted circle using ``segments`` line pieces."""
    if radius <= 0:
        return
    points = [
        (
            center[0] + radius * math.cos(2 * math.pi * i / segments),
            center[1] + radius * math.sin(2 * math.pi * i / segments),
        )
        for i in range(segments + 1)
    ]
    for i in range(segments):
        if i % 2 == 0:
            pygame.draw.line(screen, color, points[i], points[i + 1])


class Swarm(Stage):
    """Group of units of one type belonging to a single player."""

    def __init__(
        self,
        color,
        group_id,
        flag_color,
        shape="circle",
        width=640,
        height=480,
        min_distance=4,
        attack_range=ATTACK_RANGE,
    ):
        super().__init__()
        self.ants = []
        self.color = color
        self.engaged_color = lighten(color)
        self.shape = shape
        self.group_id = group_id
        self.flag_color = flag_color
        self.active = False
        self.engaged = set()
        self.colliding_swarms = []

        # Cached centroid value for performance
        self._centroid_cache = None

        self.width = width
        self.height = height
        self.min_distance = min_distance
        self.attack_range = attack_range

        self.queue = OrderQueue()
        self.add_stage(self.queue)

    def compute_centroid(self):
        """Return the cached centroid of the swarm's units."""
        if self._centroid_cache is None:
            self._centroid_cache = compute_centroid(self.ants)
        return self._centroid_cache

    def _invalidate_centroid_cache(self):
        """Clear the cached centroid."""
        self._centroid_cache = None

    def getPosition(self):
        """Return the centroid position of this swarm."""
        return self.compute_centroid()

    def getCollisionShape(self):
        """Return a circular collision shape encompassing the swarm."""
        center = self.compute_centroid()
        if center is None:
            return None
        radius = 0.0
        cx, cy = center
        for x, y in self.ants:
            dist = math.hypot(x - cx, y - cy)
            if dist > radius:
                radius = dist

        # Expand the collision radius by the swarm's attack range so that
        # swarms register a collision when they are close enough to fight.
        radius += self.attack_range

        return CollisionShape(center, radius)

    def onCollision(self, stage):
        """Record collisions with other swarms."""
        if isinstance(stage, Swarm) and stage is not self:
            self.colliding_swarms.append(stage)

    def first_flag(self):
        return self.queue[0] if self.queue else None

    def is_fast_moving(self):
        """Return True if the active flag is a FastFlag."""
        flag = self.first_flag()
        return isinstance(flag, FastFlag)

    def spawn(self, count, x_range, y_range, occupied, width=None, height=None, min_distance=None):
        """Populate the swarm with ``count`` units randomly inside the area."""
        width = self.width if width is None else width
        height = self.height if height is None else height
        min_distance = self.min_distance if min_distance is None else min_distance
        while len(self.ants) < count:
            x = random.uniform(*x_range)
            y = random.uniform(*y_range)
            if 0 <= x < width and 0 <= y < height:
                if all((x - ox) ** 2 + (y - oy) ** 2 >= min_distance ** 2 for ox, oy in occupied):
                    self.ants.append([x, y])
                    self._invalidate_centroid_cache()
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
        shape = self.getCollisionShape()
        if shape is not None:
            draw_dotted_circle(screen, shape.center, shape.radius)
        center = self.compute_centroid()
        if center:
            for other in self.colliding_swarms:
                other_center = other.compute_centroid()
                if other_center:
                    pygame.draw.line(screen, (255, 0, 0), center, other_center, width=3)
        self.colliding_swarms.clear()

    # ------------------------------------------------------------------
    # Movement helpers
    # ------------------------------------------------------------------
    def _is_valid_position(self, x, y, others):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        for ox, oy in others:
            if (x - ox) ** 2 + (y - oy) ** 2 < self.min_distance ** 2:
                return False
        return True

    def _compute_move_vector(self, x, y, flag_pos, others):
        ex = ey = 0.0
        for ox, oy in others:
            dx = x - ox
            dy = y - oy
            d2 = dx * dx + dy * dy
            if d2 == 0:
                continue
            if d2 < self.min_distance ** 2:
                dist = math.sqrt(d2)
                ex += dx / dist
                ey += dy / dist

        fx = flag_pos[0] - x
        fy = flag_pos[1] - y
        flen = math.hypot(fx, fy)
        if flen != 0:
            fx /= flen
            fy /= flen
        else:
            fx = fy = 0.0

        angle = random.uniform(0, 2 * math.pi)
        mag = random.uniform(0.5, 3.0) if random.random() < 0.1 else random.uniform(0.1, 0.6)
        rx = math.cos(angle) * mag
        ry = math.sin(angle) * mag

        vx = ex + fx + rx
        vy = ey + fy + ry
        vlen = math.hypot(vx, vy)
        if vlen == 0:
            return 0.0, 0.0
        return vx / vlen, vy / vlen

    def _nearest_flag(self, x, y, flags):
        best_flag = None
        best_d2 = float("inf")
        for flag in flags:
            pos = flag.pos
            if pos is None:
                continue
            d2 = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best_flag = flag
        return best_flag

    def _propose_moves(self, ants, flags, all_ants, tick):
        proposed = []
        for i, (x, y) in enumerate(ants):
            flag = self._nearest_flag(x, y, flags)
            if flag is None:
                proposed.append((x, y))
                continue
            target_pos = flag.pos
            vx, vy = self._compute_move_vector(x, y, target_pos, all_ants)
            nx = max(0, min(self.width - 1, x + vx * tick))
            ny = max(0, min(self.height - 1, y + vy * tick))
            proposed.append((nx, ny))
        return proposed

    def _resolve_positions(self, ants, proposed):
        new_ants = []
        occupied_new = []
        for i, (nx, ny) in enumerate(proposed):
            if self._is_valid_position(nx, ny, occupied_new):
                new_ants.append((nx, ny))
                occupied_new.append((nx, ny))
            else:
                new_ants.append(tuple(ants[i]))
                occupied_new.append(tuple(ants[i]))
        return new_ants

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def _tick(self, dt):
        flag = self.first_flag()
        flags = [flag] if flag else []
        all_ants = self.ants
        speed = dt * 1.5 if isinstance(flag, FastFlag) else dt
        proposed = self._propose_moves(self.ants, flags, all_ants, speed)
        self.ants = [list(p) for p in self._resolve_positions(self.ants, proposed)]
        self._invalidate_centroid_cache()

        center = self.compute_centroid()
        if flag and flag.pos is not None and center is not None:
            if math.hypot(center[0] - flag.pos[0], center[1] - flag.pos[1]) < 40:
                if len(self.queue) > 1:
                    self.queue.pop(0)


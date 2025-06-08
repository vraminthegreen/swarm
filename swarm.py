#!/usr/bin/env python3

import pygame
import sys
import random
import math
import time

WIDTH, HEIGHT = 640, 480
# Number of classic red ants and the new circle-type ants
NUM_ANTS_RED_CLASSIC = 150
NUM_ANTS_RED_CIRCLE = 50
NUM_ANTS_BLUE = 200

ANT_COLOR_RED = (255, 0, 0)
ANT_COLOR_BLUE = (0, 255, 255)  # cyan

def lighten(color, factor=0.5):
    """Return a lighter variant of the given RGB color."""
    r, g, b = color
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return r, g, b

ANT_COLOR_RED_ENGAGED = lighten(ANT_COLOR_RED)
ANT_COLOR_BLUE_ENGAGED = lighten(ANT_COLOR_BLUE)
# Color for the new circle-type ants
# Color for the new archer-type ants (using red for now)
ANT_COLOR_CIRCLE = (255, 0, 0)
ANT_COLOR_CIRCLE_ENGAGED = lighten(ANT_COLOR_CIRCLE)

# Flag types
FLAG_TYPE_NORMAL = "normal"
FLAG_TYPE_FAST = "fast"
FLAG_TYPE_STOP = "stop"

BACKGROUND_COLOR = (0, 0, 0)
FLAG_COLOR_RED = (255, 100, 100)  # light red
FLAG_COLOR_BLUE = (0, 255, 255)  # cyan flag
FLAG_POLE_COLOR = (200, 200, 200)
FLAG_SIZE = 12
DOT_SIZE = 4
MIN_DISTANCE = 4  # minimum distance between ants in pixels
ATTACK_RANGE = 12  # distance within which ants will attack instead of moving
KILL_PROBABILITY = 0.02  # chance that an attack kills the target

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
flag_font = pygame.font.Font(None, 16)

# Initialize ants for both players at random positions
ants_red = []  # classic red ants
ants_circle = []  # new semi-circle "archer" ants
ants_blue = []
occupied = set()
def is_valid_position(x, y, others):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return False
    for ox, oy in others:
        if (x - ox) ** 2 + (y - oy) ** 2 < MIN_DISTANCE ** 2:
            return False
    return True

def compute_move_vector(x, y, flag_pos, others):
    """Return a normalized vector combining repulsion, attraction and randomness."""
    ex = ey = 0.0
    for ox, oy in others:
        dx = x - ox
        dy = y - oy
        d2 = dx * dx + dy * dy
        if d2 == 0:
            continue
        if d2 < MIN_DISTANCE ** 2:
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
    if random.random() < 0.1:
        mag = random.uniform(0.5, 3.0)
    else:
        mag = random.uniform(0.1, 0.6)
    rx = math.cos(angle) * mag
    ry = math.sin(angle) * mag

    vx = ex + fx + rx
    vy = ey + fy + ry
    vlen = math.hypot(vx, vy)
    if vlen == 0:
        return 0.0, 0.0
    return vx / vlen, vy / vlen


def find_nearest_enemy(x, y, enemies):
    """Return the index of the nearest enemy within ATTACK_RANGE or None."""
    best_idx = None
    best_d2 = ATTACK_RANGE * ATTACK_RANGE + 1
    for i, (ex, ey) in enumerate(enemies):
        d2 = (ex - x) ** 2 + (ey - y) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best_idx = i
    if best_d2 <= ATTACK_RANGE * ATTACK_RANGE:
        return best_idx
    return None


def handle_attacks(ants, enemies, flags):
    """Return sets of attackers and killed enemy indices considering flag types."""
    attackers = set()
    killed = set()
    for i, (x, y) in enumerate(ants):
        flag = nearest_flag(x, y, flags)
        if flag and flag["type"] == FLAG_TYPE_FAST:
            continue  # cannot attack when heading to a fast flag
        target = find_nearest_enemy(x, y, enemies)
        if target is not None:
            attackers.add(i)
            if random.random() < KILL_PROBABILITY:
                killed.add(target)
    return attackers, killed


def nearest_flag(x, y, flags):
    """Return the closest defined flag to (x, y)."""
    best_flag = None
    best_d2 = float("inf")
    for flag in flags:
        pos = flag["pos"]
        if pos is None:
            continue
        d2 = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best_flag = flag
    return best_flag


def propose_moves(ants, attackers, flags, all_ants):
    """Return proposed new positions for ants based on nearest flag."""
    proposed = []
    for i, (x, y) in enumerate(ants):
        flag = nearest_flag(x, y, flags)
        if flag is None:
            proposed.append((x, y))
            continue

        speed_mult = 1.5 if flag["type"] == FLAG_TYPE_FAST else 1.0
        speed = (0.3 if i in attackers else 1.0) * speed_mult

        target_pos = (x, y) if flag["type"] == FLAG_TYPE_STOP else flag["pos"]
        vx, vy = compute_move_vector(x, y, target_pos, all_ants)
        nx = max(0, min(WIDTH - 1, x + vx * speed))
        ny = max(0, min(HEIGHT - 1, y + vy * speed))
        proposed.append((nx, ny))
    return proposed


def resolve_positions(ants, proposed, killed, occupied_new):
    """Update ant positions based on proposals and deaths."""
    new_ants = []
    for i, (nx, ny) in enumerate(proposed):
        if i in killed:
            continue
        if is_valid_position(nx, ny, occupied_new):
            new_ants.append((nx, ny))
            occupied_new.append((nx, ny))
        else:
            new_ants.append(tuple(ants[i]))
            occupied_new.append(tuple(ants[i]))
    return new_ants


def draw_ants(ants, color, engaged=None, engaged_color=None, shape="circle"):
    """Draw ants with optional shape, highlighting engaged ones with a lighter color."""
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


def draw_flag(flag_pos, color, number=None, flag_type=FLAG_TYPE_NORMAL):
    """Draw a flag if its position is defined, optionally with a number."""
    if flag_pos is None:
        return
    fx, fy = flag_pos
    pole_top = (fx, max(0, fy - 10))
    pygame.draw.line(screen, FLAG_POLE_COLOR, flag_pos, pole_top)

    if flag_type == FLAG_TYPE_FAST:
        left1 = pole_top
        right1 = (pole_top[0] + FLAG_SIZE // 2, pole_top[1] + FLAG_SIZE // 2)
        bottom1 = (pole_top[0], pole_top[1] + FLAG_SIZE)
        left2 = (pole_top[0] + FLAG_SIZE // 2, pole_top[1])
        right2 = (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2)
        bottom2 = (pole_top[0] + FLAG_SIZE // 2, pole_top[1] + FLAG_SIZE)
        pygame.draw.polygon(screen, color, [left1, right1, bottom1])
        pygame.draw.polygon(screen, color, [left2, right2, bottom2])
    elif flag_type == FLAG_TYPE_STOP:
        bar_height = 3
        gap = 2
        rect1 = pygame.Rect(pole_top[0], pole_top[1], FLAG_SIZE, bar_height)
        rect2 = pygame.Rect(
            pole_top[0], pole_top[1] + bar_height + gap, FLAG_SIZE, bar_height
        )
        pygame.draw.rect(screen, color, rect1)
        pygame.draw.rect(screen, color, rect2)
    else:
        flag_points = [
            pole_top,
            (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
            (pole_top[0], pole_top[1] + FLAG_SIZE),
        ]
        pygame.draw.polygon(screen, color, flag_points)
    if number is not None:
        text = flag_font.render(str(number), True, (255, 255, 255))
        text_rect = text.get_rect(midleft=(pole_top[0] + FLAG_SIZE + 2, pole_top[1] + FLAG_SIZE // 2))
        screen.blit(text, text_rect)


def draw_flag_icon(idx, flag_type=FLAG_TYPE_NORMAL, active=False):
    """Draw numbered flag icons at the bottom and highlight the active one."""
    spacing = FLAG_SIZE * 2 + 20
    base_x = 20 + idx * spacing
    base_y = HEIGHT - 5
    draw_flag((base_x, base_y), FLAG_COLOR_RED, idx + 1, flag_type)
    if active:
        rect = pygame.Rect(base_x - 4, base_y - 16, FLAG_SIZE + 12, FLAG_SIZE + 20)
        pygame.draw.rect(screen, (255, 255, 0), rect, 1)


# Place classic red ants in the lower-left corner (25% of the screen)
while len(ants_red) < NUM_ANTS_RED_CLASSIC:
    x = random.uniform(0, WIDTH * 0.25)
    y = random.uniform(HEIGHT * 0.75, HEIGHT)
    if is_valid_position(x, y, occupied):
        ants_red.append([x, y])
        occupied.add((x, y))

# Place archer ants in the same area
while len(ants_circle) < NUM_ANTS_RED_CIRCLE:
    x = random.uniform(0, WIDTH * 0.25)
    y = random.uniform(HEIGHT * 0.75, HEIGHT)
    if is_valid_position(x, y, occupied):
        ants_circle.append([x, y])
        occupied.add((x, y))

# Place blue ants in the upper-right corner (25% of the screen)
while len(ants_blue) < NUM_ANTS_BLUE:
    x = random.uniform(WIDTH * 0.75, WIDTH)
    y = random.uniform(0, HEIGHT * 0.25)
    if is_valid_position(x, y, occupied):
        ants_blue.append([x, y])
        occupied.add((x, y))

flags_red = [
    {"pos": None, "type": FLAG_TYPE_NORMAL},
    {"pos": None, "type": FLAG_TYPE_NORMAL},
    {"pos": None, "type": FLAG_TYPE_FAST},
    {"pos": None, "type": FLAG_TYPE_STOP},
]
active_flag_idx = 0
flag_pos_blue = (random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
next_flag_move = time.time() + random.uniform(5, 30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                active_flag_idx = 0
            elif event.key == pygame.K_2:
                active_flag_idx = 1
            elif event.key == pygame.K_3:
                active_flag_idx = 2
            elif event.key == pygame.K_4:
                active_flag_idx = 3
            elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                flags_red[active_flag_idx]["pos"] = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            flags_red[active_flag_idx]["pos"] = event.pos

    # move the computer-controlled flag occasionally
    now = time.time()
    if now >= next_flag_move:
        flag_pos_blue = (random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        next_flag_move = now + random.uniform(5, 30)

    all_ants = ants_red + ants_circle + ants_blue

    attackers_red, killed_blue_from_red = handle_attacks(
        ants_red, ants_blue, flags_red
    )
    attackers_circle, killed_blue_from_circle = handle_attacks(
        ants_circle, ants_blue, flags_red
    )
    attackers_blue, killed_red_all = handle_attacks(
        ants_blue,
        ants_red + ants_circle,
        [{"pos": flag_pos_blue, "type": FLAG_TYPE_NORMAL}],
    )
    killed_blue = killed_blue_from_red.union(killed_blue_from_circle)
    killed_red = {i for i in killed_red_all if i < len(ants_red)}
    killed_circle = {i - len(ants_red) for i in killed_red_all if i >= len(ants_red)}

    proposed_red = propose_moves(ants_red, attackers_red, flags_red, all_ants)
    proposed_circle = propose_moves(
        ants_circle, attackers_circle, flags_red, all_ants
    )
    proposed_blue = propose_moves(
        ants_blue,
        attackers_blue,
        [{"pos": flag_pos_blue, "type": FLAG_TYPE_NORMAL}],
        all_ants,
    )

    new_ants_red = []
    new_ants_circle = []
    new_ants_blue = []
    occupied_new = []

    new_ants_red = resolve_positions(ants_red, proposed_red, killed_red, occupied_new)
    new_ants_circle = resolve_positions(
        ants_circle, proposed_circle, killed_circle, occupied_new
    )
    new_ants_blue = resolve_positions(ants_blue, proposed_blue, killed_blue, occupied_new)

    ants_red = [list(p) for p in new_ants_red]
    ants_circle = [list(p) for p in new_ants_circle]
    ants_blue = [list(p) for p in new_ants_blue]

    screen.fill(BACKGROUND_COLOR)
    draw_ants(ants_red, ANT_COLOR_RED, attackers_red, ANT_COLOR_RED_ENGAGED)
    draw_ants(
        ants_circle,
        ANT_COLOR_CIRCLE,
        attackers_circle,
        ANT_COLOR_CIRCLE_ENGAGED,
        shape="semicircle",
    )
    draw_ants(ants_blue, ANT_COLOR_BLUE, attackers_blue, ANT_COLOR_BLUE_ENGAGED)

    for idx, flag in enumerate(flags_red, start=1):
        draw_flag(flag["pos"], FLAG_COLOR_RED, idx, flag["type"])
    draw_flag(flag_pos_blue, FLAG_COLOR_BLUE)

    for idx, flag in enumerate(flags_red):
        draw_flag_icon(idx, flag["type"], idx == active_flag_idx)

    # Display remaining ant counts in the top-right corner
    count_text = font.render(
        f"Classic: {len(ants_red)}  Archers: {len(ants_circle)}  Blue: {len(ants_blue)}",
        True,
        (255, 255, 255),
    )
    text_rect = count_text.get_rect(topright=(WIDTH - 5, 5))
    screen.blit(count_text, text_rect)

    engaged_text = font.render(
        (
            f"Engaged - Classic: {len(attackers_red)}  "
            f"Archers: {len(attackers_circle)}  Blue: {len(attackers_blue)}"
        ),
        True,
        (255, 255, 255),
    )
    engaged_rect = engaged_text.get_rect(topright=(WIDTH - 5, 25))
    screen.blit(engaged_text, engaged_rect)

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
sys.exit()

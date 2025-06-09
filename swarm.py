#!/usr/bin/env python3

import pygame
import sys
import random
import math
import time

WIDTH, HEIGHT = 640, 480
# Unit counts for each team
NUM_FOOTMEN = 150
NUM_ARCHERS = 50
NUM_ARCHERS_BLUE = 50
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
# Color for the archer ants
ANT_COLOR_ARCHER = (255, 0, 0)
ANT_COLOR_ARCHER_ENGAGED = lighten(ANT_COLOR_ARCHER)
ANT_COLOR_ARCHER_BLUE = (0, 255, 255)
ANT_COLOR_ARCHER_BLUE_ENGAGED = lighten(ANT_COLOR_ARCHER_BLUE)

# Flag types
FLAG_TYPE_NORMAL = "normal"
FLAG_TYPE_FAST = "fast"
FLAG_TYPE_STOP = "stop"
FLAG_TYPE_ARCHER = "archer"

# Control groups for player units
GROUP_FOOTMEN = 1
GROUP_ARCHERS = 2

BACKGROUND_COLOR = (0, 0, 0)
FLAG_COLOR_RED = (255, 100, 100)  # light red
FLAG_COLOR_BLUE = (0, 255, 255)  # cyan flag
FLAG_POLE_COLOR = (200, 200, 200)
FLAG_SIZE = 12
DOT_SIZE = 4
MIN_DISTANCE = 4  # minimum distance between ants in pixels
ATTACK_RANGE = 12  # distance within which footmen attack instead of moving
KILL_PROBABILITY = 0.02  # chance that a footman attack kills the target

# Archers behave differently: they can shoot from much farther away but are
# less lethal.  ARCHER_ATTACK_RANGE defines how far an archer can shoot and
# ARCHER_KILL_PROBABILITY controls the probability of killing the target.
ARCHER_ATTACK_RANGE = 60
ARCHER_KILL_PROBABILITY = KILL_PROBABILITY / 3

# Distance threshold to consider a flag reached
FLAG_REACHED_DISTANCE = 40

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)
flag_font = pygame.font.Font(None, 16)

# Templates for creating new flags via the command queue
flag_templates = [
    {"type": FLAG_TYPE_NORMAL},
    {"type": FLAG_TYPE_NORMAL},
    {"type": FLAG_TYPE_FAST},
    {"type": FLAG_TYPE_STOP},
]

# Queue of player-issued flags for each control group
flag_queues = {
    GROUP_FOOTMEN: [],
    GROUP_ARCHERS: [],
}

# Currently selected control group
active_group = GROUP_FOOTMEN

# Initialize ants for both players at random positions
ants_footmen = []  # footmen units
ants_archers = []  # red archers displayed as semi-circles
ants_blue = []  # blue footmen units
ants_blue_archers = []  # blue archers displayed as semi-circles
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


def find_nearest_enemy(x, y, enemies, attack_range):
    """Return the index of the nearest enemy within ``attack_range`` or None."""
    best_idx = None
    best_d2 = attack_range * attack_range + 1
    for i, (ex, ey) in enumerate(enemies):
        d2 = (ex - x) ** 2 + (ey - y) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best_idx = i
    if best_d2 <= attack_range * attack_range:
        return best_idx
    return None


def handle_attacks(ants, enemies, flags, attack_range=ATTACK_RANGE, kill_probability=KILL_PROBABILITY):
    """Return sets of attackers and killed enemy indices considering flag types."""
    attackers = set()
    killed = set()
    for i, (x, y) in enumerate(ants):
        flag = nearest_flag(x, y, flags)
        if flag and flag["type"] == FLAG_TYPE_FAST:
            continue  # cannot attack when heading to a fast flag
        target = find_nearest_enemy(x, y, enemies, attack_range)
        if target is not None:
            attackers.add(i)
            if random.random() < kill_probability:
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


def compute_centroid(ants):
    """Return the centroid of the given ants or None if empty."""
    if not ants:
        return None
    x = sum(a[0] for a in ants) / len(ants)
    y = sum(a[1] for a in ants) / len(ants)
    return int(x), int(y)


def first_flag(queue):
    """Return the first flag in ``queue`` or ``None`` if empty."""
    return queue[0] if queue else None


def draw_group_banner(ants, color, number, active=False):
    """Draw a small banner with the control group number at the group's center."""
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
    text = flag_font.render(str(number), True, (255, 255, 255))
    text_rect = text.get_rect(center=center)
    screen.blit(text, text_rect)

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
    elif flag_type == FLAG_TYPE_ARCHER:
        flag_points = [
            pole_top,
            (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
            (pole_top[0], pole_top[1] + FLAG_SIZE),
        ]
        pygame.draw.polygon(screen, color, flag_points)
        center = (pole_top[0] + FLAG_SIZE // 2, pole_top[1] + FLAG_SIZE // 2)
        pygame.draw.line(
            screen,
            FLAG_POLE_COLOR,
            (center[0] - 3, center[1]),
            (center[0] + 3, center[1]),
            1,
        )
        pygame.draw.line(
            screen,
            FLAG_POLE_COLOR,
            (center[0], center[1] - 3),
            (center[0], center[1] + 3),
            1,
        )
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


def draw_dashed_line(start_pos, end_pos, color=(200, 200, 200), dash_length=5):
    """Draw a dashed line between two points."""
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
        end = (x1 + vx * min((i + 1) * dash_length, length), y1 + vy * min((i + 1) * dash_length, length))
        pygame.draw.line(screen, color, start, end)


def draw_flag_path(start_pos, flags):
    """Draw dashed path from ``start_pos`` through the list of flags."""
    current = start_pos
    for flag in flags:
        if flag["pos"] is None:
            continue
        draw_dashed_line(current, flag["pos"])
        current = flag["pos"]


# Place footmen in the lower-left corner (25% of the screen)
while len(ants_footmen) < NUM_FOOTMEN:
    x = random.uniform(0, WIDTH * 0.25)
    y = random.uniform(HEIGHT * 0.75, HEIGHT)
    if is_valid_position(x, y, occupied):
        ants_footmen.append([x, y])
        occupied.add((x, y))

# Place red archers in the upper-left corner
while len(ants_archers) < NUM_ARCHERS:
    x = random.uniform(0, WIDTH * 0.25)
    y = random.uniform(0, HEIGHT * 0.25)
    if is_valid_position(x, y, occupied):
        ants_archers.append([x, y])
        occupied.add((x, y))

# Place blue footmen in the upper-right corner (25% of the screen)
while len(ants_blue) < NUM_ANTS_BLUE:
    x = random.uniform(WIDTH * 0.75, WIDTH)
    y = random.uniform(0, HEIGHT * 0.25)
    if is_valid_position(x, y, occupied):
        ants_blue.append([x, y])
        occupied.add((x, y))

# Place blue archers in the lower-right corner
while len(ants_blue_archers) < NUM_ARCHERS_BLUE:
    x = random.uniform(WIDTH * 0.75, WIDTH)
    y = random.uniform(HEIGHT * 0.75, HEIGHT)
    if is_valid_position(x, y, occupied):
        ants_blue_archers.append([x, y])
        occupied.add((x, y))

active_flag_idx = 0

# Blue team alternates between footman and archer flags
flags_blue = [
    {"pos": (random.uniform(0, WIDTH), random.uniform(0, HEIGHT)), "type": FLAG_TYPE_NORMAL},
    {"pos": None, "type": FLAG_TYPE_ARCHER},
]
next_blue_flag_idx = 1
next_blue_flag_move = time.time() + random.uniform(5, 20)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                active_flag_idx = 0
                active_group = GROUP_FOOTMEN
            elif event.key == pygame.K_2:
                active_flag_idx = 1
                active_group = GROUP_ARCHERS
            elif event.key == pygame.K_3:
                active_flag_idx = 2
            elif event.key == pygame.K_4:
                active_flag_idx = 3
            elif event.key == pygame.K_DELETE:
                if flag_queues[active_group]:
                    flag_queues[active_group].pop()
            elif event.key == pygame.K_BACKSPACE:
                flag_queues[active_group].clear()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            removed = False
            for gid, queue in flag_queues.items():
                for i, flag in enumerate(queue):
                    fx, fy = flag["pos"]
                    if math.hypot(fx - event.pos[0], fy - event.pos[1]) <= FLAG_SIZE:
                        queue.pop(i)
                        removed = True
                        break
                if removed:
                    break
            if not removed:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    flag_type = FLAG_TYPE_FAST
                else:
                    flag_type = flag_templates[active_flag_idx]["type"]
                flag_queues[active_group].append({"pos": event.pos, "type": flag_type})

    # move the computer-controlled flags alternately
    now = time.time()
    if now >= next_blue_flag_move:
        flags_blue[next_blue_flag_idx]["pos"] = (
            random.uniform(0, WIDTH),
            random.uniform(0, HEIGHT),
        )
        next_blue_flag_idx = 1 - next_blue_flag_idx
        next_blue_flag_move = now + random.uniform(5, 20)

    all_ants = ants_footmen + ants_archers + ants_blue + ants_blue_archers

    flag_for_footmen = first_flag(flag_queues[GROUP_FOOTMEN])
    flag_for_archers = first_flag(flag_queues[GROUP_ARCHERS])

    flags_for_footmen = [flag_for_footmen] if flag_for_footmen else []
    flags_for_archers = [flag_for_archers] if flag_for_archers else []

    attackers_footmen, killed_blue_from_footmen = handle_attacks(
        ants_footmen, ants_blue + ants_blue_archers, flags_for_footmen
    )
    attackers_archers, killed_blue_from_archers = handle_attacks(
        ants_archers,
        ants_blue + ants_blue_archers,
        flags_for_archers,
        attack_range=ARCHER_ATTACK_RANGE,
        kill_probability=ARCHER_KILL_PROBABILITY,
    )
    attackers_blue, killed_red_all_from_blue = handle_attacks(
        ants_blue,
        ants_footmen + ants_archers,
        [flags_blue[0]],
    )
    attackers_blue_archers, killed_red_all_from_blue_archers = handle_attacks(
        ants_blue_archers,
        ants_footmen + ants_archers,
        [flags_blue[1]],
        attack_range=ARCHER_ATTACK_RANGE,
        kill_probability=ARCHER_KILL_PROBABILITY,
    )
    killed_blue_all = killed_blue_from_footmen.union(killed_blue_from_archers)
    killed_red_all = killed_red_all_from_blue.union(killed_red_all_from_blue_archers)
    killed_blue = {i for i in killed_blue_all if i < len(ants_blue)}
    killed_blue_archers = {i - len(ants_blue) for i in killed_blue_all if i >= len(ants_blue)}
    killed_footmen = {i for i in killed_red_all if i < len(ants_footmen)}
    killed_archers = {i - len(ants_footmen) for i in killed_red_all if i >= len(ants_footmen)}

    proposed_footmen = propose_moves(
        ants_footmen, attackers_footmen, flags_for_footmen, all_ants
    )
    proposed_archers = propose_moves(
        ants_archers, attackers_archers, flags_for_archers, all_ants
    )
    proposed_blue = propose_moves(
        ants_blue,
        attackers_blue,
        [flags_blue[0]],
        all_ants,
    )
    proposed_blue_archers = propose_moves(
        ants_blue_archers,
        attackers_blue_archers,
        [flags_blue[1]],
        all_ants,
    )

    new_ants_footmen = []
    new_ants_archers = []
    new_ants_blue = []
    new_ants_blue_archers = []
    occupied_new = []

    new_ants_footmen = resolve_positions(ants_footmen, proposed_footmen, killed_footmen, occupied_new)
    new_ants_archers = resolve_positions(
        ants_archers, proposed_archers, killed_archers, occupied_new
    )
    new_ants_blue = resolve_positions(ants_blue, proposed_blue, killed_blue, occupied_new)
    new_ants_blue_archers = resolve_positions(
        ants_blue_archers, proposed_blue_archers, killed_blue_archers, occupied_new
    )

    ants_footmen = [list(p) for p in new_ants_footmen]
    ants_archers = [list(p) for p in new_ants_archers]
    ants_blue = [list(p) for p in new_ants_blue]
    ants_blue_archers = [list(p) for p in new_ants_blue_archers]

    # remove flags that have been reached
    center_footmen = compute_centroid(ants_footmen)
    center_archers = compute_centroid(ants_archers)

    flag_for_footmen = first_flag(flag_queues[GROUP_FOOTMEN])
    if flag_for_footmen and center_footmen is not None:
        if math.hypot(center_footmen[0] - flag_for_footmen["pos"][0], center_footmen[1] - flag_for_footmen["pos"][1]) < FLAG_REACHED_DISTANCE:
            flag_queues[GROUP_FOOTMEN].pop(0)

    flag_for_archers = first_flag(flag_queues[GROUP_ARCHERS])
    if flag_for_archers and center_archers is not None:
        if math.hypot(center_archers[0] - flag_for_archers["pos"][0], center_archers[1] - flag_for_archers["pos"][1]) < FLAG_REACHED_DISTANCE:
            flag_queues[GROUP_ARCHERS].pop(0)

    screen.fill(BACKGROUND_COLOR)
    draw_ants(ants_footmen, ANT_COLOR_RED, attackers_footmen, ANT_COLOR_RED_ENGAGED)
    draw_ants(
        ants_archers,
        ANT_COLOR_ARCHER,
        attackers_archers,
        ANT_COLOR_ARCHER_ENGAGED,
        shape="semicircle",
    )
    draw_ants(
        ants_blue_archers,
        ANT_COLOR_ARCHER_BLUE,
        attackers_blue_archers,
        ANT_COLOR_ARCHER_BLUE_ENGAGED,
        shape="semicircle",
    )
    draw_ants(ants_blue, ANT_COLOR_BLUE, attackers_blue, ANT_COLOR_BLUE_ENGAGED)

    # control group banners for player units
    draw_group_banner(
        ants_footmen, ANT_COLOR_RED, GROUP_FOOTMEN, active_group == GROUP_FOOTMEN
    )
    draw_group_banner(
        ants_archers, ANT_COLOR_ARCHER, GROUP_ARCHERS, active_group == GROUP_ARCHERS
    )

    for group_id, ants in [
        (GROUP_FOOTMEN, ants_footmen),
        (GROUP_ARCHERS, ants_archers),
    ]:
        queue = flag_queues[group_id]
        if queue:
            start_center = compute_centroid(ants)
            if start_center:
                draw_flag_path(start_center, queue)

    for idx, flag in enumerate(flag_queues[GROUP_FOOTMEN], start=1):
        draw_flag(flag["pos"], FLAG_COLOR_RED, idx, flag["type"])
    for idx, flag in enumerate(flag_queues[GROUP_ARCHERS], start=1):
        draw_flag(flag["pos"], FLAG_COLOR_RED, idx, flag["type"])
    for flag in flags_blue:
        draw_flag(flag["pos"], FLAG_COLOR_BLUE)

    for idx, template in enumerate(flag_templates):
        draw_flag_icon(idx, template["type"], idx == active_flag_idx)

    # Display remaining ant counts in the top-right corner
    count_text = font.render(
        (
            f"Footmen: {len(ants_footmen)}  Archers: {len(ants_archers)}  "
            f"Blue Footmen: {len(ants_blue)}  Blue Archers: {len(ants_blue_archers)}"
        ),
        True,
        (255, 255, 255),
    )
    text_rect = count_text.get_rect(topright=(WIDTH - 5, 5))
    screen.blit(count_text, text_rect)

    engaged_text = font.render(
        (
            f"Engaged - Footmen: {len(attackers_footmen)}  "
            f"Archers: {len(attackers_archers)}  "
            f"Blue Footmen: {len(attackers_blue)}  "
            f"Blue Archers: {len(attackers_blue_archers)}"
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

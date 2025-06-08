#!/usr/bin/env python3

import pygame
import sys
import random
import math
import time

WIDTH, HEIGHT = 640, 480
NUM_ANTS = 200
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

BACKGROUND_COLOR = (0, 0, 0)
FLAG_COLOR_RED = (255, 100, 100)  # light red
FLAG_COLOR_BLUE = (0, 255, 255)  # cyan flag
FLAG_POLE_COLOR = (200, 200, 200)
FLAG_SIZE = 12
DOT_SIZE = 2
MIN_DISTANCE = 4  # minimum distance between ants in pixels
ATTACK_RANGE = 9  # distance within which ants will attack instead of moving
KILL_PROBABILITY = 0.1  # chance that an attack kills the target

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Initialize ants for both players at random positions
ants_red = []
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


def handle_attacks(ants, enemies):
    """Return sets of attackers and killed enemy indices."""
    attackers = set()
    killed = set()
    for i, (x, y) in enumerate(ants):
        target = find_nearest_enemy(x, y, enemies)
        if target is not None:
            attackers.add(i)
            if random.random() < KILL_PROBABILITY:
                killed.add(target)
    return attackers, killed


def propose_moves(ants, attackers, flag_pos, all_ants):
    """Return proposed new positions for ants."""
    proposed = []
    for i, (x, y) in enumerate(ants):
        if flag_pos is None:
            proposed.append((x, y))
            continue

        speed = 0.3 if i in attackers else 1.0
        vx, vy = compute_move_vector(x, y, flag_pos, all_ants)
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


def draw_ants(ants, color, engaged=None, engaged_color=None):
    """Draw ants, highlighting engaged ones with a lighter color."""
    for i, (x, y) in enumerate(ants):
        c = color
        if engaged and i in engaged:
            c = engaged_color if engaged_color else color
        pygame.draw.rect(screen, c, (x, y, DOT_SIZE, DOT_SIZE))


def draw_flag(flag_pos, color):
    """Draw a flag if its position is defined."""
    if flag_pos is None:
        return
    fx, fy = flag_pos
    pole_top = (fx, max(0, fy - 10))
    pygame.draw.line(screen, FLAG_POLE_COLOR, flag_pos, pole_top)
    flag_points = [
        pole_top,
        (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
        (pole_top[0], pole_top[1] + FLAG_SIZE),
    ]
    pygame.draw.polygon(screen, color, flag_points)


# Place red ants in the lower-left corner (25% of the screen)
while len(ants_red) < NUM_ANTS:
    x = random.uniform(0, WIDTH * 0.25)
    y = random.uniform(HEIGHT * 0.75, HEIGHT)
    if is_valid_position(x, y, occupied):
        ants_red.append([x, y])
        occupied.add((x, y))

# Place blue ants in the upper-right corner (25% of the screen)
while len(ants_blue) < NUM_ANTS_BLUE:
    x = random.uniform(WIDTH * 0.75, WIDTH)
    y = random.uniform(0, HEIGHT * 0.25)
    if is_valid_position(x, y, occupied):
        ants_blue.append([x, y])
        occupied.add((x, y))

flag_pos_red = None
flag_pos_blue = (random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
next_flag_move = time.time() + random.uniform(5, 30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            flag_pos_red = event.pos

    # move the computer-controlled flag occasionally
    now = time.time()
    if now >= next_flag_move:
        flag_pos_blue = (random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        next_flag_move = now + random.uniform(5, 30)

    all_ants = ants_red + ants_blue

    attackers_red, killed_blue = handle_attacks(ants_red, ants_blue)
    attackers_blue, killed_red = handle_attacks(ants_blue, ants_red)

    proposed_red = propose_moves(ants_red, attackers_red, flag_pos_red, all_ants)
    proposed_blue = propose_moves(ants_blue, attackers_blue, flag_pos_blue, all_ants)

    new_ants_red = []
    new_ants_blue = []
    occupied_new = []

    new_ants_red = resolve_positions(ants_red, proposed_red, killed_red, occupied_new)
    new_ants_blue = resolve_positions(ants_blue, proposed_blue, killed_blue, occupied_new)

    ants_red = [list(p) for p in new_ants_red]
    ants_blue = [list(p) for p in new_ants_blue]

    screen.fill(BACKGROUND_COLOR)
    draw_ants(ants_red, ANT_COLOR_RED, attackers_red, ANT_COLOR_RED_ENGAGED)
    draw_ants(ants_blue, ANT_COLOR_BLUE, attackers_blue, ANT_COLOR_BLUE_ENGAGED)

    draw_flag(flag_pos_red, FLAG_COLOR_RED)
    draw_flag(flag_pos_blue, FLAG_COLOR_BLUE)

    # Display remaining ant counts in the top-right corner
    count_text = font.render(
        f"Red: {len(ants_red)}  Blue: {len(ants_blue)}",
        True,
        (255, 255, 255),
    )
    text_rect = count_text.get_rect(topright=(WIDTH - 5, 5))
    screen.blit(count_text, text_rect)

    engaged_text = font.render(
        f"Engaged - Red: {len(attackers_red)}  Blue: {len(attackers_blue)}",
        True,
        (255, 255, 255),
    )
    engaged_rect = engaged_text.get_rect(topright=(WIDTH - 5, 25))
    screen.blit(engaged_text, engaged_rect)

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
sys.exit()

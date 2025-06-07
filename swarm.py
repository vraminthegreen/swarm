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

    killed_red = set()
    killed_blue = set()
    attackers_red = set()
    attackers_blue = set()

    for i, (x, y) in enumerate(ants_red):
        target = find_nearest_enemy(x, y, ants_blue)
        if target is not None:
            attackers_red.add(i)
            if random.random() < KILL_PROBABILITY:
                killed_blue.add(target)

    for i, (x, y) in enumerate(ants_blue):
        target = find_nearest_enemy(x, y, ants_red)
        if target is not None:
            attackers_blue.add(i)
            if random.random() < KILL_PROBABILITY:
                killed_red.add(target)

    if flag_pos_red is not None:
        proposed_red = []
        for i, (x, y) in enumerate(ants_red):
            if i in attackers_red:
                proposed_red.append((x, y))
                continue
            vx, vy = compute_move_vector(x, y, flag_pos_red, all_ants)
            nx = max(0, min(WIDTH - 1, x + vx))
            ny = max(0, min(HEIGHT - 1, y + vy))
            proposed_red.append((nx, ny))
    else:
        proposed_red = [tuple(a) for a in ants_red]

    proposed_blue = []
    for i, (x, y) in enumerate(ants_blue):
        if i in attackers_blue:
            proposed_blue.append((x, y))
            continue
        vx, vy = compute_move_vector(x, y, flag_pos_blue, all_ants)
        nx = max(0, min(WIDTH - 1, x + vx))
        ny = max(0, min(HEIGHT - 1, y + vy))
        proposed_blue.append((nx, ny))

    new_ants_red = []
    new_ants_blue = []
    occupied_new = []

    for i, (nx, ny) in enumerate(proposed_red):
        if i in killed_red:
            continue
        if is_valid_position(nx, ny, occupied_new):
            new_ants_red.append((nx, ny))
            occupied_new.append((nx, ny))
        else:
            new_ants_red.append(tuple(ants_red[i]))
            occupied_new.append(tuple(ants_red[i]))

    for i, (nx, ny) in enumerate(proposed_blue):
        if i in killed_blue:
            continue
        if is_valid_position(nx, ny, occupied_new):
            new_ants_blue.append((nx, ny))
            occupied_new.append((nx, ny))
        else:
            new_ants_blue.append(tuple(ants_blue[i]))
            occupied_new.append(tuple(ants_blue[i]))

    ants_red = [list(p) for p in new_ants_red]
    ants_blue = [list(p) for p in new_ants_blue]

    screen.fill(BACKGROUND_COLOR)
    for x, y in ants_red:
        pygame.draw.rect(screen, ANT_COLOR_RED, (x, y, DOT_SIZE, DOT_SIZE))
    for x, y in ants_blue:
        pygame.draw.rect(screen, ANT_COLOR_BLUE, (x, y, DOT_SIZE, DOT_SIZE))

    if flag_pos_red is not None:
        fx, fy = flag_pos_red
        pole_top = (fx, max(0, fy - 10))
        pygame.draw.line(screen, FLAG_POLE_COLOR, flag_pos_red, pole_top)
        flag_points = [
            pole_top,
            (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
            (pole_top[0], pole_top[1] + FLAG_SIZE),
        ]
        pygame.draw.polygon(screen, FLAG_COLOR_RED, flag_points)

    if flag_pos_blue is not None:
        fx, fy = flag_pos_blue
        pole_top = (fx, max(0, fy - 10))
        pygame.draw.line(screen, FLAG_POLE_COLOR, flag_pos_blue, pole_top)
        flag_points = [
            pole_top,
            (pole_top[0] + FLAG_SIZE, pole_top[1] + FLAG_SIZE // 2),
            (pole_top[0], pole_top[1] + FLAG_SIZE),
        ]
        pygame.draw.polygon(screen, FLAG_COLOR_BLUE, flag_points)

    # Display remaining ant counts in the top-right corner
    count_text = font.render(f"Red: {len(ants_red)}  Blue: {len(ants_blue)}", True, (255, 255, 255))
    text_rect = count_text.get_rect(topright=(WIDTH - 5, 5))
    screen.blit(count_text, text_rect)

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
sys.exit()

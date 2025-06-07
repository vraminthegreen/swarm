#!/usr/bin/env python3

import pygame
import sys
import random
import math

WIDTH, HEIGHT = 640, 480
NUM_ANTS = 200
ANT_COLOR = (255, 0, 0)  # red ants
BACKGROUND_COLOR = (0, 0, 0)  # black
FLAG_COLOR = (0, 255, 0)  # green
FLAG_POLE_COLOR = (200, 200, 200)
DOT_SIZE = 2
MIN_DISTANCE = 5  # minimum distance between ants in pixels

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Initialize ants at random positions (floating point coordinates)
ants = []
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


while len(ants) < NUM_ANTS:
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    if is_valid_position(x, y, occupied):
        ants.append([x, y])
        occupied.add((x, y))

flag_pos = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            flag_pos = event.pos

    # Update ants toward the flag
    if flag_pos is not None:
        proposed = []
        for x, y in ants:
            vx, vy = compute_move_vector(x, y, flag_pos, ants)
            nx = x + vx
            ny = y + vy
            nx = max(0, min(WIDTH - 1, nx))
            ny = max(0, min(HEIGHT - 1, ny))
            proposed.append((nx, ny))

        new_positions = []
        for i, (nx, ny) in enumerate(proposed):
            if is_valid_position(nx, ny, new_positions):
                new_positions.append((nx, ny))
            else:
                new_positions.append(tuple(ants[i]))
        ants = [list(p) for p in new_positions]

    screen.fill(BACKGROUND_COLOR)
    for x, y in ants:
        pygame.draw.rect(screen, ANT_COLOR, (x, y, DOT_SIZE, DOT_SIZE))
    if flag_pos is not None:
        fx, fy = flag_pos
        pole_top = (fx, max(0, fy - 10))
        pygame.draw.line(screen, FLAG_POLE_COLOR, flag_pos, pole_top)
        flag_points = [
            pole_top,
            (pole_top[0] + 6, pole_top[1] + 3),
            (pole_top[0], pole_top[1] + 6),
        ]
        pygame.draw.polygon(screen, FLAG_COLOR, flag_points)
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()

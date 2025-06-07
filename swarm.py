#!/usr/bin/env python3

import pygame
import sys
import random

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

# Initialize ants at random positions
ants = []
occupied = set()
def is_valid_position(x, y, others):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return False
    for ox, oy in others:
        if (x - ox) ** 2 + (y - oy) ** 2 < MIN_DISTANCE ** 2:
            return False
    return True

def step_away_from_conflict(x, y, others):
    """Move a step away from the nearest ant violating the distance."""
    nearest = None
    min_d2 = MIN_DISTANCE ** 2
    for ox, oy in others:
        d2 = (x - ox) ** 2 + (y - oy) ** 2
        if 0 < d2 < min_d2:
            min_d2 = d2
            nearest = (ox, oy)
    if nearest is None:
        return x, y

    ox, oy = nearest
    dx = 0 if x == ox else (1 if x > ox else -1)
    dy = 0 if y == oy else (1 if y > oy else -1)
    nx, ny = x + dx, y + dy
    if is_valid_position(nx, ny, others):
        return nx, ny
    return x, y

def pseudo_gravity_move(x, y, flag_pos, others):
    """Compute a move combining repulsion from nearby ants and attraction to the flag."""
    ax = ay = 0.0
    for ox, oy in others:
        dx = x - ox
        dy = y - oy
        d2 = dx * dx + dy * dy
        if 0 < d2 < MIN_DISTANCE ** 2:
            dist = d2 ** 0.5
            ax += dx / dist
            ay += dy / dist

    fx = flag_pos[0] - x
    fy = flag_pos[1] - y
    flen = (fx * fx + fy * fy) ** 0.5
    if flen != 0:
        fx /= flen
        fy /= flen
    else:
        fx = fy = 0.0

    vx = ax + fx
    vy = ay + fy
    vlen = (vx * vx + vy * vy) ** 0.5
    if vlen == 0:
        return x, y
    vx /= vlen
    vy /= vlen

    step_x = 0 if abs(vx) < 1e-6 else (1 if vx > 0 else -1)
    step_y = 0 if abs(vy) < 1e-6 else (1 if vy > 0 else -1)
    nx, ny = x + step_x, y + step_y
    if is_valid_position(nx, ny, others):
        return nx, ny
    return x, y

while len(ants) < NUM_ANTS:
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
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
        new_occupied = set()
        for i, (x, y) in enumerate(ants):
            moved = False

            # 1. Try a random move first with small probability
            if random.random() < 0.05:
                rdx = random.choice([-1, 0, 1])
                rdy = random.choice([-1, 0, 1])
                rx, ry = x + rdx, y + rdy
                if is_valid_position(rx, ry, new_occupied):
                    nx, ny = rx, ry
                    moved = True

            if not moved:
                # 2. Compute pseudo-gravity move
                px, py = pseudo_gravity_move(x, y, flag_pos, new_occupied)
                if (px, py) != (x, y):
                    nx, ny = px, py
                    moved = True

            if not moved:
                # 3. If still conflicted, step away from nearby ants
                if not is_valid_position(x, y, new_occupied):
                    nx, ny = step_away_from_conflict(x, y, new_occupied)
                else:
                    nx, ny = x, y

            ants[i] = [nx, ny]
            new_occupied.add((nx, ny))
        occupied = new_occupied

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

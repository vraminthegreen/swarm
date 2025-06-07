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
            dx = 0 if flag_pos[0] == x else (1 if flag_pos[0] > x else -1)
            dy = 0 if flag_pos[1] == y else (1 if flag_pos[1] > y else -1)

            # Occasionally move randomly instead of toward the flag
            if random.random() < 0.05:
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])

            nx, ny = x + dx, y + dy
            # Ensure ants keep minimum distance from each other
            if not is_valid_position(nx, ny, new_occupied):
                if is_valid_position(x, y, new_occupied):
                    nx, ny = x, y
                else:
                    for _ in range(100):
                        rx = random.randint(0, WIDTH - 1)
                        ry = random.randint(0, HEIGHT - 1)
                        if is_valid_position(rx, ry, new_occupied):
                            nx, ny = rx, ry
                            break

            ants[i] = [nx, ny]
            new_occupied.add((nx, ny))
        occupied = new_occupied

    screen.fill(BACKGROUND_COLOR)
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
    for x, y in ants:
        pygame.draw.rect(screen, ANT_COLOR, (x, y, DOT_SIZE, DOT_SIZE))
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()

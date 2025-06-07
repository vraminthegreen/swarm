import pygame
import sys
import random

WIDTH, HEIGHT = 640, 480
NUM_DOTS = 50
DOT_COLOR = (255, 0, 0)  # red
BACKGROUND_COLOR = (0, 0, 0)  # black
FLAG_COLOR = (0, 255, 0)  # green
FLAG_POLE_COLOR = (200, 200, 200)
DOT_SIZE = 2

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Initialize dots at random positions
dots = []
occupied = set()
while len(dots) < NUM_DOTS:
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
    if (x, y) not in occupied:
        dots.append([x, y])
        occupied.add((x, y))

flag_pos = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            flag_pos = event.pos

    # Update dots toward the flag
    if flag_pos is not None:
        new_occupied = set()
        for i, (x, y) in enumerate(dots):
            dx = 0 if flag_pos[0] == x else (1 if flag_pos[0] > x else -1)
            dy = 0 if flag_pos[1] == y else (1 if flag_pos[1] > y else -1)
            nx, ny = x + dx, y + dy
            # Ensure only one dot per pixel
            if (nx, ny) not in new_occupied and (0 <= nx < WIDTH) and (0 <= ny < HEIGHT):
                dots[i] = [nx, ny]
                new_occupied.add((nx, ny))
            else:
                new_occupied.add((x, y))
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
    for x, y in dots:
        pygame.draw.rect(screen, DOT_COLOR, (x, y, DOT_SIZE, DOT_SIZE))
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()

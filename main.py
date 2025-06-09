#!/usr/bin/env python3

import pygame
import sys
import random
import math
import time

from order_queue import OrderQueue
from swarm import Swarm

from flag import (
    Flag,
    NormalFlag,
    FastFlag,
    StopFlag,
    ArcherFlag,
    FLAG_SIZE,
)

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


# Control groups for player units
GROUP_FOOTMEN = 1
GROUP_ARCHERS = 2

BACKGROUND_COLOR = (0, 0, 0)
FLAG_COLOR_RED = (255, 100, 100)  # light red
FLAG_COLOR_BLUE = (0, 255, 255)  # cyan flag
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
    {"cls": NormalFlag},
    {"cls": NormalFlag},
    {"cls": FastFlag},
    {"cls": StopFlag},
]

# Swarms controlled by the player
swarm_footmen = Swarm(ANT_COLOR_RED, GROUP_FOOTMEN, FLAG_COLOR_RED)
swarm_archers = Swarm(
    ANT_COLOR_ARCHER,
    GROUP_ARCHERS,
    FLAG_COLOR_RED,
    shape="semicircle",
)
swarm_footmen.show()
swarm_archers.show()

# Swarms controlled by the AI
swarm_blue_footmen = Swarm(ANT_COLOR_BLUE, 5, FLAG_COLOR_BLUE)
swarm_blue_archers = Swarm(
    ANT_COLOR_ARCHER_BLUE,
    6,
    FLAG_COLOR_BLUE,
    shape="semicircle",
)
swarm_blue_footmen.show()
swarm_blue_archers.show()

# Queue of player-issued flags for each control group
flag_queues = {
    GROUP_FOOTMEN: swarm_footmen.queue,
    GROUP_ARCHERS: swarm_archers.queue,
}

# Currently selected control group
active_group = GROUP_FOOTMEN



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
    """Draw dashed path from ``start_pos`` through the list of ``Flag`` objects."""
    current = start_pos
    for flag in flags:
        if flag.pos is None:
            continue
        draw_dashed_line(current, flag.pos)
        current = flag.pos

occupied = set()


# Place footmen in the lower-left corner (25% of the screen)
swarm_footmen.spawn(
    NUM_FOOTMEN,
    (0, WIDTH * 0.25),
    (HEIGHT * 0.75, HEIGHT),
    occupied,
)

# Place red archers in the upper-left corner
swarm_archers.spawn(
    NUM_ARCHERS,
    (0, WIDTH * 0.25),
    (0, HEIGHT * 0.25),
    occupied,
)

# Place blue footmen in the upper-right corner (25% of the screen)
swarm_blue_footmen.spawn(
    NUM_ANTS_BLUE,
    (WIDTH * 0.75, WIDTH),
    (0, HEIGHT * 0.25),
    occupied,
)

# Place blue archers in the lower-right corner
swarm_blue_archers.spawn(
    NUM_ARCHERS_BLUE,
    (WIDTH * 0.75, WIDTH),
    (HEIGHT * 0.75, HEIGHT),
    occupied,
)

active_flag_idx = 0

# Blue team alternates between footman and archer flags
flags_blue = [
    NormalFlag((random.uniform(0, WIDTH), random.uniform(0, HEIGHT)), FLAG_COLOR_BLUE),
    ArcherFlag(None, FLAG_COLOR_BLUE),
]
for f in flags_blue:
    f.show()
next_blue_flag_idx = 1
next_blue_flag_move = time.time() + random.uniform(5, 20)

running = True
print("[Swarm] starting")
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
            handled = False
            for queue in flag_queues.values():
                if queue.handleEvent(event):
                    handled = True
                    break
            if not handled:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    flag_cls = FastFlag
                else:
                    flag_cls = flag_templates[active_flag_idx]["cls"]
                flag_queues[active_group].add_flag_at(event.pos, flag_cls)

    # move the computer-controlled flags alternately
    now = time.time()
    if now >= next_blue_flag_move:
        flags_blue[next_blue_flag_idx].pos = (
            random.uniform(0, WIDTH),
            random.uniform(0, HEIGHT),
        )
        next_blue_flag_idx = 1 - next_blue_flag_idx
        next_blue_flag_move = now + random.uniform(5, 20)

    swarm_footmen.tick(1.0)
    swarm_archers.tick(1.0)
    swarm_blue_footmen.tick(1.0)
    swarm_blue_archers.tick(1.0)

    screen.fill(BACKGROUND_COLOR)
    swarm_footmen.engaged = set()
    swarm_archers.engaged = set()
    swarm_footmen.active = active_group == GROUP_FOOTMEN
    swarm_archers.active = active_group == GROUP_ARCHERS
    swarm_footmen.draw(screen)
    swarm_archers.draw(screen)
    swarm_blue_archers.engaged = set()
    swarm_blue_footmen.engaged = set()
    swarm_blue_archers.draw(screen)
    swarm_blue_footmen.draw(screen)

    # draw AI flags after swarms
    for flag in flags_blue:
        flag.draw(screen)

    for idx, template in enumerate(flag_templates):
        temp = template["cls"](None, FLAG_COLOR_RED)
        temp.show()
        temp.draw_icon(screen, idx, HEIGHT, idx == active_flag_idx)

    # Display remaining ant counts in the top-right corner
    count_text = font.render(
        (
            f"Footmen: {len(swarm_footmen.ants)}  Archers: {len(swarm_archers.ants)}  "
            f"Blue Footmen: {len(swarm_blue_footmen.ants)}  "
            f"Blue Archers: {len(swarm_blue_archers.ants)}"
        ),
        True,
        (255, 255, 255),
    )
    text_rect = count_text.get_rect(topright=(WIDTH - 5, 5))
    screen.blit(count_text, text_rect)


    pygame.display.flip()
    clock.tick(20)

pygame.quit()
sys.exit()

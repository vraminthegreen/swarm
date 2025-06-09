#!/usr/bin/env python3

import pygame
import sys
import random

from swarm import Swarm
from ai_player import AIPlayer

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


# Queue of player-issued flags for each control group
flag_queues = {
    GROUP_FOOTMEN: swarm_footmen.queue,
    GROUP_ARCHERS: swarm_archers.queue,
}

# Currently selected control group
active_group = GROUP_FOOTMEN

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

# Initialize AI player after red units occupy the battlefield
ai_player = AIPlayer(
    WIDTH,
    HEIGHT,
    NUM_ANTS_BLUE,
    NUM_ARCHERS_BLUE,
    occupied,
)
ai_player.show()

active_flag_idx = 0

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

    swarm_footmen.tick(1.0)
    swarm_archers.tick(1.0)
    ai_player.tick(1.0)

    screen.fill(BACKGROUND_COLOR)
    swarm_footmen.engaged = set()
    swarm_archers.engaged = set()
    swarm_footmen.active = active_group == GROUP_FOOTMEN
    swarm_archers.active = active_group == GROUP_ARCHERS
    swarm_footmen.draw(screen)
    swarm_archers.draw(screen)
    ai_player.swarm_archers.engaged = set()
    ai_player.swarm_footmen.engaged = set()
    ai_player.draw(screen)

    for idx, template in enumerate(flag_templates):
        temp = template["cls"](None, FLAG_COLOR_RED)
        temp.show()
        temp.draw_icon(screen, idx, HEIGHT, idx == active_flag_idx)

    # Display remaining ant counts in the top-right corner
    count_text = font.render(
        (
            f"Footmen: {len(swarm_footmen.ants)}  Archers: {len(swarm_archers.ants)}  "
            f"Blue Footmen: {len(ai_player.swarm_footmen.ants)}  "
            f"Blue Archers: {len(ai_player.swarm_archers.ants)}"
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

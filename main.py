#!/usr/bin/env python3

import pygame
import sys
import time

from game_field import GameField


def main():
    pygame.init()

    field = GameField()
    screen = pygame.display.set_mode((field.width, field.height))
    clock = pygame.time.Clock()
    field.show()

    running = True
    print("[Swarm] starting")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                field.handleEvent(event)

        field.tick(1.0)
        field.draw(screen)
        pygame.display.flip()
        clock.tick(20)
        time.sleep(0.01)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

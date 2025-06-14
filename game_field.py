import pygame
import random

from stage import Stage
from swarm import (
    Swarm,
    ATTACK_RANGE,
    ARCHER_ATTACK_RANGE,
    KILL_PROBABILITY,
    ARCHER_KILL_PROBABILITY,
)
from destructibles import Destructibles
from ai_player import AIPlayer
from human_player import HumanPlayer
from flag import NormalFlag, FastFlag, StopFlag


# Set to ``True`` to overlay the cost field of the active flag in grayscale.
DEBUG_DRAW_COSTS = True


class GameField(Stage):
    """Main game field containing player swarms and the AI player."""

    # Default configuration
    WIDTH = 640
    HEIGHT = 480

    NUM_FOOTMEN = 150
    NUM_ARCHERS = 50
    NUM_ANTS_BLUE = 200
    NUM_ARCHERS_BLUE = 50
    NUM_CANNONS = 3
    NUM_CANNONS_BLUE = 3

    GROUP_FOOTMEN = 1
    GROUP_ARCHERS = 2
    GROUP_CANNON = 3

    BACKGROUND_COLOR = (0, 0, 0)
    FLAG_COLOR_RED = (255, 100, 100)

    def __init__(self, width=WIDTH, height=HEIGHT):
        super().__init__()
        self.width = width
        self.height = height

        # Fonts for overlay information
        self.font = pygame.font.Font(None, 24)

        # Templates for new flags
        self.flag_templates = [
            {"cls": NormalFlag},
            {"cls": NormalFlag},
            {"cls": FastFlag},
            {"cls": StopFlag},
        ]

        # Selected group and flag type
        self.active_group = self.GROUP_FOOTMEN
        self.active_flag_idx = 0

        # Create players and their swarms
        occupied = set()
        self.human_player = HumanPlayer(
            width,
            height,
            self.NUM_FOOTMEN,
            self.NUM_ARCHERS,
            occupied,
            group_footmen=self.GROUP_FOOTMEN,
            group_archers=self.GROUP_ARCHERS,
            group_cannon=self.GROUP_CANNON,
            num_cannons=self.NUM_CANNONS,
            color=(255, 0, 0),
            flag_color=self.FLAG_COLOR_RED,
        )
        self.ai_player = AIPlayer(
            width,
            height,
            self.NUM_ANTS_BLUE,
            self.NUM_ARCHERS_BLUE,
            occupied,
            num_cannons=self.NUM_CANNONS_BLUE,
        )

        self.destructibles = Destructibles(
            width,
            height,
            num_trees=20,
            occupied=occupied,
            line_ratio=0.5,
        )

        # Register enemies
        self.human_player.enemies.append(self.ai_player)
        self.ai_player.enemies.append(self.human_player)
        self.human_player.enemies.append(self.destructibles)
        self.ai_player.enemies.append(self.destructibles)
        self.destructibles.enemies.extend([self.human_player, self.ai_player])

        self.swarm_footmen = self.human_player.swarm_footmen
        self.swarm_archers = self.human_player.swarm_archers
        self.swarm_cannon = self.human_player.swarm_cannon
        self.ai_swarm_cannon = self.ai_player.swarm_cannon

        for swarm in [
            self.swarm_footmen,
            self.swarm_archers,
            self.swarm_cannon,
            self.ai_player.swarm_footmen,
            self.ai_player.swarm_archers,
            self.ai_swarm_cannon,
        ]:
            self.destructibles.register_invalidator(swarm.invalidate_flow_field)

        # Organise stage hierarchy
        self.add_stage(self.human_player)
        self.add_stage(self.ai_player)
        self.add_stage(self.destructibles)

        self.human_player.show()
        self.ai_player.show()
        self.destructibles.show()

        self.flag_queues = {
            self.GROUP_FOOTMEN: self.swarm_footmen.queue,
            self.GROUP_ARCHERS: self.swarm_archers.queue,
            self.GROUP_CANNON: self.swarm_cannon.queue,
        }

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def _handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.active_group = self.GROUP_FOOTMEN
                return True
            if event.key == pygame.K_2:
                self.active_group = self.GROUP_ARCHERS
                return True
            if event.key == pygame.K_3:
                self.active_group = self.GROUP_CANNON
                return True
            if event.key in (pygame.K_a, pygame.K_m):
                flag_cls = NormalFlag if event.key == pygame.K_a else FastFlag
                pos = pygame.mouse.get_pos()
                queue = self.flag_queues[self.active_group]
                mods = getattr(event, "mod", pygame.key.get_mods())
                if mods & pygame.KMOD_SHIFT:
                    queue.add_flag_at(pos, flag_cls)
                else:
                    queue.clear()
                    queue.add_flag_at(pos, flag_cls)
                return True
            if event.key == pygame.K_DELETE:
                if self.flag_queues[self.active_group]:
                    self.flag_queues[self.active_group].pop()
                return True
            if event.key == pygame.K_BACKSPACE:
                self.flag_queues[self.active_group].clear()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            queue = self.flag_queues[self.active_group]
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                queue.add_flag_at(event.pos, NormalFlag)
            else:
                queue.clear()
                queue.add_flag_at(event.pos, NormalFlag)
            return True
        return False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw(self, screen):
        # Background and state updates
        screen.fill(self.BACKGROUND_COLOR)
        self.swarm_footmen.active = self.active_group == self.GROUP_FOOTMEN
        self.swarm_archers.active = self.active_group == self.GROUP_ARCHERS
        self.swarm_cannon.active = self.active_group == self.GROUP_CANNON

        if DEBUG_DRAW_COSTS:
            self._draw_active_flow_field(screen)

        # Flag icons
        for idx, template in enumerate(self.flag_templates):
            temp = template["cls"](None, self.FLAG_COLOR_RED)
            temp.show()
            temp.draw_icon(screen, idx, self.height, idx == self.active_flag_idx)


    def _draw_active_flow_field(self, screen):
        print("_draw_active_flow_field")
        swarm_map = {
            self.GROUP_FOOTMEN: self.swarm_footmen,
            self.GROUP_ARCHERS: self.swarm_archers,
            self.GROUP_CANNON: self.swarm_cannon,
        }
        swarm = swarm_map.get(self.active_group)
        if not swarm:
            return
        swarm._update_flow_field()
        ff = swarm._flow_field
        if ff is None or ff.max_distance == 0:
            return
        cell = ff.cell_size
        for y in range(ff.grid_h):
            for x in range(ff.grid_w):
                cost = ff.costs[y][x]
                if cost == ff.INF:
                    continue
                intensity = int(255 * (1 - cost / ff.max_distance))
                intensity = max(0, min(255, intensity))
                if intensity <= 0:
                    continue
                rect = pygame.Rect(x * cell, y * cell, cell, cell)
                color = (intensity, intensity, intensity)
                screen.fill(color, rect)



    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    # def tick(self, dt):
    #     """Advance children first, then resolve combat."""
    #     for child in self._children:
    #         child.tick(dt)
    #     self._tick(dt)

    def _tick(self, dt):
        self.swarm_footmen.engaged = set()
        self.swarm_archers.engaged = set()
        self.swarm_cannon.engaged = set()
        self.ai_player.swarm_archers.engaged = set()
        self.ai_player.swarm_footmen.engaged = set()
        self.ai_swarm_cannon.engaged = set()


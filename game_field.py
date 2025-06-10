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
from ai_player import AIPlayer
from flag import NormalFlag, FastFlag, StopFlag


class GameField(Stage):
    """Main game field containing player swarms and the AI player."""

    # Default configuration
    WIDTH = 640
    HEIGHT = 480

    NUM_FOOTMEN = 150
    NUM_ARCHERS = 50
    NUM_ANTS_BLUE = 200
    NUM_ARCHERS_BLUE = 50

    GROUP_FOOTMEN = 1
    GROUP_ARCHERS = 2

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

        # Player-controlled swarms
        self.swarm_footmen = Swarm((255, 0, 0), self.GROUP_FOOTMEN, self.FLAG_COLOR_RED, width=width, height=height)
        self.swarm_archers = Swarm(
            (255, 0, 0),
            self.GROUP_ARCHERS,
            self.FLAG_COLOR_RED,
            shape="semicircle",
            width=width,
            height=height,
        )

        # Spawn units and create AI player
        occupied = set()
        self.swarm_footmen.spawn(
            self.NUM_FOOTMEN,
            (0, width * 0.25),
            (height * 0.75, height),
            occupied,
        )
        self.swarm_archers.spawn(
            self.NUM_ARCHERS,
            (0, width * 0.25),
            (0, height * 0.25),
            occupied,
        )

        self.ai_player = AIPlayer(width, height, self.NUM_ANTS_BLUE, self.NUM_ARCHERS_BLUE, occupied)

        # Organise stage hierarchy
        self.add_stage(self.swarm_footmen)
        self.add_stage(self.swarm_archers)
        self.add_stage(self.ai_player)

        self.swarm_footmen.show()
        self.swarm_archers.show()
        self.ai_player.show()

        self.flag_queues = {
            self.GROUP_FOOTMEN: self.swarm_footmen.queue,
            self.GROUP_ARCHERS: self.swarm_archers.queue,
        }

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def _handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.active_flag_idx = 0
                self.active_group = self.GROUP_FOOTMEN
                return True
            if event.key == pygame.K_2:
                self.active_flag_idx = 1
                self.active_group = self.GROUP_ARCHERS
                return True
            if event.key == pygame.K_3:
                self.active_flag_idx = 2
                return True
            if event.key == pygame.K_4:
                self.active_flag_idx = 3
                return True
            if event.key == pygame.K_DELETE:
                if self.flag_queues[self.active_group]:
                    self.flag_queues[self.active_group].pop()
                return True
            if event.key == pygame.K_BACKSPACE:
                self.flag_queues[self.active_group].clear()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                flag_cls = FastFlag
            else:
                flag_cls = self.flag_templates[self.active_flag_idx]["cls"]
            self.flag_queues[self.active_group].add_flag_at(event.pos, flag_cls)
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

        # Flag icons
        for idx, template in enumerate(self.flag_templates):
            temp = template["cls"](None, self.FLAG_COLOR_RED)
            temp.show()
            temp.draw_icon(screen, idx, self.height, idx == self.active_flag_idx)



    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def tick(self, dt):
        """Advance children first, then resolve combat."""
        for child in self._children:
            child.tick(dt)
        self._tick(dt)

    def _tick(self, dt):
        self.swarm_footmen.engaged = set()
        self.swarm_archers.engaged = set()
        self.ai_player.swarm_archers.engaged = set()
        self.ai_player.swarm_footmen.engaged = set()
        self._resolve_combat()

    # ------------------------------------------------------------------
    # Combat resolution
    # ------------------------------------------------------------------
    def _resolve_combat(self):
        self._handle_combat(self.swarm_footmen, self.ai_player.swarm_footmen, ATTACK_RANGE, KILL_PROBABILITY)
        self._handle_combat(self.swarm_footmen, self.ai_player.swarm_archers, ATTACK_RANGE, KILL_PROBABILITY)
        self._handle_combat(self.swarm_archers, self.ai_player.swarm_footmen, ARCHER_ATTACK_RANGE, ARCHER_KILL_PROBABILITY)
        self._handle_combat(self.swarm_archers, self.ai_player.swarm_archers, ARCHER_ATTACK_RANGE, ARCHER_KILL_PROBABILITY)
        self._handle_combat(self.ai_player.swarm_footmen, self.swarm_footmen, ATTACK_RANGE, KILL_PROBABILITY)
        self._handle_combat(self.ai_player.swarm_footmen, self.swarm_archers, ATTACK_RANGE, KILL_PROBABILITY)
        self._handle_combat(self.ai_player.swarm_archers, self.swarm_footmen, ARCHER_ATTACK_RANGE, ARCHER_KILL_PROBABILITY)
        self._handle_combat(self.ai_player.swarm_archers, self.swarm_archers, ARCHER_ATTACK_RANGE, ARCHER_KILL_PROBABILITY)

    def _handle_combat(self, attackers, defenders, attack_range, kill_prob):
        engaged_attackers = set()
        engaged_defenders = set()
        remove_indices = []
        range_sq = attack_range * attack_range
        for i, (ax, ay) in enumerate(attackers.ants):
            for j, (dx, dy) in enumerate(defenders.ants):
                if (ax - dx) ** 2 + (ay - dy) ** 2 <= range_sq:
                    engaged_attackers.add(i)
                    engaged_defenders.add(j)
                    if random.random() < kill_prob:
                        remove_indices.append(j)
                    break
        for j in sorted(set(remove_indices), reverse=True):
            defenders.ants.pop(j)
        attackers.engaged.update(engaged_attackers)
        defenders.engaged.update(engaged_defenders)

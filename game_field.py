import pygame

from stage import Stage
from swarm import Swarm
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
        self.swarm_footmen.engaged = set()
        self.swarm_archers.engaged = set()
        self.ai_player.swarm_archers.engaged = set()
        self.ai_player.swarm_footmen.engaged = set()

        # Flag icons
        for idx, template in enumerate(self.flag_templates):
            temp = template["cls"](None, self.FLAG_COLOR_RED)
            temp.show()
            temp.draw_icon(screen, idx, self.height, idx == self.active_flag_idx)

        # Ant counts
        count_text = self.font.render(
            (
                f"Footmen: {len(self.swarm_footmen.ants)}  "
                f"Archers: {len(self.swarm_archers.ants)}  "
                f"Blue Footmen: {len(self.ai_player.swarm_footmen.ants)}  "
                f"Blue Archers: {len(self.ai_player.swarm_archers.ants)}"
            ),
            True,
            (255, 255, 255),
        )
        text_rect = count_text.get_rect(topright=(self.width - 5, 5))
        screen.blit(count_text, text_rect)

    # ------------------------------------------------------------------
    # Simulation - tick is inherited and propagates to children
    # ------------------------------------------------------------------

from stage import Stage
from swarm import (
    Swarm,
    ATTACK_RANGE,
    ARCHER_ATTACK_RANGE,
    KILL_PROBABILITY,
    ARCHER_KILL_PROBABILITY,
)
from flag import NormalFlag, ArcherFlag
import random

# Simulation runs at 20 ticks per second (see main.py)
TICKS_PER_SECOND = 20.0


class AIPlayer(Stage):
    """Simple AI controller for the blue team."""

    def __init__(self, width, height, num_footmen, num_archers, occupied):
        super().__init__()
        self.width = width
        self.height = height
        self.swarm_footmen = Swarm(
            (0, 255, 255),
            5,
            (0, 255, 255),
            width=width,
            height=height,
            attack_range=ATTACK_RANGE,
            kill_probability=KILL_PROBABILITY,
        )
        self.swarm_archers = Swarm(
            (0, 255, 255),
            6,
            (0, 255, 255),
            shape="semicircle",
            width=width,
            height=height,
            attack_range=ARCHER_ATTACK_RANGE,
            kill_probability=ARCHER_KILL_PROBABILITY,
        )
        self.add_stage(self.swarm_footmen)
        self.add_stage(self.swarm_archers)
        self.swarm_footmen.show()
        self.swarm_archers.show()

        self.swarm_footmen.spawn(
            num_footmen,
            (width * 0.75, width),
            (0, height * 0.25),
            occupied,
        )
        self.swarm_archers.spawn(
            num_archers,
            (width * 0.75, width),
            (height * 0.75, height),
            occupied,
        )

        self.footmen_flag = NormalFlag(
            (random.uniform(0, width), random.uniform(0, height)),
            (0, 255, 255),
        )
        self.archer_flag = ArcherFlag(None, (0, 255, 255))
        self.footmen_flag.show()
        self.archer_flag.show()
        self.swarm_footmen.queue.add_flag(self.footmen_flag)
        self.swarm_archers.queue.add_flag(self.archer_flag)

        self._time_since_move = 0.0  # seconds since last flag move
        self._next_move_delay = random.uniform(5, 15)  # seconds
        self._next_flag_idx = 1

    def _tick(self, dt):
        # Convert the tick-based ``dt`` to seconds
        dt_seconds = dt / TICKS_PER_SECOND
        self._time_since_move += dt_seconds
        if self._time_since_move >= self._next_move_delay:
            pos = (
                random.uniform(0, self.width),
                random.uniform(0, self.height),
            )
            if self._next_flag_idx == 0:
                self.footmen_flag.pos = pos
            else:
                self.archer_flag.pos = pos
            self._next_flag_idx = 1 - self._next_flag_idx
            self._time_since_move = 0.0
            self._next_move_delay = random.uniform(5, 15)


from player import Player
from swarm import (
    Swarm,
    SwarmFootmen,
    SwarmArchers,
    SwarmCannon,
    ATTACK_RANGE,
    ARCHER_ATTACK_RANGE,
    KILL_PROBABILITY,
    ARCHER_KILL_PROBABILITY,
)


class HumanPlayer(Player):
    """Player controlled by the user."""

    def __init__(
        self,
        width,
        height,
        num_footmen,
        num_archers,
        occupied,
        group_footmen=1,
        group_archers=2,
        group_cannon=3,
        num_cannons=3,
        color=(255, 0, 0),
        flag_color=(255, 100, 100),
    ):
        super().__init__()
        self.width = width
        self.height = height

        self.swarm_footmen = SwarmFootmen(
            color,
            group_footmen,
            flag_color,
            width=width,
            height=height,
            attack_range=ATTACK_RANGE,
            kill_probability=KILL_PROBABILITY,
        )
        self.swarm_archers = SwarmArchers(
            color,
            group_archers,
            flag_color,
            width=width,
            height=height,
            attack_range=ARCHER_ATTACK_RANGE,
            kill_probability=ARCHER_KILL_PROBABILITY,
        )
        self.swarm_cannon = SwarmCannon(
            color,
            group_cannon,
            flag_color,
            width=width,
            height=height,
            owner=self,
        )

        self.swarm_footmen.owner = self
        self.swarm_archers.owner = self
        # SwarmCannon owner already set in constructor

        self.add_stage(self.swarm_footmen)
        self.add_stage(self.swarm_archers)
        self.add_stage(self.swarm_cannon)
        self.swarm_footmen.show()
        self.swarm_archers.show()
        self.swarm_cannon.show()

        self.swarm_footmen.spawn(
            num_footmen,
            (0, width * 0.25),
            (height * 0.75, height),
            occupied,
        )
        self.swarm_archers.spawn(
            num_archers,
            (0, width * 0.25),
            (0, height * 0.25),
            occupied,
        )
        self.swarm_cannon.spawn(
            num_cannons,
            (0, width * 0.05),
            (height * 0.45, height * 0.55),
            occupied,
        )

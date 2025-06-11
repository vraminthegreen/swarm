from stage import Stage
class Player(Stage):

    """Base class for entities that control swarms."""

    def __init__(self):
        super().__init__()
        self.enemies = []

    # ------------------------------------------------------------------
    # Ownership helpers
    # ------------------------------------------------------------------
    def isOwner(self, stage):
        """Return True if ``stage`` belongs to this player."""
        if stage is self:
            return True
        return getattr(stage, "owner", None) is self

    def isEnemy(self, stage):
        """Return True if ``stage`` is owned by any of this player's enemies."""
        return any(enemy.isOwner(stage) for enemy in self.enemies)

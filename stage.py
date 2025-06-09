class Stage:
    """Basic stage element with visibility control."""

    def __init__(self):
        self._visible = False

    def add(self):
        """Make the stage element visible."""
        self._visible = True

    def remove(self):
        """Hide the stage element."""
        self._visible = False

    def draw(self, screen):
        """Draw the element if visible."""
        if self._visible:
            self._draw(screen)

    def _draw(self, screen):
        """Subclasses must implement actual drawing logic."""
        raise NotImplementedError

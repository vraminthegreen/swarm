class Stage:
    """Basic stage element that can contain child stages."""

    def __init__(self):
        self._visible = False
        self._children = []

    # ------------------------------------------------------------------
    # Tree management
    # ------------------------------------------------------------------
    def add_stage(self, child):
        """Attach a child stage to this stage."""
        if not isinstance(child, Stage):
            raise TypeError("child must be a Stage instance")
        self._children.append(child)

    def remove_stage(self, child):
        """Detach a child stage from this stage."""
        self._children.remove(child)

    # ------------------------------------------------------------------
    # Visibility control
    # ------------------------------------------------------------------
    def show(self):
        """Make the stage element visible and show all children."""
        self._visible = True
        for child in self._children:
            child.show()

    def hide(self):
        """Hide the stage element and all children."""
        self._visible = False
        for child in self._children:
            child.hide()

    def draw(self, screen):
        """Draw the element and its children if visible."""
        if self._visible:
            self._draw(screen)
            for child in self._children:
                child.draw(screen)

    def _draw(self, screen):
        """Subclasses must implement actual drawing logic."""
        raise NotImplementedError

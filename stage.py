class Stage:
    """Basic stage element that can contain child stages."""

    def __init__(self):
        self._visible = False
        self._children = []
        self._parent = None

    # ------------------------------------------------------------------
    # Tree management
    # ------------------------------------------------------------------
    def add_stage(self, child):
        """Attach a child stage to this stage."""
        if not isinstance(child, Stage):
            raise TypeError("child must be a Stage instance")
        self._children.append(child)
        child._parent = self

    def remove_stage(self, child):
        """Detach a child stage from this stage."""
        self._children.remove(child)
        child._parent = None

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

    def handleEvent(self, event):
        """Process an event, returning True if it was consumed."""
        if not self._visible:
            return False
        for child in list(self._children):
            if child.handleEvent(event):
                return True
        if self._handle_event(event):
            return True
        return False

    def _handle_event(self, event):
        """Subclasses override to handle events."""
        return False

    def _draw(self, screen):
        """Draw this stage element. Subclasses may override."""
        pass

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------
    def tick(self, dt):
        """Advance the simulation by ``dt`` time units and propagate to children."""
        self._tick(dt)
        for child in self._children:
            child.tick(dt)
        if self._parent is None:
            self._resolve_collisions()

    def _tick(self, dt):
        """Subclasses override to update internal state."""
        pass

    # ------------------------------------------------------------------
    # Positioning
    # ------------------------------------------------------------------
    def getPosition(self):
        """Return the (x, y) position of this stage element if available."""
        return None

    def getCollisionShape(self):
        """Return the collision shape of this element if available."""
        return None

    def onCollision(self, stage):
        """Handle a collision with ``stage``. Subclasses may override."""
        pass

    # ------------------------------------------------------------------
    # Collision handling helpers
    # ------------------------------------------------------------------
    def _collect_collision_stages(self):
        stages = []
        if self.getCollisionShape() is not None:
            stages.append(self)
        for child in self._children:
            stages.extend(child._collect_collision_stages())
        return stages

    def _resolve_collisions(self):
        stages = self._collect_collision_stages()
        for i in range(len(stages)):
            for j in range(i + 1, len(stages)):
                s1 = stages[i]
                s2 = stages[j]
                shape1 = s1.getCollisionShape()
                shape2 = s2.getCollisionShape()
                if shape1 and shape2 and shape1.collidesWith(shape2):
                    s1.onCollision(s2)
                    s2.onCollision(s1)

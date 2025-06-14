"""Grid based flow field pathfinding without external dependencies."""

from collections import deque
from typing import Iterable, Tuple
import math

from collision_shape import CollisionShape


class FlowField:
    """Compute a flow field towards a goal avoiding obstacles."""

    DIRECTIONS = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]

    def __init__(self, width: int, height: int, cell_size: int = 1):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_w = max(1, (width + cell_size - 1) // cell_size)
        self.grid_h = max(1, (height + cell_size - 1) // cell_size)

        nan = float("nan")
        self._vectors = [
            [[nan, nan] for _ in range(self.grid_w)] for _ in range(self.grid_h)
        ]

        # Cost field initialised to ``inf``
        inf = float("inf")
        self.costs = [
            [inf for _ in range(self.grid_w)] for _ in range(self.grid_h)
        ]
        self.INF = inf

        self.goal = None
        self.max_distance = 0.0

    def _cell_center(self, x: int, y: int) -> Tuple[float, float]:
        return (
            x * self.cell_size + self.cell_size / 2,
            y * self.cell_size + self.cell_size / 2,
        )

    # ------------------------------------------------------------------
    # Field computation
    # ------------------------------------------------------------------
    def compute(
        self,
        goal: Tuple[float, float],
        obstacles: Iterable[CollisionShape],
        margin: float = 0.0,
    ):
        """Compute the cost field towards ``goal`` avoiding ``obstacles``.

        ``margin`` expands the radius of each obstacle by the given amount
        during computation.
        """
        print("flow_field compute")

        self.goal = goal

        blocked = [[False for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        half = self.cell_size / 2
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                center = self._cell_center(x, y)
                cell_shape = CollisionShape(center, half)
                for shape in obstacles:
                    inflated = CollisionShape(shape.center, shape.radius + margin)
                    if cell_shape.collidesWith(inflated):
                        blocked[y][x] = True
                        break

        costs = [[self.INF for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        gx = min(self.grid_w - 1, max(0, int(goal[0] / self.cell_size)))
        gy = min(self.grid_h - 1, max(0, int(goal[1] / self.cell_size)))
        if blocked[gy][gx]:
            # goal blocked, nothing reachable
            self.costs = costs
            for y in range(self.grid_h):
                for x in range(self.grid_w):
                    self._vectors[y][x][0] = math.nan
                    self._vectors[y][x][1] = math.nan
            self.max_distance = 0.0
            return

        costs[gy][gx] = 0.0
        q = deque([(gx, gy)])

        while q:
            cx, cy = q.popleft()
            base = costs[cy][cx]
            for dx, dy in self.DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h and not blocked[ny][nx]:
                    new_cost = base + (dx * dx + dy * dy) ** 0.5
                    if new_cost < costs[ny][nx]:
                        costs[ny][nx] = new_cost
                        q.append((nx, ny))

        self.costs = costs
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                self._vectors[y][x][0] = math.nan
                self._vectors[y][x][1] = math.nan

        finite = [v for row in costs for v in row if math.isfinite(v)]
        self.max_distance = max(finite) if finite else 0.0

    def get_vector(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Return the flow vector for ``pos``."""
        if self.goal is None:
            return 0.0, 0.0
        x = min(self.grid_w - 1, max(0, int(pos[0] / self.cell_size)))
        y = min(self.grid_h - 1, max(0, int(pos[1] / self.cell_size)))
        if math.isnan(self._vectors[y][x][0]):
            self._vectors[y][x] = self._compute_vector(x, y)
        return tuple(self._vectors[y][x])

    def get_distance(self, pos: Tuple[float, float]) -> float:
        """Return the cost distance for ``pos`` or ``INF`` if unreachable."""
        if self.goal is None:
            return self.INF
        x = min(self.grid_w - 1, max(0, int(pos[0] / self.cell_size)))
        y = min(self.grid_h - 1, max(0, int(pos[1] / self.cell_size)))
        value = self.costs[y][x]
        return float(value) if math.isfinite(value) else self.INF

    # ------------------------------------------------------------------
    # Gradient helpers
    # ------------------------------------------------------------------
    def _compute_vector(self, x: int, y: int) -> Tuple[float, float]:
        """Compute normalized gradient at cell ``(x, y)``."""
        if not math.isfinite(self.costs[y][x]):
            return (0.0, 0.0)

        best_cost = self.costs[y][x]
        best = (0, 0)
        for dx, dy in self.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h:
                c = self.costs[ny][nx]
                if c < best_cost:
                    best_cost = c
                    best = (dx, dy)

        if best == (0, 0):
            return (0.0, 0.0)

        length = (best[0] ** 2 + best[1] ** 2) ** 0.5
        if length == 0:
            return (0.0, 0.0)
        return (best[0] / length, best[1] / length)

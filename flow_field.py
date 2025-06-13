"""Simple grid based flow field pathfinding."""

from collections import deque
from typing import Iterable, Tuple

from collision_shape import CollisionShape


class FlowField:
    """Compute a basic flow field guiding units towards a goal."""

    def __init__(self, width: int, height: int, cell_size: int = 20):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_w = max(1, width // cell_size)
        self.grid_h = max(1, height // cell_size)
        self._vectors = [[(0.0, 0.0) for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self.goal = None
        self.distances = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self.max_distance = 0
        self.INF = 10 ** 9

    def _cell_center(self, x: int, y: int) -> Tuple[float, float]:
        return (
            x * self.cell_size + self.cell_size / 2,
            y * self.cell_size + self.cell_size / 2,
        )

    def compute(self, goal: Tuple[float, float], obstacles: Iterable[CollisionShape]):
        """Generate flow vectors towards ``goal`` avoiding ``obstacles``."""
        self.goal = goal
        # Mark impassable cells
        blocked = [[False for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        half = self.cell_size / 2
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                center = self._cell_center(x, y)
                cell_shape = CollisionShape(center, half)
                for shape in obstacles:
                    if cell_shape.collidesWith(shape):
                        blocked[y][x] = True
                        break
        # BFS distance from goal
        INF = self.INF
        dist = [[INF for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        gx = min(self.grid_w - 1, max(0, int(goal[0] / self.cell_size)))
        gy = min(self.grid_h - 1, max(0, int(goal[1] / self.cell_size)))
        if blocked[gy][gx]:
            # goal blocked, vectors remain zero
            self._vectors = [[(0.0, 0.0) for _ in range(self.grid_w)] for _ in range(self.grid_h)]
            self.distances = dist
            self.max_distance = 0
            return
        dist[gy][gx] = 0
        q = deque([(gx, gy)])
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        while q:
            cx, cy = q.popleft()
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h and not blocked[ny][nx]:
                    if dist[ny][nx] > dist[cy][cx] + 1:
                        dist[ny][nx] = dist[cy][cx] + 1
                        q.append((nx, ny))
        # compute vectors pointing to neighbour with lower distance
        vectors = [[(0.0, 0.0) for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if dist[y][x] == INF:
                    continue
                best = (x, y)
                best_d = dist[y][x]
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h:
                        if dist[ny][nx] < best_d:
                            best_d = dist[ny][nx]
                            best = (nx, ny)
                if best != (x, y):
                    vx = best[0] - x
                    vy = best[1] - y
                    length = (vx ** 2 + vy ** 2) ** 0.5
                    if length:
                        vectors[y][x] = (vx / length, vy / length)
        self._vectors = vectors
        self.distances = dist
        self.max_distance = max(
            (d for row in dist for d in row if d != INF),
            default=0,
        )

    def get_vector(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Return the flow vector for ``pos``."""
        if self.goal is None:
            return 0.0, 0.0
        x = min(self.grid_w - 1, max(0, int(pos[0] / self.cell_size)))
        y = min(self.grid_h - 1, max(0, int(pos[1] / self.cell_size)))
        return self._vectors[y][x]

    def get_distance(self, pos: Tuple[float, float]) -> int:
        """Return the BFS distance for ``pos`` or ``INF`` if unreachable."""
        if self.goal is None:
            return self.INF
        x = min(self.grid_w - 1, max(0, int(pos[0] / self.cell_size)))
        y = min(self.grid_h - 1, max(0, int(pos[1] / self.cell_size)))
        return self.distances[y][x]

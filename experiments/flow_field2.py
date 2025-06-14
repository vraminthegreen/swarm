#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from collections import deque

SIZE = 100
OBSTACLE_COUNT = 8
np.random.seed(42)

# --- 1. GENERUJEMY LOSOWE PRZESZKODY (wielkości, kształty) ---

obstacle_map = np.zeros((SIZE, SIZE), dtype=bool)

def random_ellipse(center, axes, angle, shape):
    """Zwraca maskę elipsy/okręgu na zadanym polu."""
    Y, X = np.ogrid[:shape[0], :shape[1]]
    cy, cx = center
    ay, ax = axes
    angle = np.deg2rad(angle)
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    x_shift = X - cx
    y_shift = Y - cy
    x_rot = x_shift * cos_a + y_shift * sin_a
    y_rot = -x_shift * sin_a + y_shift * cos_a
    return (x_rot/ax)**2 + (y_rot/ay)**2 <= 1

for _ in range(OBSTACLE_COUNT):
    # losowy kształt: 0=okrąg/owal, 1=prostokąt
    shape_type = np.random.choice([0, 1])
    cy, cx = np.random.randint(10, SIZE-10, size=2)
    if shape_type == 0:  # owal/okrąg
        ax, ay = np.random.randint(6, 16), np.random.randint(6, 20)
        angle = np.random.randint(0, 180)
        mask = random_ellipse((cy, cx), (ay, ax), angle, obstacle_map.shape)
        obstacle_map |= mask
    else:  # prostokąt
        h, w = np.random.randint(8, 20), np.random.randint(8, 20)
        y1 = max(0, cy - h//2)
        y2 = min(SIZE, cy + h//2)
        x1 = max(0, cx - w//2)
        x2 = min(SIZE, cx + w//2)
        obstacle_map[y1:y2, x1:x2] = True

# 2. LOSUJEMY PUNKTY STARTU I METY (unika przeszkód)
def random_free_point():
    while True:
        pt = tuple(np.random.randint(0, SIZE, size=2))
        if not obstacle_map[pt]:
            return pt

start = random_free_point()
goal = random_free_point()
while goal == start:
    goal = random_free_point()

# 3. POLICZ POLE KOSZTÓW OD METY (BFS, 8 kierunków)
def compute_cost_field(obstacle_map, goal):
    cost_field = np.full(obstacle_map.shape, np.inf)
    visited = np.zeros_like(obstacle_map, dtype=bool)
    q = deque()
    gx, gy = goal
    cost_field[gx, gy] = 0
    q.append((gx, gy))
    moves = [(-1,0), (1,0), (0,-1), (0,1),
             (-1,-1), (-1,1), (1,-1), (1,1)]
    while q:
        x, y = q.popleft()
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE:
                if not obstacle_map[nx, ny] and not visited[nx, ny]:
                    # Dla diagonali koszt √2, dla reszty 1
                    dist = np.hypot(dx, dy)
                    cost = cost_field[x, y] + dist
                    if cost < cost_field[nx, ny]:
                        cost_field[nx, ny] = cost
                        visited[nx, ny] = True
                        q.append((nx, ny))
    return cost_field

cost_field = compute_cost_field(obstacle_map, goal)

# 4. LENIWE LICZENIE FLOW FIELDU (CACHE, 8 kierunków)
class LazyFlowField:
    def __init__(self, cost_field):
        self.cost_field = cost_field
        self.cache = {}

    def get_gradient(self, x, y):
        if (x, y) in self.cache:
            return self.cache[(x, y)]
        h, w = self.cost_field.shape
        best_dir = (0, 0)
        best_cost = self.cost_field[x, y]
        moves = [(-1,0), (1,0), (0,-1), (0,1),
                 (-1,-1), (-1,1), (1,-1), (1,1)]
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if 0 <= nx < h and 0 <= ny < w:
                if self.cost_field[nx, ny] < best_cost:
                    best_cost = self.cost_field[nx, ny]
                    best_dir = (dx, dy)
        self.cache[(x, y)] = best_dir
        return best_dir

flow_field = LazyFlowField(cost_field)

# 5. SZUKAJ NAJKRÓTSZEJ ŚCIEŻKI (8 kierunków)
def find_path(flow_field, start, goal, max_steps=SIZE*SIZE):
    path = [start]
    x, y = start
    for _ in range(max_steps):
        if (x, y) == goal:
            break
        dx, dy = flow_field.get_gradient(x, y)
        if (dx, dy) == (0, 0):
            break
        x, y = x+dx, y+dy
        path.append((x, y))
        if len(path) > 1 and path[-1] == path[-2]:
            break
    return path

path = find_path(flow_field, start, goal)

# 6. RYSUJEMY
img = np.clip((cost_field - np.nanmin(cost_field)), 0, 50)
img = img / img.max()

plt.imshow(img, cmap='gray', interpolation='nearest', origin='lower')

# Przeszkody (zielone)
obs_x, obs_y = np.where(obstacle_map)
plt.scatter(obs_y, obs_x, c='limegreen', s=8, label='obstacles')

# Początek (czerwony)
plt.scatter(start[1], start[0], c='red', s=70, edgecolors='black', label='start', zorder=5)
# Meta (niebieski)
plt.scatter(goal[1], goal[0], c='blue', s=70, edgecolors='black', label='goal', zorder=5)
# Najkrótsza ścieżka (żółta)
if len(path) > 1:
    path_x, path_y = zip(*path)
    plt.plot(path_y, path_x, c='yellow', lw=2, label='shortest path', zorder=4)

plt.legend(loc='upper right')
plt.title('Flow Field Pathfinding – Obstacles of All Shapes')
plt.axis('off')
plt.tight_layout()
plt.show()


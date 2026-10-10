"""Fixed 10x10 city: obstacles, 4 pickup points, 4 destinations. Coordinates are (x, y)."""
from collections import deque


class CityMap:
    WIDTH = 10
    HEIGHT = 10

    OBSTACLES = {
        (2, 1), (2, 2), (2, 3),
        (5, 0), (5, 1), (5, 2),
        (7, 4), (8, 4),
        (1, 6), (2, 6), (3, 6),
        (5, 7), (5, 8), (6, 8), (8, 7),
    }
    PICKUP_POINTS = [(0, 0), (9, 0), (0, 9), (9, 9)]
    DESTINATIONS = [(4, 0), (9, 5), (3, 9), (4, 4)]

    def __init__(self):
        self._validate()

    def in_bounds(self, x, y):
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def is_obstacle(self, x, y):
        return (x, y) in self.OBSTACLES

    def is_free(self, x, y):
        return self.in_bounds(x, y) and not self.is_obstacle(x, y)

    def is_reachable(self, start, goal):
        """BFS: is there a path between two cells?"""
        seen, queue = {start}, deque([start])
        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                return True
            for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                n = (x + dx, y + dy)
                if self.is_free(*n) and n not in seen:
                    seen.add(n)
                    queue.append(n)
        return False

    def _validate(self):
        pts = self.PICKUP_POINTS + self.DESTINATIONS
        for p in pts:
            if not self.is_free(*p):
                raise ValueError(f"task point on obstacle/outside map: {p}")
        for a in pts:
            for b in pts:
                if not self.is_reachable(a, b):
                    raise ValueError(f"no path between {a} and {b}")

    def print_map(self, taxi=None):
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                p = (x, y)
                row.append("T" if p == taxi else "P" if p in self.PICKUP_POINTS
                           else "D" if p in self.DESTINATIONS
                           else "#" if p in self.OBSTACLES else ".")
            print(" ".join(row))

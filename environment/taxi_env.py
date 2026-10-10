"""SmartTaxi environment: state = (x, y, pickup_id, dest_id, passenger_on_board)."""
import numpy as np

from environment.city_map import CityMap

# Reward design (see presentation, slide "Reward function")
R_DELIVER = 100      # drop passenger at the right destination
R_PICKUP = 15        # pick passenger at the right place
R_STEP = -1          # every step (pushes for short trips)
R_WRONG = -10        # illegal pickup / drop
R_WALL = -20         # bump into an obstacle / map edge
R_TIMEOUT = -15      # episode ended without delivery


class SmartTaxiEnv:
    # 0 up, 1 down, 2 right, 3 left, 4 pickup, 5 drop-off
    MOVES = {0: (0, -1), 1: (0, 1), 2: (1, 0), 3: (-1, 0)}
    ACTION_NAMES = ["Up", "Down", "Right", "Left", "Pickup", "Dropoff"]
    NUM_ACTIONS = 6

    def __init__(self, max_steps=150, seed=None):
        self.city = CityMap()
        self.max_steps = max_steps
        self.rng = np.random.default_rng(seed)
        c = self.city
        self.num_states = (c.WIDTH * c.HEIGHT * len(c.PICKUP_POINTS)
                           * len(c.DESTINATIONS) * 2)  # 10*10*4*4*2 = 3200
        self.reset()

    # ---- state encoding: (x,y,p,d,b) <-> integer in [0, 3200) ----
    def encode(self, x, y, p, d, b):
        return (((x * self.city.HEIGHT + y) * 4 + p) * 4 + d) * 2 + b

    def decode(self, s):
        s, b = divmod(s, 2)
        s, d = divmod(s, 4)
        s, p = divmod(s, 4)
        x, y = divmod(s, self.city.HEIGHT)
        return x, y, p, d, b

    @property
    def state(self):
        return self.encode(*self.taxi, self.pickup, self.dest, self.onboard)

    def reset(self, pickup=None, dest=None, start=None):
        free = [(x, y) for x in range(self.city.WIDTH) for y in range(self.city.HEIGHT)
                if self.city.is_free(x, y)]
        self.taxi = start or free[self.rng.integers(len(free))]
        self.pickup = int(self.rng.integers(4)) if pickup is None else pickup
        self.dest = int(self.rng.integers(4)) if dest is None else dest
        self.onboard = 0
        self.steps = self.collisions = 0
        self.done = self.success = False
        return self.state

    def step(self, action):
        """Returns (next_state, reward, terminated, truncated, info)."""
        reward, terminated = R_STEP, False
        self.steps += 1
        if action in self.MOVES:
            dx, dy = self.MOVES[action]
            nx, ny = self.taxi[0] + dx, self.taxi[1] + dy
            if self.city.is_free(nx, ny):
                self.taxi = (nx, ny)
            else:                       # blocked: stay in place + penalty
                reward += R_WALL
                self.collisions += 1
        elif action == 4:
            if not self.onboard and self.taxi == self.city.PICKUP_POINTS[self.pickup]:
                self.onboard, reward = 1, reward + R_PICKUP
            else:
                reward += R_WRONG
        else:
            if self.onboard and self.taxi == self.city.DESTINATIONS[self.dest]:
                reward += R_DELIVER
                terminated = self.success = True
            else:
                reward += R_WRONG
        truncated = (not terminated) and self.steps >= self.max_steps
        if truncated:
            reward += R_TIMEOUT
        self.done = terminated or truncated
        info = {"steps": self.steps, "success": self.success,
                "collisions": self.collisions, "taxi_position": self.taxi}
        return self.state, reward, terminated, truncated, info

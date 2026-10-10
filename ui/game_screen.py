"""Pygame viewer: watch the trained agent (or drive manually) with a stats side panel.

Keys: SPACE run/pause AI | N one AI step | R new task | arrows move | P pickup | D drop | ESC quit
"""
import sys
from pathlib import Path

import pygame

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv

CELL, MAP_X, MAP_Y, PANEL_W = 56, 20, 20, 300
BG, ROAD, WALL, GRID = (245, 246, 248), (226, 229, 234), (60, 66, 78), (205, 209, 216)
GREEN, BLUE, TAXI, TEXT, RED = (46, 160, 90), (31, 111, 139), (240, 180, 30), (30, 34, 42), (200, 60, 50)
KEYS = {pygame.K_UP: 0, pygame.K_DOWN: 1, pygame.K_RIGHT: 2, pygame.K_LEFT: 3,
        pygame.K_p: 4, pygame.K_d: 5}


class SmartTaxiGame:
    def __init__(self, q_path=None):
        pygame.init()
        self.env = SmartTaxiEnv()
        c = self.env.city
        self.screen = pygame.display.set_mode((MAP_X * 2 + c.WIDTH * CELL + PANEL_W, MAP_Y * 2 + c.HEIGHT * CELL))
        pygame.display.set_caption("SmartTaxi RL")
        self.font, self.small = pygame.font.SysFont(None, 28), pygame.font.SysFont(None, 20)
        self.agent = QLearningAgent(self.env.num_states, self.env.NUM_ACTIONS, epsilon=0.0)
        q_path = Path(q_path or Path(__file__).resolve().parents[1] / "results" / "q_table.npz")
        self.has_model = q_path.exists()
        if self.has_model:
            self.agent.load(q_path)
        self.running_ai, self.total, self.last = False, 0.0, ""
        self.trips = self.wins = 0
        self.env.reset()

    def text(self, s, x, y, font=None, color=TEXT):
        self.screen.blit((font or self.font).render(str(s), True, color), (x, y))

    def cell_center(self, pos):
        return MAP_X + pos[0] * CELL + CELL // 2, MAP_Y + pos[1] * CELL + CELL // 2

    def draw(self):
        e, c = self.env, self.env.city
        self.screen.fill(BG)
        for y in range(c.HEIGHT):
            for x in range(c.WIDTH):
                r = pygame.Rect(MAP_X + x * CELL, MAP_Y + y * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, WALL if c.is_obstacle(x, y) else ROAD, r)
                pygame.draw.rect(self.screen, GRID, r, 1)
        for i, p in enumerate(c.PICKUP_POINTS):
            col = GREEN if (i == e.pickup and not e.onboard) else (150, 200, 170)
            pygame.draw.circle(self.screen, col, self.cell_center(p), 16)
            self.text(f"P{i}", self.cell_center(p)[0] - 9, self.cell_center(p)[1] - 7, self.small, (255, 255, 255))
        for i, p in enumerate(c.DESTINATIONS):
            col = BLUE if i == e.dest else (150, 185, 200)
            r = pygame.Rect(0, 0, 30, 30); r.center = self.cell_center(p)
            pygame.draw.rect(self.screen, col, r, border_radius=6)
            self.text(f"D{i}", r.x + 6, r.y + 8, self.small, (255, 255, 255))
        r = pygame.Rect(0, 0, 34, 24); r.center = self.cell_center(e.taxi)
        pygame.draw.rect(self.screen, TAXI, r, border_radius=8)
        pygame.draw.rect(self.screen, TEXT, r, 2, border_radius=8)
        if e.onboard:
            pygame.draw.circle(self.screen, RED, r.center, 5)
        px = MAP_X * 2 + c.WIDTH * CELL
        status = "Delivered!" if e.success else ("Timeout" if e.done else
                 "Driving to destination" if e.onboard else "Going to passenger")
        lines = [("SmartTaxi RL", self.font), (f"Task: P{e.pickup} -> D{e.dest}", self.small),
                 (f"Status: {status}", self.small), (f"Steps: {e.steps}", self.small),
                 (f"Reward: {self.total:.0f}", self.small), (f"Wall hits: {e.collisions}", self.small),
                 (f"Trips: {self.trips}  Delivered: {self.wins}", self.small),
                 (f"Last action: {self.last}", self.small)]
        for i, (s, f) in enumerate(lines):
            self.text(s, px + 10, 20 + i * 32, f)
        mode = "AI running" if self.running_ai else "paused"
        self.text(f"Mode: {mode}" + ("" if self.has_model else "  (no model: run train)"), px + 10, 300, self.small)
        for i, s in enumerate(["SPACE run/pause AI", "N one AI step", "R new task",
                               "Arrows move, P pickup, D drop"]):
            self.text(s, px + 10, 340 + i * 24, self.small, (90, 96, 108))
        # Q-values of the current state: what the agent "thinks"
        q = self.agent.q_table[e.state]
        for i, name in enumerate(e.ACTION_NAMES):
            self.text(f"Q[{name}] = {q[i]:6.1f}", px + 10, 450 + i * 20, self.small, BLUE if q[i] == q.max() else TEXT)

    def act(self, a):
        if self.env.done:
            return
        _, r, term, trunc, _ = self.env.step(a)
        self.total += r
        self.last = self.env.ACTION_NAMES[a]
        if term or trunc:
            self.trips += 1
            self.wins += int(term)

    def new_task(self):
        self.env.reset(); self.total = 0.0; self.last = ""

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE: self.running_ai = not self.running_ai
                    elif ev.key == pygame.K_r: self.new_task()
                    elif ev.key == pygame.K_n: self.act(self.agent.choose_action(self.env.state, explore=False))
                    elif ev.key in KEYS: self.act(KEYS[ev.key])
            if self.running_ai:
                if self.env.done:
                    pygame.time.wait(500); self.new_task()
                else:
                    self.act(self.agent.choose_action(self.env.state, explore=False))
            self.draw(); pygame.display.flip(); clock.tick(8)

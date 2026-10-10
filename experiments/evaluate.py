"""Greedy Q agent vs random agent on identical tasks (same seed per episode)."""
import argparse
import csv
from pathlib import Path

import numpy as np

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv

RESULTS = Path(__file__).resolve().parents[1] / "results"


def run_episode(env, seed, policy):
    env.rng = np.random.default_rng(seed)
    s, total = env.reset(), 0.0
    while True:
        s, r, term, trunc, info = env.step(policy(s))
        total += r
        if term or trunc:
            return total, info


def evaluate(episodes=500, q_path=RESULTS / "q_table.npz"):
    env = SmartTaxiEnv()
    agent = QLearningAgent(env.num_states, env.NUM_ACTIONS)
    agent.load(q_path)
    rnd = np.random.default_rng(0)
    pols = {"random": lambda s: int(rnd.integers(env.NUM_ACTIONS)),
            "q": lambda s: agent.choose_action(s, explore=False)}
    rows = []
    for i in range(episodes):
        row = {"episode": i + 1}
        for name, pol in pols.items():
            total, info = run_episode(env, 10_000 + i, pol)
            row.update({f"{name}_reward": total, f"{name}_steps": info["steps"],
                        f"{name}_success": int(info["success"]),
                        f"{name}_collisions": info["collisions"]})
        rows.append(row)
    with (RESULTS / "evaluation_results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for name in ("random", "q"):
        m = lambda k: np.mean([r[f"{name}_{k}"] for r in rows])
        print(f"{name:7s} success {m('success'):.1%} | reward {m('reward'):8.2f} | "
              f"steps {m('steps'):6.1f} | collisions {m('collisions'):5.2f}")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=500)
    evaluate(ap.parse_args().episodes)

"""Traces used in the presentation: (1) one greedy episode with the trained table,
(2) how Q values appear and spread backwards when the same route is replayed from a zero table,
(3) epsilon after N episodes."""
import json
from pathlib import Path

import numpy as np

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv

RESULTS = Path(__file__).resolve().parents[1] / "results"


def main():
    env = SmartTaxiEnv()
    trained = QLearningAgent(env.num_states, env.NUM_ACTIONS)
    trained.load(RESULTS / "q_table.npz")

    # (1) greedy episode: passenger at P0 (0,0), destination D0 (4,0), taxi starts at (1,0)
    s = env.reset(pickup=0, dest=0, start=(1, 0))
    steps, actions = [], []
    while not env.done:
        a = trained.choose_action(s, explore=False)
        before = env.taxi
        q = trained.q_table[s].copy()
        s2, r, *_ = env.step(a)
        steps.append({"step": env.steps, "before": before, "after": env.taxi, "action": int(a),
                      "reward": r, "q_chosen": float(q[a]), "state": int(s),
                      "onboard": int(env.onboard)})
        actions.append(a)
        s = s2
    print("greedy episode:")
    for t in steps:
        print(t)

    # (2) replay the same route from an all-zero table, same order as a real episode
    zero = QLearningAgent(env.num_states, env.NUM_ACTIONS, alpha=0.1, gamma=0.95, epsilon=0.0)
    snapshots = {}
    watch = [1, 2, 3, 10, 50]
    for p in range(1, max(watch) + 1):
        s = env.reset(pickup=0, dest=0, start=(1, 0))
        for a in actions:
            s2, r, term, trunc, _ = env.step(a)
            zero.update(s, a, r, s2, term)
            s = s2
        if p in watch:
            snapshots[p] = [round(float(zero.q_table[t["state"], t["action"]]), 2) for t in steps]
    print("\nQ along the route after passes:")
    for p, v in snapshots.items():
        print(p, v)

    # (3) epsilon schedule
    eps = {n: round(max(0.05, 0.999 ** n), 3) for n in (0, 500, 1000, 2000, 3000, 5000)}
    print("\nepsilon:", eps)

    (RESULTS / "trace.json").write_text(json.dumps(
        {"steps": steps, "snapshots": snapshots, "epsilon": eps,
         "action_names": SmartTaxiEnv.ACTION_NAMES}))


if __name__ == "__main__":
    main()

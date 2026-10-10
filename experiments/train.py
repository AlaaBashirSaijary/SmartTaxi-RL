"""Train the agent; log every episode + the Q-value of a tracked (state, action) pair."""
import argparse
import csv
from pathlib import Path

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv

RESULTS = Path(__file__).resolve().parents[1] / "results"


def train(episodes=30000, seed=42, alpha=0.1, gamma=0.95, epsilon_decay=0.999,
          tag="", save=True, on_progress=None):
    RESULTS.mkdir(exist_ok=True)
    env = SmartTaxiEnv(seed=seed)
    agent = QLearningAgent(env.num_states, env.NUM_ACTIONS, alpha=alpha, gamma=gamma,
                           epsilon_decay=epsilon_decay, seed=seed)
    # Tracked pair for the "how Q changes" plot: taxi at pickup P0 (0,0), passenger P0->D0,
    # not yet on board; action 4 = Pickup.
    tracked_s, tracked_a = env.encode(0, 0, 0, 0, 0), 4
    rows = []
    for ep in range(1, episodes + 1):
        s = env.reset()
        total = 0.0
        while True:
            a = agent.choose_action(s)
            s2, r, term, trunc, info = env.step(a)
            agent.update(s, a, r, s2, term)      # bootstrap on timeout, not on delivery
            s, total = s2, total + r
            if term or trunc:
                break
        agent.decay_epsilon()
        rows.append({"episode": ep, "reward": total, "steps": info["steps"],
                     "success": int(info["success"]), "collisions": info["collisions"],
                     "epsilon": round(agent.epsilon, 4),
                     "q_tracked": agent.q_table[tracked_s, tracked_a],
                     "q_mean_max": agent.q_table.max(axis=1).mean()})
        if on_progress and ep % 250 == 0:
            on_progress(ep, episodes)
        if ep % max(1, episodes // 10) == 0:
            last = rows[-200:]
            print(f"ep {ep:6d} | eps {agent.epsilon:.3f} | "
                  f"success(last200) {sum(x['success'] for x in last)/len(last):.1%} | "
                  f"reward {sum(x['reward'] for x in last)/len(last):7.1f}")
    if save:
        name = f"training_results{tag}.csv"
        with (RESULTS / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        agent.save(RESULTS / f"q_table{tag}.npz")
    return agent, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    train(a.episodes, a.seed)

"""Make all figures used in the report/presentation into results/."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[1] / "results"
BLUE, ORANGE, GRAY = "#1F6F8B", "#E8743B", "#8A8F98"


def smooth(x, w=100):
    return np.convolve(x, np.ones(w) / w, mode="valid")


def style(ax, title, xl, yl):
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.25)


def training():
    df = pd.read_csv(R / "training_results.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(smooth(df.reward), color=BLUE)
    style(ax, "Average reward per episode (window 100)", "Training episode", "Reward")
    fig.tight_layout(); fig.savefig(R / "training_reward.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(smooth(df.success) * 100, color=BLUE, label="Success rate %")
    ax2 = ax.twinx(); ax2.plot(df.epsilon, color=ORANGE, label="epsilon")
    ax2.set_ylabel("epsilon (exploration)"); ax2.spines[["top"]].set_visible(False)
    style(ax, "Success rate and exploration", "Training episode", "Success rate (%)")
    fig.tight_layout(); fig.savefig(R / "training_success.png", dpi=160); plt.close(fig)

    # How one Q-value and the average best-Q change with experience
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(df.episode, df.q_tracked, color=BLUE)
    style(axes[0], "Q(s0, Pickup) over training", "Training episode", "Q value")
    axes[1].plot(df.episode, df.q_mean_max, color=ORANGE)
    style(axes[1], "Mean of max_a Q(s,a) over all states", "Training episode", "Mean max Q")
    fig.tight_layout(); fig.savefig(R / "q_value_growth.png", dpi=160); plt.close(fig)


def comparison():
    df = pd.read_csv(R / "evaluation_results.csv")
    metrics = [("success", "Success rate", 100), ("steps", "Avg steps", 1),
               ("reward", "Avg reward", 1), ("collisions", "Avg wall hits", 1)]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6))
    for ax, (k, t, mult) in zip(axes, metrics):
        vals = [df[f"random_{k}"].mean() * mult, df[f"q_{k}"].mean() * mult]
        bars = ax.bar(["Random", "Q-Learning"], vals, color=[GRAY, BLUE])
        ax.bar_label(bars, fmt="%.1f", fontsize=10)
        ax.set_title(t, fontweight="bold", loc="left"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(R / "agent_comparison.png", dpi=160); plt.close(fig)


def sweep():
    p = R / "sweep.json"
    if not p.exists():
        return
    data = json.loads(p.read_text())
    titles = {"alpha": "Learning rate α", "gamma": "Discount γ", "epsilon_decay": "Epsilon decay"}
    cols = [GRAY, BLUE, ORANGE]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    for ax, (g, items) in zip(axes, data.items()):
        for c, (label, d) in zip(cols, items.items()):
            y = np.array(d["curve_mean"]) * 100
            ax.plot(np.arange(len(y)) * 50 + 100, y, color=c, label=f"{label} ({d['final_mean']:.0%})")
        style(ax, titles[g], "Training episode", "Success rate (%)")
        ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout(); fig.savefig(R / "sweep.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    training(); comparison(); sweep()
    print("figures saved to", R)

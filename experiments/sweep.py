"""Small hyper-parameter study: alpha, gamma, epsilon decay; 3 seeds each."""
import json
from pathlib import Path

import numpy as np

from experiments.train import train

RESULTS = Path(__file__).resolve().parents[1] / "results"
EPISODES, SEEDS, WIN = 6000, (1, 2, 3), 500

CONFIGS = {
    "alpha": [("0.01", dict(alpha=0.01)), ("0.1", dict(alpha=0.1)), ("0.5", dict(alpha=0.5))],
    "gamma": [("0.50", dict(gamma=0.5)), ("0.95", dict(gamma=0.95)), ("0.99", dict(gamma=0.99))],
    "epsilon_decay": [("0.99", dict(epsilon_decay=0.99)), ("0.999", dict(epsilon_decay=0.999)),
                      ("0.9995", dict(epsilon_decay=0.9995))],
}

out = {}
for group, items in CONFIGS.items():
    out[group] = {}
    for label, kw in items:
        curves = []
        for seed in SEEDS:
            _, rows = train(EPISODES, seed=seed, save=False, **kw)
            s = np.array([r["success"] for r in rows], float)
            curves.append(np.convolve(s, np.ones(100) / 100, mode="valid"))
        curves = np.array(curves)
        final = curves[:, -WIN:].mean(axis=1)
        out[group][label] = {"curve_mean": curves.mean(0)[::50].tolist(),
                             "final_mean": float(final.mean()), "final_std": float(final.std())}
        print(f"{group}={label}: final success {final.mean():.1%} ± {final.std():.1%}")
(RESULTS / "sweep.json").write_text(json.dumps(out))

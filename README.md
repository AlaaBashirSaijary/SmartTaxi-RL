# SmartTaxi RL

Tabular Q-Learning on a 10x10 taxi city (Python, NumPy, Pygame). Includes experiments, plots and an Arabic presentation.

```bash
pip install -r requirements.txt
python -m experiments.train          # 30000 episodes -> results/q_table.npz, training_results.csv
python -m experiments.evaluate       # greedy Q agent vs random agent, 500 identical tasks
python -m experiments.sweep          # alpha / gamma / epsilon-decay study (3 seeds)
python -m experiments.plot_results   # figures in results/
python -m experiments.explain_q      # one Q update printed with real numbers
python main.py                       # Pygame viewer (SPACE run, N step, R new task, arrows/P/D manual)
```

Presentation: `presentation/SmartTaxi_RL_Presentation.pptx` (rebuild with `node presentation/build_deck.js`, needs `pptxgenjs`).

## Design
- State `(x, y, pickup, dest, onboard)` -> 10*10*4*4*2 = 3200 states; 6 actions; Q-table 3200x6.
- Update: `Q(s,a) += alpha * (r + gamma * max_a' Q(s',a') - Q(s,a))`, no future term on delivery.
- Rewards: +100 deliver, +15 pickup, -1 step, -10 wrong pickup/drop, -20 wall, -15 timeout (150 steps).
- Defaults: alpha 0.1, gamma 0.95, epsilon 1.0 -> 0.05 (x0.999 per episode).

## Results (this repo's runs)
| | Success | Avg steps | Avg reward | Wall hits |
|---|---|---|---|---|
| Random | 0.8% | 149.6 | -1121 | 23.2 |
| Q-Learning (30k episodes) | 100% | 20.8 | 94.2 | 0 |

With only 10k training episodes the success rate was 95.6% (rarely visited states not yet learned).
Limits: fixed map, static obstacles, grid moves only - simulation result, not evidence of real driving ability.

"""Prints one real Q-Learning update, step by step (used in the presentation)."""
import numpy as np

from agent.q_learning import QLearningAgent
from environment.taxi_env import SmartTaxiEnv

env = SmartTaxiEnv(seed=0)
agent = QLearningAgent(env.num_states, env.NUM_ACTIONS, alpha=0.1, gamma=0.95, epsilon=0.0)

# Taxi stands on pickup P0 = (0,0); passenger waits there, destination D0 = (4,0)
s = env.reset(pickup=0, dest=0, start=(0, 0))
print("state tuple (x,y,p,d,b) =", env.decode(s), "-> integer index", s)
print("\n--- Take the 'Pickup' action 3 times, same state, to see Q move ---")
for visit in range(1, 4):
    env.reset(pickup=0, dest=0, start=(0, 0))
    s = env.state
    a = 4
    s2, r, term, trunc, info = env.step(a)
    old = agent.q_table[s, a]
    # pretend the next state already has a learned value, to show the bootstrap term
    agent.q_table[s2, :] = np.array([0, 0, 0, 0, 0, 0.0]) if visit == 1 else agent.q_table[s2]
    if visit == 1:
        agent.q_table[s2, 2] = 20.0          # assume max_a' Q(s',a') = 20 for the illustration
    best_next = agent.q_table[s2].max()
    target, td = agent.update(s, a, r, s2, term)
    new = agent.q_table[s, a]
    print(f"visit {visit}: r={r}  max Q(s')={best_next:.2f}  target = {r} + 0.95*{best_next:.2f} = {target:.2f}"
          f"  TD error = {target:.2f} - {old:.2f} = {td:.2f}  Q: {old:.2f} -> {new:.2f}")

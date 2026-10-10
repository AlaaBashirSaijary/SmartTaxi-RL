"""Tabular Q-Learning agent with epsilon-greedy exploration."""
from pathlib import Path

import numpy as np


class QLearningAgent:
    def __init__(self, num_states, num_actions, alpha=0.1, gamma=0.95,
                 epsilon=1.0, min_epsilon=0.05, epsilon_decay=0.999, seed=None):
        self.num_actions = num_actions
        self.alpha, self.gamma = alpha, gamma
        self.epsilon, self.min_epsilon, self.epsilon_decay = epsilon, min_epsilon, epsilon_decay
        self.rng = np.random.default_rng(seed)
        self.q_table = np.zeros((num_states, num_actions))   # Q(s,a) = 0 at start

    def choose_action(self, state, explore=True):
        """epsilon-greedy: random with prob. epsilon, otherwise argmax_a Q(s,a)."""
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.num_actions))
        row = self.q_table[state]
        best = np.flatnonzero(row == row.max())           # break ties randomly
        return int(self.rng.choice(best))

    def update(self, s, a, r, s_next, terminated):
        """Q(s,a) <- Q(s,a) + alpha * [ r + gamma*max_a' Q(s',a') - Q(s,a) ]"""
        future = 0.0 if terminated else self.gamma * self.q_table[s_next].max()
        target = r + future
        td_error = target - self.q_table[s, a]
        self.q_table[s, a] += self.alpha * td_error
        return target, td_error

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, q_table=self.q_table, alpha=self.alpha,
                            gamma=self.gamma, epsilon=self.epsilon)

    def load(self, path):
        self.q_table = np.load(path)["q_table"]

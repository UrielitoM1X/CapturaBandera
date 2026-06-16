# --- agent.py ---
import numpy as np
import random
import pickle
from settings import ACTIONS

class QAgent:
    def __init__(self, alpha=0.2, gamma=0.95, eps=1.0, eps_min=0.05, eps_decay=0.9998):
        self.Q = {}
        self.alpha, self.gamma = alpha, gamma
        self.eps, self.eps_min, self.eps_decay = eps, eps_min, eps_decay

    def _row(self, s):
        if s not in self.Q:
            self.Q[s] = np.zeros(len(ACTIONS))
        return self.Q[s]

    def act(self, s, greedy=False):
        row = self._row(s)
        if not greedy and random.random() < self.eps:
            return random.randrange(len(ACTIONS))
        return int(np.argmax(row))

    def learn(self, s, a, r, s2, done):
        row = self._row(s); row2 = self._row(s2)
        target = r + (0 if done else self.gamma * np.max(row2))
        row[a] += self.alpha * (target - row[a])

    def decay(self):
        self.eps = max(self.eps_min, self.eps * self.eps_decay)

    def save(self, path='qagent.pkl'):
        with open(path, 'wb') as f:
            pickle.dump({'Q': self.Q, 'eps': self.eps,
                         'alpha': self.alpha, 'gamma': self.gamma,
                         'eps_min': self.eps_min, 'eps_decay': self.eps_decay}, f)
        print(f'Modelo guardado en {path} | estados: {len(self.Q)}')

    def load(self, path='qagent.pkl'):
        with open(path, 'rb') as f:
            d = pickle.load(f)
        self.Q = d['Q']; self.eps = d.get('eps', 0.05)
        self.alpha = d.get('alpha', self.alpha); self.gamma = d.get('gamma', self.gamma)
        self.eps_min = d.get('eps_min', self.eps_min); self.eps_decay = d.get('eps_decay', self.eps_decay)
        print(f'Modelo cargado de {path} | estados: {len(self.Q)}')
        return self
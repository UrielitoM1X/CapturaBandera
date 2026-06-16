# --- environment.py ---
import numpy as np
import random
from collections import deque
from settings import *

def bfs_connected(grid, start, goal):
    # ---> Pega aquí tu función bfs_connected <---
    pass

def carve_corridor(grid, a, b):
    # ---> Pega aquí tu función carve_corridor <---
    pass

def parse_map(text):
    # ---> Pega aquí tu función parse_map <---
    pass

class CTFEnv:
    def __init__(self, grid):
        self.grid = [row[:] for row in grid]
        self.base_ia = (0, 0)
        self.base_hum = (SIZE-1, SIZE-1)
        self.reset()

    def reset(self):
        self.ia = self.base_ia
        self.hum = self.base_hum
        self.ia_flag = False
        self.hum_flag = False
        self.ia_points = MOVE_POINTS    # puntos restantes de la IA en su turno
        self.done = False
        self.winner = None
        self.last_hits = []
        return self.get_state()

    def passable(self, pos):
        r, c = pos
        return 0 <= r < SIZE and 0 <= c < SIZE and self.grid[r][c] != WALL

    def ia_goal(self):
        return self.base_hum if not self.ia_flag else self.base_ia

    def _rel_dir(self, frm, to):
        return (int(np.sign(to[0]-frm[0])), int(np.sign(to[1]-frm[1])))

    @staticmethod
    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def get_state(self):
        goal = self.ia_goal()
        d_goal = min(self.manh(self.ia, goal), 9)
        d_opp = min(self.manh(self.ia, self.hum), 9)
        return (self.ia, self.hum, int(self.ia_flag), int(self.hum_flag),
                self._rel_dir(self.ia, goal), d_goal, d_opp, self.ia_points)

    def _try_move(self, pos, action, points):
        """Devuelve (nueva_pos, choco)."""
        dr, dc = MOVE[action]
        if (dr, dc) == (0, 0):
            return pos, False
        npos = (pos[0]+dr, pos[1]+dc)
        if not self.passable(npos):
            return pos, True
        c = COST[self.grid[npos[0]][npos[1]]]
        if c > points:
            return pos, False
        return npos, False

    def _capture_logic(self):
        if not self.ia_flag and self.ia == self.base_hum:
            self.ia_flag = True
        if self.ia_flag and self.ia == self.base_ia:
            self.done = True; self.winner = 'ia'
        if not self.hum_flag and self.hum == self.base_ia:
            self.hum_flag = True
        if self.hum_flag and self.hum == self.base_hum:
            self.done = True; self.winner = 'humano'

    def _send_home(self, who):
        if who == 'ia':
            self.ia = self.base_ia; self.ia_flag = False
        else:
            self.hum = self.base_hum; self.hum_flag = False

    def _fire_cannon(self):
        cells = [(r,c) for r in range(SIZE) for c in range(SIZE) if self.grid[r][c] != WALL]
        self.last_hits = random.sample(cells, min(CANNON_HITS, len(cells)))
        for h in self.last_hits:
            if self.ia == h: self._send_home('ia')
            if self.hum == h: self._send_home('hum')

    def _human_policy(self):
        """Humano simple: avanza hacia su objetivo gastando sus 4 puntos."""
        goal = self.base_ia if not self.hum_flag else self.base_hum
        points = MOVE_POINTS
        for _ in range(MOVE_POINTS):
            best, bestd = 'STAY', self.manh(self.hum, goal)
            for a in ['UP','DOWN','LEFT','RIGHT']:
                np_, choc = self._try_move(self.hum, a, points)
                if not choc and np_ != self.hum:
                    d = self.manh(np_, goal)
                    if d < bestd:
                        best, bestd = a, d
            np_, _ = self._try_move(self.hum, best, points)
            if np_ == self.hum:
                break
            points -= COST[self.grid[np_[0]][np_[1]]]
            self.hum = np_
            self._capture_logic()
            if self.done:
                return

    def _end_ia_turn(self):
        """Cierra el turno de la IA: mueve al humano, dispara canon y recarga puntos."""
        reward = 0.0
        self._human_policy()
        if self.ia == self.hum:
            self._send_home('ia')
        if self.hum_flag:
            reward -= 0.2
        if self.done and self.winner == 'humano':
            reward -= 30.0
            return reward
        self._fire_cannon()
        self.ia_points = MOVE_POINTS
        return reward

    def step(self, action):
        """Una accion de la IA (consume puntos). El humano y el canon solo
        actuan cuando la IA agota su turno (STAY, sin puntos o choque)."""
        reward = -0.05
        prev_goal_d = self.manh(self.ia, self.ia_goal())
        had_flag = self.ia_flag
        end_turn = False

        if action == 'STAY':
            reward -= 0.1
            end_turn = True
        else:
            npos, choc = self._try_move(self.ia, action, self.ia_points)
            if choc:
                reward -= 0.3
                end_turn = True
            elif npos == self.ia:
                # no alcanzan los puntos para moverse: termina el turno
                end_turn = True
            else:
                self.ia_points -= COST[self.grid[npos[0]][npos[1]]]
                self.ia = npos
                self._capture_logic()

        if self.ia_flag and not had_flag:
            reward += 5.0
        new_goal_d = self.manh(self.ia, self.ia_goal())
        if new_goal_d < prev_goal_d:
            reward += 0.2
        if self.ia == self.hum:
            reward += 1.0
            self._send_home('hum')

        if self.done:
            reward += 50.0 if self.winner == 'ia' else 0.0
            return self.get_state(), reward, True, {}

        if self.ia_points <= 0:
            end_turn = True

        if end_turn:
            reward += self._end_ia_turn()
            if self.done:
                return self.get_state(), reward, True, {}

        return self.get_state(), reward, self.done, {}
# --- codes/environment.py ---
import numpy as np
import random
from collections import deque
from codes.settings import *

def bfs_connected(grid, start, goal):
    q = deque([start]); seen = {start}
    while q:
        r, c = q.popleft()
        if (r, c) == goal: return True
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE and (nr,nc) not in seen and grid[nr][nc] != WALL:
                seen.add((nr,nc)); q.append((nr,nc))
    return False

# GENERADOR ALEATORIO DE MAPAS
def generate_random_map():
    """Genera mapas aleatorios hasta que encuentra uno con un camino válido entre bases."""
    while True:
        grid = []
        for r in range(SIZE):
            row = []
            for c in range(SIZE):
                # Probabilidades: 70% vacio, 15% lodo, 15% pared
                prob = random.random()
                if prob < 0.70:
                    row.append(EMPTY)
                elif prob < 0.85:
                    row.append(DIRT)
                else:
                    row.append(WALL)
            grid.append(row)
        
        # Asegurar que los spawns esten libres
        grid[0][0] = EMPTY
        grid[SIZE-1][SIZE-1] = EMPTY
        
        # Validador
        if bfs_connected(grid, (0,0), (SIZE-1,SIZE-1)):
            return grid

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
        self.ia_points = MOVE_POINTS
        self.hum_points = MOVE_POINTS
        self.turn = 'ia' 
        self.done = False
        self.winner = None
        self.last_hits = []
        return self.get_state(self.turn)

    def passable(self, pos):
        r, c = pos
        return 0 <= r < SIZE and 0 <= c < SIZE and self.grid[r][c] != WALL

    def ia_goal(self):
        return self.base_hum if not self.ia_flag else self.base_ia

    def hum_goal(self):
        return self.base_ia if not self.hum_flag else self.base_hum

    def _rel_dir(self, frm, to):
        return (int(np.sign(to[0]-frm[0])), int(np.sign(to[1]-frm[1])))

    @staticmethod
    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def get_state(self, who='ia'):
        if who == 'ia':
            goal = self.ia_goal()
            d_goal = min(self.manh(self.ia, goal), 9)
            d_opp = min(self.manh(self.ia, self.hum), 9)
            return (self.ia, self.hum, int(self.ia_flag), int(self.hum_flag),
                    self._rel_dir(self.ia, goal), d_goal, d_opp, self.ia_points)
        else:
            goal = self.hum_goal()
            d_goal = min(self.manh(self.hum, goal), 9)
            d_opp = min(self.manh(self.hum, self.ia), 9)
            return (self.hum, self.ia, int(self.hum_flag), int(self.ia_flag),
                    self._rel_dir(self.hum, goal), d_goal, d_opp, self.hum_points)

    def _try_move(self, pos, action, points):
        dr, dc = MOVE[action]
        npos = (pos[0]+dr, pos[1]+dc)
        if not self.passable(npos): return pos, True
        c = COST[self.grid[npos[0]][npos[1]]]
        if c > points: return pos, False
        return npos, False

    def _capture_logic(self):
        if not self.ia_flag and self.ia == self.base_hum: self.ia_flag = True
        if self.ia_flag and self.ia == self.base_ia: self.done = True; self.winner = 'ia'
        if not self.hum_flag and self.hum == self.base_ia: self.hum_flag = True
        if self.hum_flag and self.hum == self.base_hum: self.done = True; self.winner = 'humano'

    def _send_home(self, who):
        if who == 'ia': self.ia = self.base_ia; self.ia_flag = False
        else: self.hum = self.base_hum; self.hum_flag = False

    def _fire_cannon(self):
        cells = [(r,c) for r in range(SIZE) for c in range(SIZE) if self.grid[r][c] != WALL]
        self.last_hits = random.sample(cells, min(CANNON_HITS, len(cells)))
        for h in self.last_hits:
            if self.ia == h: self._send_home('ia')
            if self.hum == h: self._send_home('hum')

    def step(self, action):
        reward = -0.05 
        end_turn = False
        
        prev_goal_d_ia = self.manh(self.ia, self.ia_goal())
        prev_goal_d_hum = self.manh(self.hum, self.hum_goal())
        had_flag_ia = self.ia_flag
        had_flag_hum = self.hum_flag

        if self.turn == 'ia':
            npos, choc = self._try_move(self.ia, action, self.ia_points)
            
            if choc:
                reward -= 0.3 
                self.ia_points -= 1 
            elif npos == self.ia:
                end_turn = True 
            else:
                self.ia_points -= COST[self.grid[npos[0]][npos[1]]]
                self.ia = npos
                self._capture_logic()
                if self.ia == self.hum:
                    reward += 1.0 
                    self._send_home('hum')

            if self.ia_flag and not had_flag_ia: reward += 5.0
            if self.manh(self.ia, self.ia_goal()) < prev_goal_d_ia: reward += 0.2
            
            if self.done:
                reward += 50.0 if self.winner == 'ia' else -30.0
                return self.get_state('ia'), reward, True, {}
                
            if self.ia_points <= 0: end_turn = True
            if end_turn: self.turn = 'hum'

        else: 
            npos, choc = self._try_move(self.hum, action, self.hum_points)
            
            if choc:
                reward -= 0.3 
                self.hum_points -= 1 
            elif npos == self.hum:
                end_turn = True 
            else:
                self.hum_points -= COST[self.grid[npos[0]][npos[1]]]
                self.hum = npos
                self._capture_logic()
                if self.hum == self.ia:
                    reward += 1.0 
                    self._send_home('ia')

            if self.hum_flag and not had_flag_hum: reward += 5.0
            if self.manh(self.hum, self.hum_goal()) < prev_goal_d_hum: reward += 0.2

            if self.done:
                reward += 50.0 if self.winner == 'humano' else -30.0
                return self.get_state('hum'), reward, True, {}
                
            if self.hum_points <= 0: end_turn = True
            if end_turn:
                if self.ia_flag or self.hum_flag:
                    self._fire_cannon()
                self.ia_points = MOVE_POINTS
                self.hum_points = MOVE_POINTS
                self.turn = 'ia'
                
        return self.get_state(self.turn), reward, self.done, {}
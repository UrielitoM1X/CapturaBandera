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

def generate_random_map():
    while True:
        grid = []
        for r in range(SIZE):
            row = []
            for c in range(SIZE):
                prob = random.random()
                if prob < 0.70: row.append(EMPTY)
                elif prob < 0.85: row.append(DIRT)
                else: row.append(WALL)
            grid.append(row)
        
        grid[0][0] = EMPTY
        grid[SIZE-1][SIZE-1] = EMPTY
        
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

    # --- NUEVA VISIÓN DE RADAR ---
    def _get_local_vision(self, pos):
        """Devuelve qué hay exactamente 1 paso arriba, abajo, izquierda y derecha."""
        r, c = pos
        vision = []
        # El orden debe coincidir siempre: UP, DOWN, LEFT, RIGHT
        for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            dr, dc = MOVE[action]
            nr, nc = r + dr, c + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                tile = self.grid[nr][nc]
                if tile == WALL: vision.append(0)    # 0 = Impasable (Pared)
                elif tile == EMPTY: vision.append(1) # 1 = Costo 1 (Libre)
                elif tile == DIRT: vision.append(2)  # 2 = Costo 2 (Lodo)
            else:
                vision.append(0) # Fuera del mapa cuenta como pared
        return tuple(vision)

    def get_state(self, who='ia'):
        """Genera un estado generalizado (sin coordenadas absolutas)."""
        if who == 'ia':
            my_pos, en_pos = self.ia, self.hum
            have_en_flag, en_has_my_flag = self.ia_flag, self.hum_flag
            goal = self.ia_goal()
            pts = self.ia_points
        else:
            my_pos, en_pos = self.hum, self.ia
            have_en_flag, en_has_my_flag = self.hum_flag, self.ia_flag
            goal = self.hum_goal()
            pts = self.hum_points

        vision = self._get_local_vision(my_pos)
        goal_dir = self._rel_dir(my_pos, goal)
        en_dir = self._rel_dir(my_pos, en_pos)

        # La IA ya no sabe en qué (x,y) está. Solo sabe lo que ve, qué banderas 
        # están robadas, hacia dónde ir y cuántos puntos le quedan.
        return (vision, int(have_en_flag), int(en_has_my_flag), goal_dir, en_dir, pts)

    def _try_move(self, pos, action, points):
        dr, dc = MOVE[action]
        npos = (pos[0]+dr, pos[1]+dc)
        if not self.passable(npos): return pos, True
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
        reward = -1.0 # 1. RECOMPENSA: -1 por cada paso
        end_turn = False
        
        prev_goal_d_ia = self.manh(self.ia, self.ia_goal())
        prev_goal_d_hum = self.manh(self.hum, self.hum_goal())
        had_flag_ia = self.ia_flag
        had_flag_hum = self.hum_flag

        if self.turn == 'ia':
            npos, choc = self._try_move(self.ia, action, self.ia_points)
            
            if choc:
                self.ia_points -= 1 
            elif npos == self.ia:
                end_turn = True 
            else:
                self.ia_points -= COST[self.grid[npos[0]][npos[1]]]
                self.ia = npos
                self._capture_logic()
                
                if self.ia == self.hum:
                    # 2. RECOMPENSA: +1 por recuperar tu bandera (tocar al que la tiene)
                    if self.hum_flag: reward += 1.0 
                    self._send_home('hum')

            # 3. RECOMPENSA: +5 por agarrar bandera enemiga
            if self.ia_flag and not had_flag_ia: reward += 5.0
            
            # 4. RECOMPENSA: +0.5 por acercarse, -0.5 por alejarse
            new_goal_d = self.manh(self.ia, self.ia_goal())
            if new_goal_d < prev_goal_d_ia: reward += 0.5
            elif new_goal_d > prev_goal_d_ia: reward -= 0.5
            
            # 5. RECOMPENSA: +10 por ganar, -10 por perder
            if self.done:
                reward += 10.0 if self.winner == 'ia' else -10.0
                return self.get_state('ia'), reward, True, {}
                
            if self.ia_points <= 0: end_turn = True
            if end_turn: self.turn = 'hum'

        else: # Turno de la IA 2 / Humano
            npos, choc = self._try_move(self.hum, action, self.hum_points)
            
            if choc:
                self.hum_points -= 1 
            elif npos == self.hum:
                end_turn = True 
            else:
                self.hum_points -= COST[self.grid[npos[0]][npos[1]]]
                self.hum = npos
                self._capture_logic()
                
                if self.hum == self.ia:
                    # 2. RECOMPENSA: +1 por recuperar tu bandera (tocar al que la tiene)
                    if self.ia_flag: reward += 1.0 
                    self._send_home('ia')

            # 3. RECOMPENSA: +5 por agarrar bandera enemiga
            if self.hum_flag and not had_flag_hum: reward += 5.0
            
            # 4. RECOMPENSA: +0.5 por acercarse, -0.5 por alejarse
            new_goal_d = self.manh(self.hum, self.hum_goal())
            if new_goal_d < prev_goal_d_hum: reward += 0.5
            elif new_goal_d > prev_goal_d_hum: reward -= 0.5

            # 5. RECOMPENSA: +10 por ganar, -10 por perder
            if self.done:
                reward += 10.0 if self.winner == 'humano' else -10.0
                return self.get_state('hum'), reward, True, {}
                
            if self.hum_points <= 0: end_turn = True
            if end_turn:
                if self.ia_flag or self.hum_flag:
                    self._fire_cannon()
                self.ia_points = MOVE_POINTS
                self.hum_points = MOVE_POINTS
                self.turn = 'ia'
                
        return self.get_state(self.turn), reward, self.done, {}
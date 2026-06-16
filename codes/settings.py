# --- codes/settings.py ---
SIZE = 10
EMPTY, DIRT, WALL = '.', 't', '#'
COST = {EMPTY: 1, DIRT: 2}
ACTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']
MOVE = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
MOVE_POINTS = 4
CANNON_HITS = 5

# Constantes visuales para Pygame
TILE_SIZE = 60
SCREEN_SIZE = SIZE * TILE_SIZE
FPS = 5
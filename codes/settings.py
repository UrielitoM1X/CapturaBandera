# --- settings.py ---

# Constantes del entorno matemático (Extraídas de tus notebooks)
SIZE = 10
EMPTY, DIRT, WALL = '.', 't', '#'
COST = {EMPTY: 1, DIRT: 2}
ACTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'STAY']
MOVE = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1), 'STAY': (0, 0)}
MOVE_POINTS = 4
CANNON_HITS = 5

# Constantes visuales para Pygame
TILE_SIZE = 60                       # Tamaño en píxeles de cada celda
SCREEN_SIZE = SIZE * TILE_SIZE       # Tamaño total de la ventana
FPS = 5                              # Velocidad a la que la IA hace sus movimientos
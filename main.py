# --- main.py ---
import pygame
import sys

# Importaciones modificadas para usar la carpeta 'codes' como librería
from codes.settings import *
from codes.environment import CTFEnv, parse_map
from codes.agent import QAgent

ejemplo_mapa = """
. . . . . . t t . .
. t . # . . # . # .
. . . t . . . . . .
t . . # t . . # # .
. . . . . t . . . .
. # . . . # . . # .
. . . . . . . . t .
. t . # . t t . # .
. . . . . . . . # .
. . t # . . . . . .
"""

def draw_grid(screen, env):
    """Convierte el estado de CTFEnv en rectángulos y círculos de Pygame."""
    colores = {
        EMPTY: (245, 245, 245), 
        DIRT: (202, 164, 114),  
        WALL: (68, 68, 68)      
    }

    # 1. Dibujar el terreno
    for r in range(SIZE):
        for c in range(SIZE):
            tipo = env.grid[r][c]
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, colores[tipo], rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1) 

    # 2. Dibujar impactos del cañón
    for (r, c) in env.last_hits:
        rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (255, 0, 0), rect, 3)

    # 3. Dibujar Jugadores
    ia_center = (env.ia[1] * TILE_SIZE + TILE_SIZE//2, env.ia[0] * TILE_SIZE + TILE_SIZE//2)
    pygame.draw.circle(screen, (0, 0, 255), ia_center, TILE_SIZE//3)
    
    hum_rect = pygame.Rect(env.hum[1] * TILE_SIZE + 10, env.hum[0] * TILE_SIZE + 10, TILE_SIZE - 20, TILE_SIZE - 20)
    pygame.draw.rect(screen, (0, 255, 0), hum_rect)

    # 4. Dibujar banderas capturadas
    if env.ia_flag:
        pygame.draw.circle(screen, (255, 255, 255), ia_center, TILE_SIZE//6)
    if env.hum_flag:
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(env.hum[1] * TILE_SIZE + 20, env.hum[0] * TILE_SIZE + 20, TILE_SIZE - 40, TILE_SIZE - 40))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Captura la Bandera - Agente Q-Learning")
    clock = pygame.time.Clock()

    # Preparar el entorno
    mapa = parse_map(ejemplo_mapa)
    env = CTFEnv(mapa)
    
    # Instanciar e intentar cargar la IA
    agent = QAgent()
    try:
        agent.load('qagent.pkl')
        agent.eps = 0.0 
        print("Modelo 'qagent.pkl' cargado exitosamente.")
    except Exception:
        print("[AVISO] No se encontró 'qagent.pkl'. La IA actuará con los parámetros por defecto.")

    state = env.reset()
    running = True

    # Bucle principal de Pygame
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not env.done:
            action_idx = agent.act(state, greedy=True)
            state, reward, done, _ = env.step(ACTIONS[action_idx])
            
            if done:
                print(f"Partida finalizada. Ganador: {env.winner}")

        # Actualizar los gráficos
        screen.fill((0, 0, 0))
        draw_grid(screen, env)
        pygame.display.flip()
        
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
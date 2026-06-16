# --- main.py ---
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from codes.settings import *
# Importamos el generador aleatorio
from codes.environment import CTFEnv, generate_random_map
from codes.agent import QAgent

def draw_grid(screen, env):
    colores = {EMPTY: (245, 245, 245), DIRT: (202, 164, 114), WALL: (68, 68, 68)}

    for r in range(SIZE):
        for c in range(SIZE):
            tipo = env.grid[r][c]
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, colores[tipo], rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

    for (r, c) in env.last_hits:
        rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (255, 0, 0), rect, 3)

    if not env.hum_flag:
        br, bc = env.base_ia
        pygame.draw.polygon(screen, (0, 150, 255), [(bc * TILE_SIZE + 15, br * TILE_SIZE + 15), (bc * TILE_SIZE + 45, br * TILE_SIZE + 30), (bc * TILE_SIZE + 15, br * TILE_SIZE + 45)])
        pygame.draw.line(screen, (0, 0, 0), (bc * TILE_SIZE + 15, br * TILE_SIZE + 15), (bc * TILE_SIZE + 15, br * TILE_SIZE + 50), 3) 

    if not env.ia_flag:
        br, bc = env.base_hum
        pygame.draw.polygon(screen, (50, 200, 50), [(bc * TILE_SIZE + 45, br * TILE_SIZE + 15), (bc * TILE_SIZE + 15, br * TILE_SIZE + 30), (bc * TILE_SIZE + 45, br * TILE_SIZE + 45)])
        pygame.draw.line(screen, (0, 0, 0), (bc * TILE_SIZE + 45, br * TILE_SIZE + 15), (bc * TILE_SIZE + 45, br * TILE_SIZE + 50), 3) 

    ia_center = (env.ia[1] * TILE_SIZE + TILE_SIZE//2, env.ia[0] * TILE_SIZE + TILE_SIZE//2)
    pygame.draw.circle(screen, (0, 0, 255), ia_center, TILE_SIZE//3)
    if env.ia_flag:
        pygame.draw.polygon(screen, (50, 200, 50), [(ia_center[0] - 10, ia_center[1] - 10), (ia_center[0] + 10, ia_center[1]), (ia_center[0] - 10, ia_center[1] + 10)])

    hum_rect = pygame.Rect(env.hum[1] * TILE_SIZE + 10, env.hum[0] * TILE_SIZE + 10, TILE_SIZE - 20, TILE_SIZE - 20)
    pygame.draw.rect(screen, (0, 255, 0), hum_rect)
    if env.hum_flag:
        hcx, hcy = env.hum[1] * TILE_SIZE + TILE_SIZE//2, env.hum[0] * TILE_SIZE + TILE_SIZE//2
        pygame.draw.polygon(screen, (0, 150, 255), [(hcx + 10, hcy - 10), (hcx - 10, hcy), (hcx + 10, hcy + 10)])

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    
    PVE_MODE = True  

    if PVE_MODE:
        pygame.display.set_caption("Captura la Bandera - Jugador vs IA")
    else:
        pygame.display.set_caption("Captura la Bandera - IA vs IA")
        
    clock = pygame.time.Clock()

    # Se genera el primer mapa aleatorio
    env = CTFEnv(generate_random_map())
    
    agent1 = QAgent()
    agent2 = QAgent()
    
    try:
        agent1.load('qagent.pkl')
        agent1.eps = 0.0 
        if not PVE_MODE:
            agent2.load('qagent.pkl') 
            agent2.eps = 0.0
        print("Cerebro(s) de IA cargado(s) exitosamente.")
    except Exception as e:
        print(f"[AVISO] No se pudo cargar el modelo ({e}).")

    state = env.reset()
    running = True

    teclas_acciones = {
        pygame.K_UP: 'UP', pygame.K_w: 'UP',
        pygame.K_DOWN: 'DOWN', pygame.K_s: 'DOWN',
        pygame.K_LEFT: 'LEFT', pygame.K_a: 'LEFT',
        pygame.K_RIGHT: 'RIGHT', pygame.K_d: 'RIGHT'
    }

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if PVE_MODE and not env.done and env.turn == 'hum':
                if event.type == pygame.KEYDOWN:
                    if event.key in teclas_acciones:
                        accion_humano = teclas_acciones[event.key]
                        state, reward, done, _ = env.step(accion_humano)
                        
                        if done:
                            print(f"Partida finalizada. Ganador: {env.winner}")

        if not env.done:
            current_player = env.turn
            
            if current_player == 'ia':
                pygame.time.wait(200) 
                estado_ia = env.get_state('ia')
                action_idx = agent1.act(estado_ia, greedy=True)
                state, reward, done, _ = env.step(ACTIONS[action_idx])
                if done: print(f"Partida finalizada. Ganador: {env.winner}")
                    
            elif not PVE_MODE and current_player == 'hum':
                pygame.time.wait(200)
                estado_ia2 = env.get_state('hum')
                action_idx = agent2.act(estado_ia2, greedy=True)
                state, reward, done, _ = env.step(ACTIONS[action_idx])
                if done: print(f"Partida finalizada. Ganador: {env.winner}")

        else:
            pygame.time.wait(2000)
            # ¡La magia ocurre aquí! Se sobreescribe el entorno con un nuevo mapa aleatorio
            env = CTFEnv(generate_random_map())
            state = env.reset()
            print("Reiniciando nueva partida en mapa aleatorio...")

        screen.fill((0, 0, 0))
        draw_grid(screen, env)
        pygame.display.flip()
        
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
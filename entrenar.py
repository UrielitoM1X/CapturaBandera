# --- entrenar.py ---
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from codes.settings import *
# Importacion del generador aleatorio
from codes.environment import CTFEnv, generate_random_map
from codes.agent import QAgent

def train_self_play(episodes=30000, max_steps=400):
    agent = QAgent()

    print(f"Iniciando entrenamiento de {episodes} episodios en MAPAS ALEATORIOS...")
    start_time = time.time()
    
    historial_victorias = {'ia': 0, 'humano': 0, 'empates': 0}

    for ep in range(episodes):
        # Creaciond de nuevo mapa
        env = CTFEnv(generate_random_map())
        pasos_actuales = 0 
        
        while not env.done and pasos_actuales < max_steps:
            current_player = env.turn
            state = env.get_state(current_player)
            
            a = agent.act(state)
            _, r, done, _ = env.step(ACTIONS[a])
            
            next_state = env.get_state(current_player)
            agent.learn(state, a, r, next_state, done)
            
            pasos_actuales += 1
        
        agent.decay() 
        
        if env.winner:
            historial_victorias[env.winner] += 1
        else:
            historial_victorias['empates'] += 1
            
        if (ep + 1) % 1000 == 0:
            print(f"Ep {ep + 1}/{episodes} | Eps: {agent.eps:.3f} | "
                  f"Wins Azul: {historial_victorias['ia']} | Wins Verde: {historial_victorias['humano']} | Empates: {historial_victorias['empates']}")
            historial_victorias = {'ia': 0, 'humano': 0, 'empates': 0}

    print(f"\nEntrenamiento finalizado en {time.time() - start_time:.2f} segundos.")
    agent.save('qagent.pkl')

if __name__ == "__main__":
    train_self_play(30000, max_steps=400)
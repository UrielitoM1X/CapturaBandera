# qlearning.py
import random
from collections import deque, defaultdict

# Constantes del mapa
PASTO, TIERRA, BLOQUEADO, BORDE = ".", "T", "X", "#"
JUGADOR, ENEMIGO = "A", "B"

# Acciones posibles: 0=Arriba, 1=Abajo, 2=Izquierda, 3=Derecha
MOVIMIENTOS = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, -1),
    3: (0, 1)
}

def dentro_limites(f, c, filas, columnas):
    return 0 <= f < filas and 0 <= c < columnas

def bfs(grid, inicio, destino):
    """Valida si existe un camino libre entre dos puntos del mapa."""
    filas, columnas = len(grid), len(grid[0])
    cola, visitados = deque([inicio]), {inicio}
    while cola:
        f, c = cola.popleft()
        if (f, c) == destino: 
            return True
        for df, dc in MOVIMIENTOS.values():
            nf, nc = f + df, c + dc
            if dentro_limites(nf, nc, filas, columnas) and (nf, nc) not in visitados:
                if grid[nf][nc] not in [BORDE, BLOQUEADO]:
                    visitados.add((nf, nc))
                    cola.append((nf, nc))
    return False

class Mapa:
    def __init__(self, filas=12, columnas=12):
        self.filas = filas
        self.columnas = columnas
        self.grid = []
        self.base_jugador = (1, 1)
        self.base_enemigo = (self.filas - 2, self.columnas - 2)
        self.generar()

    def generar(self):
        while True:
            # Rejilla base con bordes perimetrales
            self.grid = [[BORDE if f == 0 or c == 0 or f == self.filas - 1 or c == self.columnas - 1 else PASTO 
                          for c in range(self.columnas)] for f in range(self.filas)]
            
            # Posicionar bases iniciales fijas
            self.grid[self.base_jugador[0]][self.base_jugador[1]] = JUGADOR
            self.grid[self.base_enemigo[0]][self.base_enemigo[1]] = ENEMIGO
            
            # Obstáculos aleatorios sin pisar las bases
            for f in range(1, self.filas - 1):
                for c in range(1, self.columnas - 1):
                    if (f, c) in [self.base_jugador, self.base_enemigo]: 
                        continue
                    prob = random.random()
                    if prob < 0.08: 
                        self.grid[f][c] = BLOQUEADO
                    elif prob < 0.14: 
                        self.grid[f][c] = TIERRA
                        
            if bfs(self.grid, self.base_jugador, self.base_enemigo) and bfs(self.grid, self.base_enemigo, self.base_jugador):
                break

class GestorPartida:
    def __init__(self, mapa):
        self.mapa = mapa
        self.pos_j = list(mapa.base_jugador)
        self.pos_e = list(mapa.base_enemigo)
        self.ganador = ""
        
        # Flujo de estrategia por turnos
        self.turno = "JUGADOR"
        self.puntos_accion = 4
        
        # Cerebro de la IA (Q-Table)
        self.q_table = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2

    def reiniciar(self):
        self.pos_j = list(self.mapa.base_jugador)
        self.pos_e = list(self.mapa.base_enemigo)
        self.ganador = ""
        self.turno = "JUGADOR"
        self.puntos_accion = 4

    def mover_jugador(self, direccion: int):
        """Mueve al jugador gastando Puntos de Acción dinámicamente según el terreno."""
        if self.ganador or self.turno != "JUGADOR": 
            return
            
        df, dc = MOVIMIENTOS[direccion]
        nf, nc = self.pos_j[0] + df, self.pos_j[1] + dc
        
        if dentro_limites(nf, nc, self.mapa.filas, self.mapa.columnas):
            tipo_terreno = self.mapa.grid[nf][nc]
            
            if tipo_terreno not in [BORDE, BLOQUEADO]:
                # Regreso del requerimiento: Tierra cuesta 2 PA, Pasto cuesta 1 PA
                costo = 2 if tipo_terreno == TIERRA else 1
                
                if self.puntos_accion >= costo:
                    self.pos_j = [nf, nc]
                    self.puntos_accion -= costo
                    self.comprobar_final()
                    
                    # Si se agotan los 4 turnos/PA, cambia automáticamente al Bot
                    if self.puntos_accion <= 0 and not self.ganador:
                        self.turno = "BOT"
                        self.ejecutar_turno_bot()

    def ejecutar_turno_bot(self):
        """El bot realiza exactamente un único movimiento óptimo y cede el turno."""
        if self.ganador: 
            return
            
        self.realizar_movimiento_optimo_agente()
        
        # Regresa el control al usuario con sus 4 PA completos
        if not self.ganador:
            self.turno = "JUGADOR"
            self.puntos_accion = 4

    def comprobar_final(self):
        if self.pos_j == self.pos_e:
            self.ganador = "¡Fin del juego! El Agente B te ha atrapado."

    def exportar_estado(self):
        return {
            "filas": self.mapa.filas,
            "columnas": self.mapa.columnas,
            "posicion_jugador": self.pos_j,
            "posicion_enemigo": self.pos_e,
            "ganador": self.ganador,
            "grid": self.mapa.grid,
            "puntos_accion": self.puntos_accion,
            "turno": self.turno
        }

    # --- ENTRENAMIENTO PURO: BOT VS BOT VIRTUAL EN LA ESQUINA (1,1) ---

    def entrenar_episodio(self):
        """Entrenamiento autónomo: B busca la esquina (1,1) en simulaciones rápidas."""
        estado_actual = tuple(self.pos_e)
        objetivo_virtual = tuple(self.mapa.base_jugador) # Destino fijo de entrenamiento
        pasos = 0
        
        while estado_actual != objetivo_virtual and pasos < 200:
            pasos += 1
            
            if random.random() < self.epsilon:
                accion = random.randint(0, 3)
            else:
                valores_q = self.q_table[estado_actual]
                accion = valores_q.index(max(valores_q))
                
            df, dc = MOVIMIENTOS[accion]
            nf, nc = estado_actual[0] + df, estado_actual[1] + dc
            nuevo_estado = (nf, nc)
            
            if not dentro_limites(nf, nc, self.mapa.filas, self.mapa.columnas) or self.mapa.grid[nf][nc] in [BORDE, BLOQUEADO]:
                recompensa = -15
                nuevo_estado = estado_actual
            elif nuevo_estado == objetivo_virtual:
                recompensa = 100
            elif self.mapa.grid[nf][nc] == TIERRA:
                recompensa = -3
            else:
                recompensa = -1
                
            q_antiguo = self.q_table[estado_actual][accion]
            max_q_futuro = max(self.q_table[nuevo_estado])
            
            # Ecuación de Bellman
            self.q_table[estado_actual][accion] = q_antiguo + self.alpha * (recompensa + self.gamma * max_q_futuro - q_antiguo)
            estado_actual = nuevo_estado

    def realizar_movimiento_optimo_agente(self):
        """El Bot consulta su conocimiento y da un paso físico en el mapa real."""
        estado_actual = tuple(self.pos_e)
        valores_q = self.q_table[estado_actual]
        accion = valores_q.index(max(valores_q))
        
        df, dc = MOVIMIENTOS[accion]
        nf, nc = self.pos_e[0] + df, self.pos_e[1] + dc
        
        if dentro_limites(nf, nc, self.mapa.filas, self.mapa.columnas) and self.mapa.grid[nf][nc] not in [BORDE, BLOQUEADO]:
            self.pos_e = [nf, nc]
            self.comprobar_final()
# ============================================================
# entorno.py - PARTE 1
# Generación de mapas y validación
# ============================================================

import random
from collections import deque

# ============================================================
# CONSTANTES
# ============================================================

MIN_MAPA = 5
MAX_MAPA = 10

PASTO = "."
TIERRA = "T"
BLOQUEADO = "X"
BORDE = "#"

JUGADOR = "A"
ENEMIGO = "B"

# Costos de movimiento
COSTO_TERRENO = {
    PASTO: 1,
    TIERRA: 2
}

# Movimientos posibles
MOVIMIENTOS = [
    (-1, 0),  # arriba
    (1, 0),   # abajo
    (0, -1),  # izquierda
    (0, 1)    # derecha
]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def dentro_limites(fila, columna, filas, columnas):
    """
    Verifica si una coordenada está dentro del mapa.
    """
    return 0 <= fila < filas and 0 <= columna < columnas


def es_transitable(valor):
    """
    Casillas que pueden recorrerse.
    Las banderas NO forman parte del mapa,
    son entidades independientes.
    """

    return valor in (
        PASTO,
        TIERRA,
        JUGADOR,
        ENEMIGO
    )


def es_bloqueado(valor):

    return valor in (
        BLOQUEADO,
        BORDE
    )

# ============================================================
# BFS
# ============================================================

def bfs(mapa, inicio, destino):
    """
    Verifica si existe un camino entre dos puntos.
    """

    filas = len(mapa)
    columnas = len(mapa[0])

    cola = deque()
    visitados = set()

    cola.append(inicio)
    visitados.add(inicio)

    while cola:

        fila, columna = cola.popleft()

        if (fila, columna) == destino:
            return True

        for df, dc in MOVIMIENTOS:

            nf = fila + df
            nc = columna + dc

            if not dentro_limites(nf, nc, filas, columnas):
                continue

            if (nf, nc) in visitados:
                continue

            if not es_transitable(mapa[nf][nc]):
                continue

            visitados.add((nf, nc))
            cola.append((nf, nc))

    return False


# ============================================================
# CLASE MAPA
# ============================================================

class Mapa:

    def __init__(self):

        self.filas = 0
        self.columnas = 0

        self.grid = []

        self.base_jugador = None
        self.base_enemigo = None

    # ========================================================
    # CREAR MAPA ALEATORIO
    # ========================================================

    def generar_aleatorio(self, filas=None, columnas=None):

        if filas is None:
            filas = random.randint(MIN_MAPA, MAX_MAPA)

        if columnas is None:
            columnas = random.randint(MIN_MAPA, MAX_MAPA)

        self.filas = filas
        self.columnas = columnas

        while True:

            self.grid = []

            # ----------------------------------------
            # Crear bordes
            # ----------------------------------------

            for f in range(filas):

                fila_actual = []

                for c in range(columnas):

                    if (
                        f == 0
                        or c == 0
                        or f == filas - 1
                        or c == columnas - 1
                    ):
                        fila_actual.append(BORDE)
                    else:
                        fila_actual.append(PASTO)

                self.grid.append(fila_actual)

            # ----------------------------------------
            # Bases
            # ----------------------------------------

            self.base_jugador = (1, 1)
            self.base_enemigo = (filas - 2, columnas - 2)

            self.grid[1][1] = JUGADOR
            self.grid[filas - 2][columnas - 2] = ENEMIGO

            # ----------------------------------------
            # Casillas interiores
            # ----------------------------------------

            interiores = []

            for f in range(1, filas - 1):
                for c in range(1, columnas - 1):

                    if (f, c) == self.base_jugador:
                        continue

                    if (f, c) == self.base_enemigo:
                        continue

                    interiores.append((f, c))

            porcentaje = random.uniform(0.05, 0.07)

            cantidad_modificar = max(
                1,
                int(len(interiores) * porcentaje)
            )

            seleccionadas = random.sample(
                interiores,
                cantidad_modificar
            )

            mitad = cantidad_modificar // 2

            tierras = seleccionadas[:mitad]
            bloqueadas = seleccionadas[mitad:]

            for f, c in tierras:
                self.grid[f][c] = TIERRA

            for f, c in bloqueadas:
                self.grid[f][c] = BLOQUEADO

            # ----------------------------------------
            # Validar
            # ----------------------------------------

            if self.es_valido():
                break

    # ========================================================
    # CARGAR DESDE TXT
    # ========================================================

    def cargar_desde_txt(self, ruta):

        with open(ruta, "r", encoding="utf-8") as archivo:

            lineas = [
                linea.strip()
                for linea in archivo.readlines()
                if linea.strip()
            ]

        self.grid = [list(fila) for fila in lineas]

        self.filas = len(self.grid)
        self.columnas = len(self.grid[0])

        self.base_jugador = None
        self.base_enemigo = None

        for f in range(self.filas):
            for c in range(self.columnas):

                if self.grid[f][c] == JUGADOR:
                    self.base_jugador = (f, c)

                elif self.grid[f][c] == ENEMIGO:
                    self.base_enemigo = (f, c)

        if self.base_jugador is None:
            raise ValueError(
                "No existe la base del jugador (A)"
            )

        if self.base_enemigo is None:
            raise ValueError(
                "No existe la base del enemigo (B)"
            )

        if not self.es_valido():
            raise ValueError(
                "El mapa cargado no tiene solución"
            )

    # ========================================================
    # VALIDAR ESCENARIO
    # ========================================================

    def es_valido(self):
        """
        Verifica que ambos puedan llegar
        a la bandera enemiga y volver.
        """

        if self.base_jugador is None:
            return False

        if self.base_enemigo is None:
            return False

        ida_jugador = bfs(
            self.grid,
            self.base_jugador,
            self.base_enemigo
        )

        vuelta_jugador = bfs(
            self.grid,
            self.base_enemigo,
            self.base_jugador
        )

        ida_enemigo = bfs(
            self.grid,
            self.base_enemigo,
            self.base_jugador
        )

        vuelta_enemigo = bfs(
            self.grid,
            self.base_jugador,
            self.base_enemigo
        )

        return (
            ida_jugador
            and vuelta_jugador
            and ida_enemigo
            and vuelta_enemigo
        )

    # ========================================================
    # OBTENER TERRENO
    # ========================================================

    def obtener_terreno(self, fila, columna):
        return self.grid[fila][columna]

    # ========================================================
    # COSTO DE MOVIMIENTO
    # ========================================================

    def costo_movimiento(self, fila, columna):

        terreno = self.grid[fila][columna]

        if terreno == PASTO:
            return 1

        if terreno == TIERRA:
            return 2

        return float("inf")

    # ========================================================
    # IMPRIMIR MAPA
    # ========================================================

    def mostrar(self):

        for fila in self.grid:
            print(" ".join(fila))

        print()
        
    
    def vecinos_validos(self, fila, columna):

        vecinos = []

        for df, dc in MOVIMIENTOS:

            nf = fila + df
            nc = columna + dc

            if not dentro_limites(
                nf,
                nc,
                self.filas,
                self.columnas
            ):
                continue

            if es_bloqueado(
                self.grid[nf][nc]
            ):
                continue

            vecinos.append((nf, nc))

        return vecinos
    
    
    def exportar(self):

        return {
            "filas": self.filas,
            "columnas": self.columnas,
            "grid": self.grid,
            "base_jugador": self.base_jugador,
            "base_enemigo": self.base_enemigo
        }
        
    
    def importar(self, datos):

        self.filas = datos["filas"]
        self.columnas = datos["columnas"]

        self.grid = datos["grid"]

        self.base_jugador = tuple(
            datos["base_jugador"]
        )

        self.base_enemigo = tuple(
            datos["base_enemigo"]
        )
    


def distancia_manhattan(a, b):

    return (
        abs(a[0] - b[0]) +
        abs(a[1] - b[1])
    )

# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":

    mapa = Mapa()

    mapa.generar_aleatorio()

    print("Mapa generado:")
    mapa.mostrar()

    print("Valido:", mapa.es_valido())

    print("Base jugador:", mapa.base_jugador)
    print("Base enemigo:", mapa.base_enemigo)
    
    
# ============================================================
# entorno.py - PARTE 2
# Entidades y mecánicas del juego
# ============================================================

import random

# ============================================================
# BANDERA
# ============================================================

class Bandera:

    def __init__(self, posicion_base):
        self.base_original = posicion_base
        self.posicion = posicion_base

    def reiniciar(self):
        self.posicion = self.base_original


# ============================================================
# JUGADOR
# ============================================================

class Jugador:

    def __init__(self, posicion_inicial):

        self.base = posicion_inicial

        self.fila = posicion_inicial[0]
        self.columna = posicion_inicial[1]

        self.tiene_bandera = False

    def posicion(self):
        return (self.fila, self.columna)

    def reiniciar(self):

        self.fila = self.base[0]
        self.columna = self.base[1]

        self.tiene_bandera = False

    def mover(self, accion, mapa):

        movimientos = {
            0: (-1, 0),   # arriba
            1: (1, 0),    # abajo
            2: (0, -1),   # izquierda
            3: (0, 1)     # derecha
        }

        if accion not in movimientos:
            return False

        df, dc = movimientos[accion]

        nf = self.fila + df
        nc = self.columna + dc

        if not dentro_limites(
            nf,
            nc,
            mapa.filas,
            mapa.columnas
        ):
            return False

        if mapa.grid[nf][nc] in [BORDE, BLOQUEADO]:
            return False

        self.fila = nf
        self.columna = nc

        return True


# ============================================================
# ENEMIGO
# ============================================================

class Enemigo(Jugador):

    def mover_aleatorio(self, mapa):

        acciones = [0, 1, 2, 3]

        random.shuffle(acciones)

        for accion in acciones:

            if self.mover(accion, mapa):
                return accion

        return None


# ============================================================
# CANON
# ============================================================

class Canon:

    def __init__(self):

        self.activo = False
        self.casillas_bombardeadas = []

    def activar(self):
        self.activo = True

    def desactivar(self):

        self.activo = False
        self.casillas_bombardeadas = []

    def generar_bombardeo(self, mapa):

        if not self.activo:
            return []

        disponibles = []

        for f in range(1, mapa.filas - 1):
            for c in range(1, mapa.columnas - 1):

                if mapa.grid[f][c] != BLOQUEADO:
                    disponibles.append((f, c))

        cantidad = min(5, len(disponibles))

        self.casillas_bombardeadas = random.sample(
            disponibles,
            cantidad
        )

        return self.casillas_bombardeadas


# ============================================================
# GESTOR DE PARTIDA
# ============================================================

class GestorPartida:

    def __init__(self, mapa):

        self.mapa = mapa

        self.jugador = Jugador(
            mapa.base_jugador
        )

        self.enemigo = Enemigo(
            mapa.base_enemigo
        )

        self.bandera_jugador = Bandera(
            mapa.base_jugador
        )

        self.bandera_enemigo = Bandera(
            mapa.base_enemigo
        )

        self.canon = Canon()

        self.turno = "jugador"

        self.ganador = None

    # ========================================================
    # CAPTURA DE BANDERAS
    # ========================================================

    def verificar_banderas(self):

        # Jugador captura bandera enemiga

        if (
            self.jugador.posicion()
            == self.bandera_enemigo.posicion
            and not self.jugador.tiene_bandera
        ):

            self.jugador.tiene_bandera = True

            self.canon.activar()

        # Enemigo captura bandera jugador

        if (
            self.enemigo.posicion()
            == self.bandera_jugador.posicion
            and not self.enemigo.tiene_bandera
        ):

            self.enemigo.tiene_bandera = True

            self.canon.activar()

    # ========================================================
    # VICTORIA
    # ========================================================

    def verificar_victoria(self):

        if (
            self.jugador.tiene_bandera
            and self.jugador.posicion()
            == self.jugador.base
        ):
            self.ganador = "jugador"
            return True

        if (
            self.enemigo.tiene_bandera
            and self.enemigo.posicion()
            == self.enemigo.base
        ):
            self.ganador = "enemigo"
            return True

        return False

    # ========================================================
    # COLISIONES
    # ========================================================

    def verificar_colision(self):

        if (
            self.jugador.posicion()
            != self.enemigo.posicion()
        ):
            return

        if self.turno == "jugador":

            self.enemigo.reiniciar()

            self.bandera_jugador.reiniciar()
            self.bandera_enemigo.reiniciar()

            self.canon.desactivar()

        else:

            self.jugador.reiniciar()

            self.bandera_jugador.reiniciar()
            self.bandera_enemigo.reiniciar()

            self.canon.desactivar()

    # ========================================================
    # BOMBARDEO
    # ========================================================

    def verificar_bombardeo(self):

        if not self.canon.activo:
            return

        bombas = self.canon.generar_bombardeo(
            self.mapa
        )

        pos_jugador = self.jugador.posicion()
        pos_enemigo = self.enemigo.posicion()

        if pos_jugador in bombas:

            self.jugador.reiniciar()

            self.bandera_jugador.reiniciar()
            self.bandera_enemigo.reiniciar()

            self.canon.desactivar()

        if pos_enemigo in bombas:

            self.enemigo.reiniciar()

            self.bandera_jugador.reiniciar()
            self.bandera_enemigo.reiniciar()

            self.canon.desactivar()

    # ========================================================
    # TURNO DEL JUGADOR
    # ========================================================

    def turno_jugador(self, accion):

        self.turno = "jugador"

        valido = self.jugador.mover(
            accion,
            self.mapa
        )

        self.verificar_banderas()
        self.verificar_colision()
        self.verificar_victoria()

        return valido

    # ========================================================
    # TURNO DEL ENEMIGO
    # ========================================================

    def turno_enemigo(self):

        self.turno = "enemigo"

        self.enemigo.mover_aleatorio(
            self.mapa
        )

        self.verificar_banderas()
        self.verificar_colision()
        self.verificar_victoria()

    # ========================================================
    # TURNO DEL CAÑON
    # ========================================================

    def turno_canon(self):

        self.verificar_bombardeo()

    # ========================================================
    # CICLO COMPLETO
    # ========================================================

    def ejecutar_turno(self, accion_jugador):

        self.turno_jugador(
            accion_jugador
        )

        if self.ganador:
            return

        self.turno_enemigo()

        if self.ganador:
            return

        self.turno_canon()

    # ========================================================
    # ESTADO PARA Q-LEARNING
    # ========================================================

    def obtener_estado_jugador(self):

        return (
            self.jugador.fila,
            self.jugador.columna,
            int(self.jugador.tiene_bandera)
        )

    # ========================================================
    # REINICIO COMPLETO
    # ========================================================

    def reiniciar(self):

        self.jugador.reiniciar()

        self.enemigo.reiniciar()

        self.bandera_jugador.reiniciar()

        self.bandera_enemigo.reiniciar()

        self.canon.desactivar()

        self.ganador = None
        


# ============================================================
# entorno.py - PARTE 3
# Q-Learning
# ============================================================

import pickle
import random
from collections import defaultdict

# ============================================================
# AGENTE Q-LEARNING
# ============================================================

class QLearningAgent:

    def __init__(
        self,
        alpha=0.1,
        gamma=0.95,
        epsilon=0.10
    ):

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        # Estado -> [Q arriba, abajo, izquierda, derecha]
        self.q_table = defaultdict(
            lambda: [0.0, 0.0, 0.0, 0.0]
        )

    # ========================================================
    # OBTENER Q
    # ========================================================

    def obtener_q(self, estado):

        return self.q_table[estado]

    # ========================================================
    # ACCIÓN ε-GREEDY
    # ========================================================

    def elegir_accion(self, estado):

        if random.random() < self.epsilon:
            return random.randint(0, 3)

        valores = self.q_table[estado]

        maximo = max(valores)

        mejores = [
            i
            for i, v in enumerate(valores)
            if v == maximo
        ]

        return random.choice(mejores)

    # ========================================================
    # POLÍTICA PURA
    # ========================================================

    def mejor_accion(self, estado):

        valores = self.q_table[estado]

        maximo = max(valores)

        mejores = [
            i
            for i, v in enumerate(valores)
            if v == maximo
        ]

        return random.choice(mejores)

    # ========================================================
    # ACTUALIZACIÓN Q
    # ========================================================

    def actualizar_q(
        self,
        estado,
        accion,
        recompensa,
        siguiente_estado
    ):

        q_actual = self.q_table[estado][accion]

        max_siguiente = max(
            self.q_table[siguiente_estado]
        )

        nuevo_q = q_actual + self.alpha * (
            recompensa
            + self.gamma * max_siguiente
            - q_actual
        )

        self.q_table[estado][accion] = nuevo_q

    # ========================================================
    # GUARDAR
    # ========================================================

    def guardar(self, archivo):

        datos = {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "q_table": dict(self.q_table)
        }

        with open(archivo, "wb") as f:
            pickle.dump(datos, f)

    # ========================================================
    # CARGAR
    # ========================================================

    def cargar(self, archivo):

        with open(archivo, "rb") as f:
            datos = pickle.load(f)

        self.alpha = datos["alpha"]
        self.gamma = datos["gamma"]
        self.epsilon = datos["epsilon"]

        self.q_table = defaultdict(
            lambda: [0.0, 0.0, 0.0, 0.0]
        )

        self.q_table.update(
            datos["q_table"]
        )

# ============================================================
# RECOMPENSAS
# ============================================================

class SistemaRecompensas:

    @staticmethod
    def calcular(
        gestor,
        estado_anterior,
        estado_nuevo,
        movimiento_valido
    ):

        recompensa = 0

        jugador = gestor.jugador

        # ------------------------------------
        # Movimiento inválido
        # ------------------------------------

        if not movimiento_valido:
            return -50

        fila = jugador.fila
        columna = jugador.columna

        terreno = gestor.mapa.grid[
            fila
        ][
            columna
        ]

        # ------------------------------------
        # Costo terreno
        # ------------------------------------

        if terreno == PASTO:
            recompensa -= 1

        elif terreno == TIERRA:
            recompensa -= 2

        # ------------------------------------
        # Objetivo actual
        # ------------------------------------

        if jugador.tiene_bandera:

            objetivo = jugador.base

        else:

            objetivo = (
                gestor.bandera_enemigo.posicion
            )

        distancia_antes = distancia_manhattan(
            (
                estado_anterior[0],
                estado_anterior[1]
            ),
            objetivo
        )

        distancia_despues = distancia_manhattan(
            (
                estado_nuevo[0],
                estado_nuevo[1]
            ),
            objetivo
        )

        # ------------------------------------
        # Acercarse
        # ------------------------------------

        if distancia_despues < distancia_antes:
            recompensa += 5

        elif distancia_despues > distancia_antes:
            recompensa -= 5

        # ------------------------------------
        # Captura bandera
        # ------------------------------------

        if (
            not estado_anterior[2]
            and estado_nuevo[2]
        ):
            recompensa += 200

        # ------------------------------------
        # Victoria
        # ------------------------------------

        if gestor.ganador == "jugador":
            recompensa += 1000

        # ------------------------------------
        # Muerte por bomba
        # ------------------------------------

        if (
            jugador.posicion()
            == jugador.base
            and estado_anterior[:2]
            != jugador.base
        ):
            recompensa -= 500

        return recompensa

# ============================================================
# ENTRENADOR
# ============================================================

class EntrenadorQLearning:

    def __init__(
        self,
        gestor,
        agente
    ):

        self.gestor = gestor
        self.agente = agente

    # ========================================================
    # UNA ÉPOCA
    # ========================================================

    def entrenar_epoca(
        self,
        pasos_maximos=500
    ):

        self.gestor.reiniciar()

        for _ in range(
            pasos_maximos
        ):

            estado = (
                self.gestor.obtener_estado_jugador()
            )

            accion = (
                self.agente.elegir_accion(
                    estado
                )
            )

            valido = (
                self.gestor.turno_jugador(
                    accion
                )
            )

            self.gestor.turno_enemigo()

            self.gestor.turno_canon()

            siguiente_estado = (
                self.gestor.obtener_estado_jugador()
            )

            recompensa = (
                SistemaRecompensas.calcular(
                    self.gestor,
                    estado,
                    siguiente_estado,
                    valido
                )
            )

            self.agente.actualizar_q(
                estado,
                accion,
                recompensa,
                siguiente_estado
            )

            if self.gestor.ganador:
                break

    # ========================================================
    # MUCHAS ÉPOCAS
    # ========================================================

    def entrenar(
        self,
        epocas=10000,
        pasos_maximos=500
    ):

        for epoca in range(epocas):

            self.entrenar_epoca(
                pasos_maximos
            )

            if (epoca + 1) % 1000 == 0:

                print(
                    f"Entrenadas "
                    f"{epoca+1} épocas"
                )

    # ========================================================
    # EJECUTAR POLÍTICA APRENDIDA
    # ========================================================

    def ejecutar_modelo(
        self,
        pasos_maximos=500
    ):

        self.gestor.reiniciar()

        historial = []

        for _ in range(
            pasos_maximos
        ):

            estado = (
                self.gestor.obtener_estado_jugador()
            )

            accion = (
                self.agente.mejor_accion(
                    estado
                )
            )

            self.gestor.ejecutar_turno(
                accion
            )

            historial.append(
                self.gestor.obtener_estado_jugador()
            )

            if self.gestor.ganador:
                break

        return historial
    

# ============================================================
# entorno.py - PARTE 4
# Integración general
# ============================================================

class Entorno:

    def __init__(self):

        self.mapa = None

        self.gestor = None

        self.agente = None

        self.entrenador = None

    # ========================================================
    # CREAR MAPA ALEATORIO
    # ========================================================

    def generar_mapa(
        self,
        filas=None,
        columnas=None
    ):

        self.mapa = Mapa()

        self.mapa.generar_aleatorio(
            filas,
            columnas
        )

        self._crear_componentes()

    # ========================================================
    # CARGAR TXT
    # ========================================================

    def cargar_mapa(
        self,
        ruta_txt
    ):

        self.mapa = Mapa()

        self.mapa.cargar_desde_txt(
            ruta_txt
        )

        self._crear_componentes()

    # ========================================================
    # CREAR OBJETOS
    # ========================================================

    def _crear_componentes(self):

        self.gestor = GestorPartida(
            self.mapa
        )

        self.agente = QLearningAgent()

        self.entrenador = (
            EntrenadorQLearning(
                self.gestor,
                self.agente
            )
        )

    # ========================================================
    # ENTRENAR
    # ========================================================

    def entrenar(
        self,
        epocas=10000,
        pasos_maximos=500
    ):

        if self.entrenador is None:

            raise RuntimeError(
                "No existe mapa cargado"
            )

        self.entrenador.entrenar(
            epocas,
            pasos_maximos
        )

    # ========================================================
    # GUARDAR MODELO
    # ========================================================

    def guardar_modelo(
        self,
        archivo="modelo_q.pkl"
    ):

        self.agente.guardar(
            archivo
        )

    # ========================================================
    # CARGAR MODELO
    # ========================================================

    def cargar_modelo(
        self,
        archivo="modelo_q.pkl"
    ):

        if self.agente is None:
            self.agente = (
                QLearningAgent()
            )

        self.agente.cargar(
            archivo
        )

    # ========================================================
    # REINICIAR PARTIDA
    # ========================================================

    def reiniciar(self):

        self.gestor.reiniciar()

    # ========================================================
    # EJECUTAR IA
    # ========================================================

    def ejecutar_ia(
        self,
        pasos_maximos=500
    ):

        return (
            self.entrenador
            .ejecutar_modelo(
                pasos_maximos
            )
        )

    # ========================================================
    # MOVER MANUALMENTE
    # ========================================================

    def mover_jugador(
        self,
        accion
    ):

        self.gestor.ejecutar_turno(
            accion
        )

    # ========================================================
    # OBTENER POSICIONES
    # ========================================================

    def posicion_jugador(self):

        return (
            self.gestor.jugador.posicion()
        )

    def posicion_enemigo(self):

        return (
            self.gestor.enemigo.posicion()
        )

    def posicion_bandera_jugador(self):

        return (
            self.gestor
            .bandera_jugador
            .posicion
        )

    def posicion_bandera_enemigo(self):

        return (
            self.gestor
            .bandera_enemigo
            .posicion
        )

    # ========================================================
    # ESTADO
    # ========================================================

    def obtener_estado(self):

        return (
            self.gestor
            .obtener_estado_jugador()
        )

    # ========================================================
    # GANADOR
    # ========================================================

    def ganador(self):

        return self.gestor.ganador

    # ========================================================
    # CANON
    # ========================================================

    def canon_activo(self):

        return (
            self.gestor
            .canon
            .activo
        )

    def casillas_bombardeadas(self):

        return (
            self.gestor
            .canon
            .casillas_bombardeadas
        )

    # ========================================================
    # MAPA
    # ========================================================

    def obtener_grid(self):

        return self.mapa.grid

    # ========================================================
    # DIMENSIONES
    # ========================================================

    def filas(self):
        return self.mapa.filas

    def columnas(self):
        return self.mapa.columnas


# ============================================================
# EJEMPLO DE USO
# ============================================================

if __name__ == "__main__":

    entorno = Entorno()

    entorno.generar_mapa()

    print("\nMAPA\n")

    entorno.mapa.mostrar()

    print("\nENTRENANDO...\n")

    entorno.entrenar(
        epocas=10000,
        pasos_maximos=300
    )

    entorno.guardar_modelo(
        "modelo_q.pkl"
    )

    print(
        "\nModelo guardado correctamente\n"
    )

    historial = (
        entorno.ejecutar_ia(
            pasos_maximos=300
        )
    )

    print(
        "\nEstados recorridos:\n"
    )

    for estado in historial:

        print(estado)

    print(
        "\nGanador:",
        entorno.ganador()
    )
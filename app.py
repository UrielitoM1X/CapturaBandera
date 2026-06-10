# app.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from qlearning import Mapa, GestorPartida

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Forzado a 12x12 para zona central jugable limpia de 10x10
mapa_juego = Mapa(filas=12, columnas=12)
partida = GestorPartida(mapa_juego)

def obtener_contexto():
    estado = partida.exportar_estado()
    return {
        "grid": estado["grid"],
        "filas": int(estado["filas"]),
        "columnas": int(estado["columnas"]),
        "ganador": estado["ganador"],
        "pos_j": estado["posicion_jugador"],
        "pos_e": estado["posicion_enemigo"],
        "puntos_accion": estado["puntos_accion"],
        "turno": estado["turno"]
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    contexto_render = obtener_contexto()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=contexto_render
    )

@app.post("/reiniciar")
async def reiniciar_mapa():
    partida.mapa.generar()
    partida.reiniciar()
    return RedirectResponse(url="/", status_code=303)

@app.post("/mover/{direccion}")
async def mover(direccion: int):
    partida.mover_jugador(direccion)
    return RedirectResponse(url="/", status_code=303)

@app.post("/entrenar")
async def entrenar_paso():
    """Modo Entrenamiento Puro: B entrena en la oscuridad contra la esquina superior izquierda."""
    print("[IA] Ejecutando 1500 episodios de auto-entrenamiento (Bot vs Esquina Superior)...")
    for _ in range(1500):
        partida.entrenar_episodio()
    print("[IA] Cerebro de B actualizado correctamente.")
    return RedirectResponse(url="/", status_code=303)
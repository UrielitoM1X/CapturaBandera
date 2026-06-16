@echo off
title Lanzador del Proyecto de IA
echo ========================================
echo   Iniciando el entorno de desarrollo...
echo ========================================
echo.

REM Asegura que la consola se ubique en la carpeta donde está este archivo .bat
cd /d "%~dp0"

REM 1. Verifica si el entorno virtual ya existe
if not exist venv\ (
    echo [INFO] No se encontro el entorno virtual. Creando uno nuevo...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual. Asegurate de tener Python instalado y agregado al PATH.
        pause
        exit /b
    )
    echo [OK] Entorno virtual creado exitosamente.
)

REM 2. Activa el entorno virtual
call venv\Scripts\activate.bat

REM 3. Instala o actualiza las dependencias
echo [INFO] Verificando dependencias en requirements.txt...
pip install -r requirements.txt -q
echo [OK] Dependencias listas.
echo.

REM 4. Ejecuta el juego asegurando que detecte la carpeta "codes"
echo [INFO] Lanzando el entorno...
set PYTHONPATH=%cd%
python main.py

REM Desactiva el entorno cuando el programa se cierre
deactivate
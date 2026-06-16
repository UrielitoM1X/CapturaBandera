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

REM 3. Forzar la instalacion de pip (Soluciona el error de Python 3.13 sin pip)
echo [INFO] Comprobando el gestor de paquetes (pip)...
python -m ensurepip --upgrade >nul 2>&1

REM 4. Actualiza las herramientas base de Python
echo [INFO] Actualizando instaladores base...
python -m pip install --upgrade pip setuptools wheel

REM 5. Instala o actualiza las dependencias
echo [INFO] Instalando dependencias desde requirements.txt...
python -m pip install -r requirements.txt
echo.
echo [OK] Dependencias listas.
echo.

REM 6. Ejecuta el juego asegurando que detecte la carpeta "codes"
echo [INFO] Lanzando el entorno...
set PYTHONPATH=%cd%
python main.py

REM
echo.
echo [INFO] La ejecucion de Python ha terminado. Si el entorno no se abrio, lee el error de arriba.
pause

REM Desactiva el entorno
deactivate
@echo off
title Ciudad del Caos - Desarrollo
color 0A

echo.
echo ===================================================
echo           CIUDAD DEL CAOS - JUEGO DE CARTAS
echo ===================================================
echo.
echo Verificando dependencias y servicios...
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.7+ desde https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python está disponible

:: Verificar Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no está instalado o no está en el PATH
    echo Por favor instala Node.js 16+ desde https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js está disponible

echo.
echo Iniciando servicios...
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Iniciar backend en una nueva ventana
echo [INFO] Iniciando backend (WebSocket Server)...
start "Ciudad del Caos - Backend" cmd /c "cd backend && if not exist venv (python -m venv venv) && call venv\Scripts\activate.bat && pip install -q -r requirements.txt && echo [BACKEND] Servidor iniciado en puerto 8000 && python run_server.py && pause"

:: Esperar un poco para que el backend se inicie
timeout /t 3 /nobreak >nul

:: Iniciar frontend en una nueva ventana
echo [INFO] Iniciando frontend (React + Vite)...
start "Ciudad del Caos - Frontend" cmd /c "cd frontend && npm install -s && echo [FRONTEND] Servidor de desarrollo iniciado en puerto 3000 && npm run dev && pause"

echo.
echo [INFO] Ambos servicios están iniciándose...
echo [INFO] Backend: http://localhost:8000 (WebSocket)
echo [INFO] Frontend: http://localhost:3000
echo.
echo Una vez que ambos servicios estén corriendo:
echo 1. Abre tu navegador en http://localhost:3000
echo 2. Crea un nuevo juego o únete a uno existente
echo 3. ¡Disfruta jugando Ciudad del Caos!
echo.

:: Esperar 5 segundos y abrir el navegador
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
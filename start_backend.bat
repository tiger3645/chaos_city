@echo off
echo Iniciando Ciudad del Caos - Backend
echo ======================================

cd /d "%~dp0backend"

echo Verificando entorno virtual...
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Instalando/actualizando dependencias...
pip install -r requirements.txt

echo Iniciando servidor WebSocket en puerto 8000...
python run_server.py

pause
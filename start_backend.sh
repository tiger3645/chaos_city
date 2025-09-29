#!/bin/bash

echo "Iniciando Ciudad del Caos - Backend"
echo "===================================="

cd "$(dirname "$0")/backend"

echo "Verificando entorno virtual..."
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Instalando/actualizando dependencias..."
pip install -r requirements.txt

echo "Iniciando servidor WebSocket en puerto 8000..."
python run_server.py
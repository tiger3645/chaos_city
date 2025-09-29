#!/bin/bash

echo "Iniciando Ciudad del Caos - Frontend"
echo "===================================="

cd "$(dirname "$0")/frontend"

echo "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "Error: Node.js no está instalado. Por favor instala Node.js 16+ desde https://nodejs.org"
    exit 1
fi

echo "Instalando/actualizando dependencias..."
npm install

echo "Iniciando servidor de desarrollo en puerto 3000..."
npm run dev
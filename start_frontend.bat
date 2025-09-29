@echo off
echo Iniciando Ciudad del Caos - Frontend
echo ======================================

cd /d "%~dp0frontend"

echo Verificando Node.js...
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js no está instalado. Por favor instala Node.js 16+ desde https://nodejs.org
    pause
    exit /b 1
)

echo Instalando/actualizando dependencias...
npm install

echo Iniciando servidor de desarrollo en puerto 3000...
npm run dev

pause
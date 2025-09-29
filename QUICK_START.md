# Scripts de Inicio Rápido

## Windows (PowerShell)

### Iniciar Backend
```powershell
# Navegar al directorio del backend
cd backend

# Crear entorno virtual (solo la primera vez)
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# Ejecutar servidor
python run_server.py
```

### Iniciar Frontend
```powershell
# En otra terminal, navegar al directorio del frontend
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

## Linux/Mac

### Iniciar Backend
```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual (solo la primera vez)
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# Ejecutar servidor
python run_server.py
```

### Iniciar Frontend
```bash
# En otra terminal, navegar al directorio del frontend
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

## Acceso

- **Frontend**: http://localhost:3000
- **Backend WebSocket**: ws://localhost:8000

## Solución de Problemas

### Backend no inicia
- Verificar que Python 3.7+ esté instalado
- Verificar que el entorno virtual esté activado
- Reinstalar dependencias: `pip install -r requirements.txt`

### Frontend no inicia
- Verificar que Node.js 16+ esté instalado
- Limpiar cache: `npm cache clean --force`
- Eliminar node_modules y reinstalar: `rm -rf node_modules && npm install`

### No se puede conectar WebSocket
- Verificar que el backend esté corriendo en puerto 8000
- Verificar que no haya firewall bloqueando la conexión
- Comprobar en la consola del navegador si hay errores de conexión
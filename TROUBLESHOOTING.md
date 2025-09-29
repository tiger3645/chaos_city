# 🔧 Solución de Problemas - Ciudad del Caos

## WebSocket se conecta y desconecta constantemente

### Posibles causas y soluciones:

#### 1. **Servidor Backend no está corriendo**
```bash
# Verificar si el servidor está corriendo
netstat -an | findstr 8000

# Si no hay respuesta, iniciar el backend:
cd backend
python run_server.py
```

#### 2. **Firewall o Antivirus bloqueando la conexión**
- Agregar excepción para Python.exe y Node.js
- Permitir conexiones en puerto 8000 (backend) y 3000 (frontend)
- Temporalmente desactivar firewall para probar

#### 3. **Puerto 8000 ocupado por otra aplicación**
```bash
# Windows: Ver qué proceso usa el puerto 8000
netstat -ano | findstr :8000

# Matar proceso si es necesario (reemplazar PID)
taskkill /PID <PID> /F
```

#### 4. **Dependencias faltantes**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd frontend
npm install
```

#### 5. **Problemas de red local**
- Probar con `127.0.0.1` en lugar de `localhost`
- Modificar `frontend/src/config.ts`:
```javascript
WEBSOCKET: {
  URL: 'ws://127.0.0.1:8000',
  // ...
}
```

#### 6. **Límites de conexión del navegador**
- Cerrar otras pestañas que usen WebSockets
- Reiniciar el navegador
- Probar en modo incógnito

#### 7. **Configuración de reconexión muy agresiva**
En `frontend/src/config.ts`, ajustar:
```javascript
WEBSOCKET: {
  RECONNECT_ATTEMPTS: 3,        // Reducir intentos
  RECONNECT_DELAY_BASE: 2000,   // Aumentar delay inicial
  RECONNECT_DELAY_MAX: 30000,   // Aumentar delay máximo
}
```

## Otros Problemas Comunes

### El frontend no carga
```bash
# Limpiar cache de npm
npm cache clean --force

# Reinstalar dependencias
rm -rf node_modules
npm install

# Verificar puerto 3000 libre
netstat -an | findstr 3000
```

### Error "Cannot find module"
```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Juego se cuelga al crear partida
1. Verificar logs del backend en la consola
2. Abrir DevTools del navegador (F12) → Console
3. Buscar errores rojos
4. Verificar que ambos jugadores tengan nombres válidos

### Performance lenta
1. Cerrar otras aplicaciones pesadas
2. En `frontend/src/config.ts`:
```javascript
DEBUG: {
  WEBSOCKET_LOGS: false,    // Desactivar logs
  GAME_STATE_LOGS: false,
  PERFORMANCE_LOGS: false,
}
```

## Debugging Avanzado

### Habilitar logs detallados
En `frontend/src/config.ts`:
```javascript
DEBUG: {
  WEBSOCKET_LOGS: true,
  GAME_STATE_LOGS: true,
  PERFORMANCE_LOGS: true,
}
```

### Verificar estado del WebSocket en el navegador
1. Abrir DevTools (F12)
2. Ir a Network → WS (WebSocket)
3. Verificar mensajes enviados/recibidos
4. Estado de conexión debe ser "Open"

### Logs del servidor backend
El servidor muestra logs en la consola:
- `Client connected/disconnected`
- `Message received/sent`
- Errores de parsing JSON

### Herramientas útiles
```bash
# Monitorear conexiones de red
netstat -an | findstr ":8000\|:3000"

# Verificar procesos Python/Node
tasklist | findstr "python\|node"

# Test manual del WebSocket
# Usar herramientas como WebSocket King o extensiones de browser
```

## Configuración Recomendada para Desarrollo

### Para desarrollo local estable:
```javascript
// frontend/src/config.ts
export const CONFIG = {
  WEBSOCKET: {
    URL: 'ws://localhost:8000',
    RECONNECT_ATTEMPTS: 3,
    RECONNECT_DELAY_BASE: 1500,
    RECONNECT_DELAY_MAX: 15000,
    PING_INTERVAL: 30000,
    CONNECTION_TIMEOUT: 10000,
  },
  DEBUG: {
    WEBSOCKET_LOGS: true,  // Para ver problemas
    GAME_STATE_LOGS: false,
    PERFORMANCE_LOGS: false,
  }
};
```

### Para producción:
```javascript
// frontend/src/config.ts
export const CONFIG = {
  WEBSOCKET: {
    URL: 'wss://tu-servidor.com',  // HTTPS/WSS
    RECONNECT_ATTEMPTS: 5,
    RECONNECT_DELAY_BASE: 1000,
    RECONNECT_DELAY_MAX: 30000,
    PING_INTERVAL: 60000,
    CONNECTION_TIMEOUT: 15000,
  },
  DEBUG: {
    WEBSOCKET_LOGS: false,
    GAME_STATE_LOGS: false, 
    PERFORMANCE_LOGS: false,
  }
};
```

## Contacto para Soporte

Si los problemas persisten:
1. Revisar los logs de ambos servicios
2. Documentar pasos exactos para reproducir el problema
3. Incluir información del sistema (OS, versiones de Python/Node)
4. Screenshots de errores en consola
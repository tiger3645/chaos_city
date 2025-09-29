# 🧪 Testing Guide - Correcciones Implementadas

## Problemas Solucionados:

### ✅ 1. "Loading game..." infinito
**Causa:** El gameState llegaba después del mensaje de game_created/joined_game
**Solución:** Separé el manejo de mensajes WebSocket del procesamiento del gameState en useEffects independientes

### ✅ 2. Estado de conexión en barra superior
**Antes:** Barra fija en la parte superior de toda la pantalla
**Ahora:** Div flotante en la esquina superior derecha con fondo semi-transparente

### ✅ 3. Persistencia en localStorage
**Implementado:** 
- Hook `useGameSession` para manejar sesiones
- Auto-guardado del estado del juego
- Auto-recuperación al recargar la página
- Expiración automática después de 24 horas

## Cómo Probar:

### Prueba 1: Creación de juego
1. Abrir http://localhost:3000
2. Crear un nuevo juego con nombres y facciones
3. Verificar que sale del "Loading game..." y muestra el tablero
4. Verificar que aparece "Nuevo Juego" en esquina superior izquierda

### Prueba 2: Estado de conexión
1. Verificar que el estado de conexión aparece en esquina superior derecha
2. Cerrar el backend (`Ctrl+C` en la terminal del servidor)
3. Verificar que muestra "Desconectado" y botón "Reintentar"
4. Reiniciar backend y verificar reconexión automática

### Prueba 3: Persistencia
1. Crear un juego exitosamente
2. Recargar la página (`F5` o `Ctrl+R`)
3. Verificar que automáticamente intenta reconectarse al juego
4. Verificar que mantiene el player ID y game ID

### Prueba 4: Sesión expirada
1. Crear juego y cerrarlo
2. Simular paso de tiempo modificando localStorage:
   ```javascript
   // En DevTools Console:
   let session = JSON.parse(localStorage.getItem('chaosCity_gameSession'));
   session.timestamp = Date.now() - (25 * 60 * 60 * 1000); // 25 horas atrás
   localStorage.setItem('chaosCity_gameSession', JSON.stringify(session));
   location.reload();
   ```
3. Verificar que vuelve a la pantalla de setup

## Debug Info:

### Consola del Navegador
Ahora muestra logs detallados:
- ✅ "Received message: game_created"
- ✅ "Game created, ID: [uuid]"
- ✅ "Processing gameState with players: [player-ids]"
- ✅ "Assigning player ID: [player-id]"

### LocalStorage
Puedes inspeccionar en DevTools > Application > Local Storage:
```json
{
  "gameId": "uuid-del-juego",
  "playerId": "uuid-del-jugador",
  "view": "game",
  "timestamp": 1727548800000
}
```

## Comandos de Test:

```bash
# Terminal 1: Backend
cd backend
python run_server.py

# Terminal 2: Frontend  
cd frontend
npm run dev

# Abrir navegador
start http://localhost:3000
```

## Errores Conocidos y Soluciones:

### Si persiste "Loading game...":
1. Verificar logs en consola
2. Verificar que backend está corriendo en puerto 8000
3. Limpiar localStorage: `localStorage.clear()`
4. Hacer hard refresh: `Ctrl+Shift+R`

### Si no aparece el estado de conexión:
1. Verificar que no hay errores CSS
2. Probar en modo incógnito
3. Verificar z-index en DevTools

### Si no persiste la sesión:
1. Verificar que localStorage no está deshabilitado
2. Verificar en DevTools > Application > Local Storage
3. Probar en navegador diferente

## Next Steps:
- [ ] Añadir notificaciones toast para feedback visual
- [ ] Mejorar manejo de errores de conexión
- [ ] Añadir indicador de "reconectando..." más visible
- [ ] Implementar sistema de salas/lobbies
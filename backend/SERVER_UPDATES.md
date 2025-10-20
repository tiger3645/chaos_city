# 🔄 Actualizaciones del Servidor WebSocket

## Resumen de Cambios

El servidor WebSocket ha sido actualizado para soportar el nuevo **sistema de efectos de cartas**. Los cambios principales incluyen:

1. ✅ Nuevos tipos de retorno (Dict en lugar de bool)
2. ✅ Soporte para efectos multi-paso
3. ✅ Endpoints nuevos para continuar efectos y obtener stats
4. ✅ Broadcast mejorado con exclusión opcional

---

## 📡 Cambios en Endpoints Existentes

### 1. `play_card` - Ahora retorna información completa

**Antes:**
```json
{
  "type": "card_played",
  "player_id": "p1",
  "card_game_id": "card_123",
  "zone": "fighter"
}
```

**Ahora:**
```json
{
  "type": "card_played",
  "player_id": "p1",
  "card_game_id": "card_123",
  "zone": "fighter",
  "message": "Card played successfully",
  "requires_choice": false,
  "choices": [],
  "revealed_info": null,
  "effect_id": null
}
```

**Efecto Multi-Paso:**
```json
{
  "type": "card_played",
  "player_id": "p1",
  "card_game_id": "card_123",
  "zone": null,
  "message": "Choose a card to destroy",
  "requires_choice": true,
  "choices": [
    {
      "id": "card_456",
      "name": "Enemy Fighter",
      "description": "Fighter card in opponent's field"
    }
  ],
  "revealed_info": null,
  "effect_id": "effect_789"
}
```

**Información Revelada:**
```json
{
  "type": "card_played",
  "player_id": "p1",
  "card_game_id": "card_123",
  "zone": null,
  "message": "Revealed opponent's hand",
  "requires_choice": false,
  "choices": [],
  "revealed_info": {
    "type": "hand",
    "cards": [
      {"id": "card_111", "name": "Hidden Card 1"},
      {"id": "card_222", "name": "Hidden Card 2"}
    ]
  },
  "effect_id": null
}
```

### 2. `attack` - Retorna información mejorada

**Respuesta mejorada:**
```json
{
  "type": "attack_result",
  "result": {
    "success": true,
    "message": "Attack successful! Defender destroyed",
    "attacker_effective_attack": 5,
    "attacker_effective_defense": 3,
    "defender_effective_attack": 2,
    "defender_effective_defense": 4,
    "attacker_survived": true,
    "defender_survived": false,
    "triggered_effects": [
      "Berserker Rage triggered: +2 ATK",
      "Defender destroyed"
    ]
  }
}
```

### 3. `next_phase` - Notifica efectos disparados

**Respuesta con efectos:**
```json
{
  "type": "effects_triggered",
  "effects": [
    "Start of turn: Drew 1 card",
    "Regeneration: Healed 1 reputation",
    "Environment effect: All fighters get +1 ATK"
  ],
  "message": "Phase changed to ACTION"
}
```

---

## 🆕 Nuevos Endpoints

### 1. `continue_effect` - Continuar efectos multi-paso

**Request:**
```json
{
  "type": "continue_effect",
  "player_id": "p1",
  "effect_id": "effect_789",
  "chosen_value": "card_456"
}
```

**Response (Completado):**
```json
{
  "type": "effect_continued",
  "message": "Card destroyed successfully",
  "requires_choice": false,
  "choices": [],
  "revealed_info": null,
  "effect_id": null
}
```

**Response (Requiere más elecciones):**
```json
{
  "type": "effect_continued",
  "message": "Choose where to place the card",
  "requires_choice": true,
  "choices": ["fighter", "gunslinger", "talker"],
  "revealed_info": null,
  "effect_id": "effect_789"
}
```

### 2. `get_card_stats` - Obtener stats efectivos

**Request:**
```json
{
  "type": "get_card_stats",
  "card_game_id": "card_123"
}
```

**Response:**
```json
{
  "type": "card_stats",
  "card_game_id": "card_123",
  "stats": {
    "attack": 5,
    "defense": 4,
    "base_attack": 3,
    "base_defense": 3,
    "modifiers": [
      {"source": "Police Station", "attack": +2, "defense": +1},
      {"source": "Battle Cry", "attack": 0, "defense": 0}
    ]
  }
}
```

---

## 🎮 Flujo de Uso Completo

### Caso 1: Carta Simple (Sin Efectos)

```
Cliente → Servidor: play_card
Servidor → Cliente: card_played (requires_choice = false)
Servidor → Todos: game_state
```

### Caso 2: Carta con Efecto Multi-Paso

```
Cliente → Servidor: play_card
Servidor → Cliente: card_played (requires_choice = true, choices = [...])
Cliente → Servidor: continue_effect (chosen_value = ...)
Servidor → Cliente: effect_continued (requires_choice = false)
Servidor → Todos: game_state
```

### Caso 3: Carta con Múltiples Pasos

```
Cliente → Servidor: play_card
Servidor → Cliente: card_played (requires_choice = true, step 1)
Cliente → Servidor: continue_effect
Servidor → Cliente: effect_continued (requires_choice = true, step 2)
Cliente → Servidor: continue_effect
Servidor → Cliente: effect_continued (requires_choice = false, complete)
Servidor → Todos: game_state
```

### Caso 4: Carta que Revela Información

```
Cliente → Servidor: play_card
Servidor → Cliente: card_played (revealed_info = {...})
Servidor → Todos: game_state
```

### Caso 5: Ataque con Efectos

```
Cliente → Servidor: attack
Servidor → Todos: attack_result (con stats efectivos y triggers)
Servidor → Todos: game_state
```

### Caso 6: Cambio de Fase con Triggers

```
Cliente → Servidor: next_phase
Servidor → Todos: effects_triggered (lista de efectos)
Servidor → Todos: game_state
```

---

## 🛠️ Implementación en Cliente

### Ejemplo: Manejar Efecto Multi-Paso

```typescript
// Cuando el jugador juega una carta
async function playCard(cardId: string, zone?: string) {
  ws.send(JSON.stringify({
    type: "play_card",
    player_id: playerId,
    card_game_id: cardId,
    zone: zone
  }));
}

// Listener de mensajes
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "card_played") {
    if (data.requires_choice) {
      // Mostrar modal con opciones
      showChoiceModal({
        message: data.message,
        choices: data.choices,
        onChoose: (choice) => {
          continueEffect(data.effect_id, choice);
        }
      });
    } else if (data.revealed_info) {
      // Mostrar información revelada
      showRevealedInfo(data.revealed_info);
    } else {
      // Carta jugada normalmente
      showMessage(data.message);
    }
  }
  
  if (data.type === "effect_continued") {
    if (data.requires_choice) {
      // Otro paso del efecto
      showChoiceModal({
        message: data.message,
        choices: data.choices,
        onChoose: (choice) => {
          continueEffect(data.effect_id, choice);
        }
      });
    } else {
      // Efecto completado
      showMessage(data.message);
    }
  }
};

// Continuar efecto
async function continueEffect(effectId: string, choice: any) {
  ws.send(JSON.stringify({
    type: "continue_effect",
    player_id: playerId,
    effect_id: effectId,
    chosen_value: choice
  }));
}
```

### Ejemplo: Mostrar Stats Efectivos

```typescript
async function getCardStats(cardId: string) {
  ws.send(JSON.stringify({
    type: "get_card_stats",
    card_game_id: cardId
  }));
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "card_stats") {
    const stats = data.stats;
    
    // Mostrar stats con modificadores
    displayCardStats({
      attack: stats.attack,
      defense: stats.defense,
      baseAttack: stats.base_attack,
      baseDefense: stats.base_defense,
      modifiers: stats.modifiers
    });
  }
};
```

### Ejemplo: Manejar Ataque con Efectos

```typescript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "attack_result") {
    const result = data.result;
    
    // Mostrar animación de ataque
    showAttackAnimation({
      attackerAttack: result.attacker_effective_attack,
      attackerDefense: result.attacker_effective_defense,
      defenderAttack: result.defender_effective_attack,
      defenderDefense: result.defender_effective_defense,
      attackerSurvived: result.attacker_survived,
      defenderSurvived: result.defender_survived
    });
    
    // Mostrar efectos disparados
    if (result.triggered_effects) {
      result.triggered_effects.forEach(effect => {
        showEffectNotification(effect);
      });
    }
  }
};
```

---

## 📋 Checklist de Implementación Frontend

### Funcionalidad Básica
- [ ] Actualizar `playCard` para manejar respuesta Dict
- [ ] Implementar modal para efectos multi-paso
- [ ] Implementar `continueEffect` para completar efectos
- [ ] Actualizar ataque para mostrar stats efectivos
- [ ] Mostrar efectos disparados en cambio de fase

### UI/UX
- [ ] Modal/dialog para elección de objetivos
- [ ] Animación de efectos
- [ ] Mostrar información revelada (mano del oponente)
- [ ] Indicadores de stats efectivos en cartas
- [ ] Iconos de efectos activos en cartas
- [ ] Tooltip con detalles de modificadores
- [ ] Notificaciones de efectos disparados

### Funcionalidad Avanzada
- [ ] Implementar `getCardStats` en hover de cartas
- [ ] Resaltar objetivos válidos para efectos
- [ ] Previsualización de resultado de ataque
- [ ] Log de efectos en historial del juego
- [ ] Animación de modificadores aplicándose

---

## 🔧 Testing del Servidor

Para probar el servidor actualizado:

```bash
cd backend
python run_server.py
```

Usa un cliente WebSocket de prueba o el frontend actualizado para probar:

1. **Crear juego y unir dos jugadores**
2. **Jugar carta simple** - Verificar que funciona normal
3. **Jugar carta de efecto** - Verificar modal de elección
4. **Continuar efecto** - Verificar múltiples pasos
5. **Atacar con modificadores** - Verificar stats efectivos
6. **Cambiar fase** - Verificar triggers disparados
7. **Obtener stats de carta** - Verificar modificadores

---

## 📊 Compatibilidad

### Cambios Breaking
- ❌ `play_card` ya no retorna simple `card_played`
- ❌ `attack` retorna información más detallada
- ❌ `next_phase` ahora envía `effects_triggered`

### Backwards Compatibility
- ✅ Mensajes antiguos todavía funcionan (solo respuestas cambiaron)
- ✅ Clientes antiguos recibirán game_state igual que antes
- ⚠️ Clientes antiguos ignorarán campos nuevos automáticamente

---

## 🚀 Próximos Pasos

1. **Frontend:** Implementar UI para efectos multi-paso
2. **Testing:** Probar todos los flujos de efectos
3. **UI/UX:** Diseñar visualización de efectos activos
4. **Performance:** Optimizar broadcast de game_state
5. **Logging:** Agregar logs de efectos para debugging

---

**Fecha:** 20 de octubre de 2025  
**Versión:** 2.0  
**Estado:** ✅ Servidor actualizado y funcionando

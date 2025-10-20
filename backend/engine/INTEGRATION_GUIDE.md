# Integración del Sistema de Efectos - Guía de Uso

## 🎯 Resumen de Cambios

El motor del juego (`engine/base.py`) ha sido completamente integrado con el sistema de efectos, permitiendo que todas las cartas ejecuten sus efectos correctamente y que los modificadores de estadísticas se apliquen automáticamente.

## 🔄 Cambios Principales

### 1. Importaciones y Inicialización

El motor ahora importa y registra automáticamente todos los efectos al inicializarse:

```python
from engine.effects import (
    EffectContext,
    EffectTrigger,
    effect_manager,
    EffectResult
)
from engine.card_effects import (
    get_card_effect,
    get_environment_effect,
    get_leader_passive_effect,
    register_all_card_effects
)
```

### 2. Método `play_card()` - Actualizado ✅

**Antes:** Retornaba `bool`  
**Ahora:** Retorna `Dict[str, Any]` con información detallada

#### Nuevas Características:

- **Cartas de Efecto:** Se ejecutan automáticamente usando el sistema de efectos
- **Cartas de Ambiente:** Activan efectos pasivos que modifican estadísticas
- **Cartas de Líder:** Activan habilidades pasivas automáticamente
- **Efectos Multi-Paso:** Soporta efectos que requieren elección del jugador

#### Ejemplo de Retorno:

```python
{
    "success": True,
    "message": "Pedir refuerzos executed successfully",
    "requires_choice": False,  # True si necesita elección del jugador
    "choices": [],            # Lista de opciones si requires_choice=True
    "revealed_info": {},      # Información revelada (ej: mano del oponente)
    "next_step": None,        # ID del siguiente paso para multi-step
    "data": {"cards_drawn": 2}  # Datos adicionales del efecto
}
```

### 3. Método `continue_effect()` - NUEVO ✅

Permite continuar efectos multi-paso después de que el jugador haga una elección:

```python
def continue_effect(
    self,
    game_id: str,
    player_id: str,
    effect_id: str,
    chosen_value: Any
) -> Dict[str, Any]:
```

**Uso:**
```python
# Paso 1: Jugar carta que requiere elección
result = engine.play_card(game_id, player_id, card_id)

if result["requires_choice"]:
    # Mostrar opciones al jugador
    choices = result["choices"]
    
    # Paso 2: Continuar con la elección del jugador
    result2 = engine.continue_effect(
        game_id,
        player_id,
        effect_id,
        chosen_card_id  # Lo que el jugador eligió
    )
```

### 4. Método `attack()` - Mejorado ✅

**Nuevas Características:**

- **Modificadores de Estadísticas:** Calcula ATK/DEF efectivos automáticamente
- **Triggers de Ataque:** Dispara efectos `ON_ATTACK`
- **Efectos Especiales:** Soporta "ignorar defensa" y otros efectos de ataque
- **Triggers de Destrucción:** Dispara `ON_DESTROY`, `ON_ALLY_DESTROY`, `ON_ENEMY_DESTROY`
- **Efectos de Prevención:** Soporta prevención de daño directo
- **Habilidades Pasivas:** Como Don Vito ganando reputación al destruir aliado

**Cambio de Firma:**
```python
# Antes
def attack(self, game_id, player_id, attacker_id, defender_id, target_zone)

# Ahora
def attack(self, game_id, player_id, attacker_id, defender_id: Optional[str], target_zone)
# defender_id puede ser None para ataque directo
```

#### Ejemplo de Retorno:

```python
{
    "success": True,
    "message": "Agentes de patrulla destroyed Matones a sueldo",
    "destroyed": "Matones a sueldo",
    "attacker_stats": "3/3"  # ATK/DEF con modificadores incluidos
}
```

### 5. Método `next_phase()` - Mejorado ✅

**Antes:** Retornaba `bool`  
**Ahora:** Retorna `Dict[str, Any]` con información de triggers

**Nuevas Características:**

- **Triggers de Turno:** Dispara `ON_TURN_START` y `ON_TURN_END`
- **Efectos Automáticos:** Ejecuta efectos pasivos y asíncronos
- **Mensajes de Efectos:** Retorna lista de efectos que se dispararon

#### Ejemplo de Retorno:

```python
{
    "success": True,
    "phase": "draw",
    "turn": 2,
    "current_player": "Jugador 2",
    "message": "Turn changed to Jugador 2",
    "triggered_effects": [
        "Detective Marlowe mira la mano del rival",
        "Efecto temporal expiró"
    ]
}
```

### 6. Método `get_card_effective_stats()` - NUEVO ✅

Obtiene las estadísticas efectivas de una carta incluyendo modificadores:

```python
def get_card_effective_stats(
    self,
    game_id: str,
    card_game_id: str
) -> Optional[Dict[str, int]]:
```

**Retorna:**
```python
{
    "attack": 4,        # ATK efectivo
    "defense": 4,       # DEF efectivo
    "base_attack": 3,   # ATK base
    "base_defense": 3,  # DEF base
    "attack_mod": 1,    # Modificador de ATK
    "defense_mod": 1    # Modificador de DEF
}
```

**Uso:**
```python
stats = engine.get_card_effective_stats(game_id, card_game_id)
if stats:
    print(f"ATK: {stats['attack']} (base: {stats['base_attack']} + {stats['attack_mod']})")
```

### 7. Método `end_game()` - NUEVO ✅

Finaliza un juego y limpia todos los efectos:

```python
def end_game(self, game_id: str) -> bool:
```

**Importante:** Siempre llama a este método cuando un juego termina para liberar recursos.

## 📋 Flujos de Trabajo Actualizados

### Flujo 1: Jugar Carta de Efecto Simple

```python
# Jugador juega "Pedir refuerzos" (roba 2 cartas)
result = engine.play_card(game_id, player_id, card_game_id)

if result["success"]:
    print(result["message"])  # "Se robaron 2 cartas"
    # Actualizar UI con las nuevas cartas
```

### Flujo 2: Jugar Carta de Efecto Multi-Paso

```python
# Jugador juega "Tácticas de interrogatorio" (ver mano y descartar)
result = engine.play_card(game_id, player_id, card_game_id)

if result["success"] and result["requires_choice"]:
    # Paso 1: Mostrar opciones al jugador
    choices = result["choices"]
    # choices = [{"game_id": "...", "name": "Carta 1", ...}, ...]
    
    # Jugador elige una carta
    chosen_card_id = show_choices_to_player(choices)
    
    # Paso 2: Continuar efecto con la elección
    result2 = engine.continue_effect(
        game_id,
        player_id,
        result["next_step"],  # ID del efecto
        chosen_card_id
    )
    
    if result2["success"]:
        print(result2["message"])  # "Jugador 2 descartó Carta X"
```

### Flujo 3: Jugar Carta de Ambiente

```python
# Jugador juega "Barricadas improvisadas" (+1 DEF a luchadores)
result = engine.play_card(game_id, player_id, card_game_id)

if result["success"]:
    print(result["message"])  # "Barricadas improvisadas is now active"
    
    # Ahora todos los luchadores tienen +1 DEF automáticamente
    # Verificar stats de un luchador:
    stats = engine.get_card_effective_stats(game_id, fighter_card_id)
    print(f"DEF: {stats['defense']}")  # Mostrará DEF base + 1
```

### Flujo 4: Atacar con Modificadores

```python
# Atacar con carta que tiene modificadores activos
result = engine.attack(
    game_id,
    player_id,
    attacker_id,
    defender_id,
    target_zone
)

if result["success"]:
    print(result["message"])
    print(f"Stats del atacante: {result['attacker_stats']}")
    
    if "destroyed" in result:
        print(f"¡{result['destroyed']} fue destruido!")
        # Los triggers ON_DESTROY se ejecutan automáticamente
```

### Flujo 5: Ataque Directo con Prevención

```python
# Intentar ataque directo
result = engine.attack(
    game_id,
    player_id,
    attacker_id,
    None,  # None = ataque directo
    target_zone
)

if result.get("prevented"):
    print("¡El ataque fue prevenido!")
    # Por ejemplo, por "Guardia antidisturbios"
else:
    print(f"Daño a reputación: {result['reputation_damage']}")
```

### Flujo 6: Cambio de Turno

```python
# Avanzar fase o cambiar turno
result = engine.next_phase(game_id)

if result["success"]:
    print(result["message"])
    
    # Si cambió de turno
    if "current_player" in result:
        print(f"Turno de: {result['current_player']}")
        print(f"Turno número: {result['turn']}")
        
        # Mostrar efectos que se dispararon
        for effect_msg in result.get("triggered_effects", []):
            print(f"  - {effect_msg}")
```

### Flujo 7: Verificar Stats con Modificadores

```python
# Obtener stats efectivos para mostrar en UI
stats = engine.get_card_effective_stats(game_id, card_game_id)

if stats:
    if stats["attack_mod"] != 0 or stats["defense_mod"] != 0:
        # Hay modificadores activos
        print(f"ATK: {stats['attack']} ({stats['base_attack']}+{stats['attack_mod']})")
        print(f"DEF: {stats['defense']} ({stats['base_defense']}+{stats['defense_mod']})")
    else:
        # Sin modificadores
        print(f"ATK: {stats['attack']}")
        print(f"DEF: {stats['defense']}")
```

## 🎮 Ejemplo Completo de Turno

```python
# INICIO DE TURNO
result = engine.next_phase(game_id)
for msg in result.get("triggered_effects", []):
    print(f"Efecto: {msg}")

# FASE DE ROBO
card = engine.draw_card(game_id, player_id)
if card:
    print(f"Robaste: {card.name}")

# FASE DE DESPLIEGUE
# Jugar carta de ambiente
result = engine.play_card(game_id, player_id, environment_card_id)
print(result["message"])

# Jugar carta de personaje
result = engine.play_card(game_id, player_id, character_card_id)
print(result["message"])

# Jugar carta de efecto
result = engine.play_card(game_id, player_id, effect_card_id)
if result["requires_choice"]:
    # Manejar elección del jugador
    chosen = get_player_choice(result["choices"])
    result = engine.continue_effect(game_id, player_id, effect_id, chosen)

print(result["message"])

# FASE DE ACCIÓN
# Verificar stats antes de atacar
attacker_stats = engine.get_card_effective_stats(game_id, attacker_id)
print(f"Atacante: {attacker_stats['attack']}/{attacker_stats['defense']}")

# Atacar
result = engine.attack(game_id, player_id, attacker_id, defender_id, zone)
print(result["message"])

if result.get("game_over"):
    print(f"¡{result['winner']} ganó!")
    engine.end_game(game_id)

# FIN DE TURNO
result = engine.next_phase(game_id)
```

## 🔍 Efectos Implementados por Tipo

### Efectos Inmediatos
- ✅ Robar cartas (DrawCardsEffect)
- ✅ Infligir daño (DealDamageEffect)
- ✅ Curar reputación (HealReputationEffect)
- ✅ Destruir cartas (DestroyCardEffect)
- ✅ Devolver a mano (ReturnToHandEffect)
- ✅ Descartar al azar (DiscardRandomEffect)
- ✅ Ver mano del oponente (RevealOpponentHandEffect)
- ✅ Intercambiar cartas (SwapRandomHandCardEffect)
- ✅ Destruir todas las cartas (DestroyAllCardsEffect)
- ✅ Y muchos más...

### Efectos Pasivos
- ✅ Modificadores de estadísticas (StatModifierEffect)
- ✅ Reacción a destrucción de aliados (OnAllyDestroyEffect)
- ✅ Efectos al inicio de turno (OnTurnStartEffect)
- ✅ Efectos de ambiente
- ✅ Habilidades de líder

### Efectos Asíncronos
- ✅ Modificadores temporales (DelayedStatModifierEffect)
- ✅ Prevención de ataques (PreventAttackEffect)
- ✅ Ignorar defensa (IgnoreDefenseEffect)
- ✅ Prevención de daño (PreventNextAttackEffect)

## 📊 Triggers Disponibles

El sistema responde automáticamente a estos eventos:

| Trigger | Cuándo se dispara | Ejemplo |
|---------|-------------------|---------|
| `ON_PLAY` | Al jugar una carta | Efectos de entrada |
| `ON_DESTROY` | Al destruirse una carta | Efectos de muerte |
| `ON_ALLY_DESTROY` | Al destruirse aliado | Don Vito gana reputación |
| `ON_ENEMY_DESTROY` | Al destruirse enemigo | Robar carta |
| `ON_TURN_START` | Inicio del turno | Detective Marlowe ve mano |
| `ON_TURN_END` | Fin del turno | Efectos temporales expiran |
| `ON_ATTACK` | Al atacar | Ignorar defensa |
| `ON_RECEIVE_DAMAGE` | Al recibir daño | Prevenir daño |
| `ON_DRAW` | Al robar carta | Efectos de robo |
| `ALWAYS` | Siempre activo | Modificadores de stats |

## 🚨 Cambios Importantes para el Servidor

### 1. Actualizar Endpoints

**Antes:**
```python
result = engine.play_card(game_id, player_id, card_id)
if result:  # bool
    return {"success": True}
```

**Ahora:**
```python
result = engine.play_card(game_id, player_id, card_id)
# result es un dict con toda la información
return result
```

### 2. Nuevo Endpoint para Multi-Paso

Necesitas añadir un nuevo endpoint para continuar efectos:

```python
@app.route("/continue_effect", methods=["POST"])
def continue_effect():
    data = request.json
    result = engine.continue_effect(
        data["game_id"],
        data["player_id"],
        data["effect_id"],
        data["chosen_value"]
    )
    return jsonify(result)
```

### 3. Actualizar Cliente para Multi-Paso

```javascript
// Jugar carta
const result = await playCard(cardId);

if (result.requires_choice) {
    // Mostrar modal con opciones
    const choice = await showChoiceModal(result.choices);
    
    // Continuar efecto
    const result2 = await continueEffect(
        result.next_step,
        choice
    );
}
```

### 4. Mostrar Stats Efectivos en UI

```javascript
// Al renderizar una carta en el campo
const stats = await getCardEffectiveStats(cardId);

if (stats.attack_mod !== 0 || stats.defense_mod !== 0) {
    // Mostrar con color diferente o indicador
    cardElement.innerHTML = `
        <div class="card">
            <span class="attack ${stats.attack_mod > 0 ? 'buffed' : 'debuffed'}">
                ${stats.attack}
            </span>
            /
            <span class="defense ${stats.defense_mod > 0 ? 'buffed' : 'debuffed'}">
                ${stats.defense}
            </span>
        </div>
    `;
}
```

## ⚠️ Notas Importantes

1. **Limpieza de Recursos:** Siempre llama a `end_game()` cuando un juego termina
2. **Efectos Multi-Paso:** Requieren interacción adicional del cliente
3. **Stats Efectivos:** Usa `get_card_effective_stats()` para mostrar stats correctos en UI
4. **Triggers Automáticos:** Los efectos se disparan automáticamente, no necesitas llamarlos manualmente
5. **Compatibilidad:** Los métodos antiguos todavía funcionan pero retornan tipos diferentes

## 🎯 Testing

Para probar el sistema integrado:

```python
# Crear juego
engine = GameEngine()
game_id, player1_id = engine.create_game("Player 1", Faction.POLICE)
player2_id = engine.join_game(game_id, "Player 2", Faction.MAFIA)

# Jugar carta con efecto
result = engine.play_card(game_id, player1_id, effect_card_id)
assert result["success"]
assert "message" in result

# Verificar modificadores
stats = engine.get_card_effective_stats(game_id, card_id)
assert stats["attack_mod"] >= 0

# Limpiar
engine.end_game(game_id)
```

## 🚀 Próximos Pasos

1. ✅ Sistema de efectos integrado
2. ✅ Modificadores de stats funcionando
3. ✅ Triggers automáticos implementados
4. ⏳ Actualizar servidor WebSocket
5. ⏳ Actualizar cliente para multi-paso
6. ⏳ Añadir UI para mostrar efectos activos
7. ⏳ Implementar animaciones de efectos
8. ⏳ Añadir sistema de descarte completo

## 📚 Recursos

- `engine/effects.py` - Sistema base de efectos
- `engine/card_effects.py` - Efectos específicos de cartas
- `engine/base.py` - Motor del juego (actualizado)
- `engine/EFFECTS_README.md` - Documentación completa
- `engine/effects_integration_example.py` - Ejemplos de uso

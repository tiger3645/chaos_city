# Sistema de Efectos - Chaos City

## Descripción General

El sistema de efectos proporciona una arquitectura flexible y extensible para implementar todos los tipos de efectos de cartas en Chaos City.

## Tipos de Efectos

### 1. Efectos Inmediatos (`ImmediateEffect`)
Efectos que se ejecutan una sola vez al activarse la carta.

**Ejemplos:**
- Robar cartas
- Infligir daño
- Destruir una carta
- Recuperar reputación

**Características:**
- Pueden requerir cartas objetivo (`requires_target=True`)
- Pueden requerir una elección del jugador (`requires_choice=True`)
- Pueden ser multi-paso (`is_multi_step=True`)

### 2. Efectos Pasivos (`PassiveEffect`)
Efectos que modifican estadísticas o reaccionan a eventos durante el juego.

**Ejemplos:**
- Modificadores de stats de cartas de ambiente
- Habilidades de líder que se activan con eventos
- Efectos que reaccionan a destrucciones

**Características:**
- Tienen un `trigger` que determina cuándo se activan
- Pueden tener duración limitada o permanente
- Se mantienen activos mientras la carta está en juego

### 3. Efectos Asíncronos (`AsyncEffect`)
Efectos que se activan una vez en el futuro.

**Ejemplos:**
- Modificadores de stats temporales (durante X turnos)
- Prevención del próximo ataque
- Efectos retardados

**Características:**
- Se activan en respuesta a un trigger específico
- Se ejecutan una sola vez y luego expiran
- Pueden tener duración en turnos

## Arquitectura

### Clases Base

```python
Effect (ABC)
├── ImmediateEffect
├── PassiveEffect
└── AsyncEffect
```

### Componentes Clave

#### `EffectContext`
Contiene toda la información necesaria para ejecutar un efecto:
- Estado del juego (`game_state`)
- Jugador que activa el efecto (`source_player_id`)
- Carta fuente (`source_card`)
- Objetivos opcionales (`target_card`, `target_player_id`)
- Trigger del evento (`trigger`)
- Datos adicionales (`additional_data`)

#### `EffectResult`
Resultado de la ejecución de un efecto:
- Éxito/fracaso (`success`)
- Mensaje descriptivo (`message`)
- Si requiere elección del jugador (`requires_choice`)
- Opciones disponibles (`choices`)
- Información revelada (`revealed_info`)
- Siguiente paso en efectos multi-paso (`next_step`)
- Datos adicionales (`data`)

#### `EffectManager`
Gestor centralizado que:
- Registra tipos de efectos
- Ejecuta efectos inmediatos
- Mantiene efectos pasivos y asíncronos activos
- Dispara efectos en respuesta a eventos
- Calcula modificadores de stats

## Uso Básico

### 1. Crear un Efecto Inmediato Simple

```python
from engine.effects import ImmediateEffect, EffectContext, EffectResult

class DrawCardsEffect(ImmediateEffect):
    def __init__(self, effect_id: str, num_cards: int):
        super().__init__(
            effect_id=effect_id,
            name=f"Robar {num_cards} cartas",
            description=f"Roba {num_cards} cartas del mazo"
        )
        self.num_cards = num_cards
    
    def can_execute(self, context: EffectContext) -> bool:
        player = self._get_player(context)
        return player is not None and len(player.deck) > 0
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        drawn = 0
        for _ in range(self.num_cards):
            if player.deck:
                card = player.deck.pop()
                player.hand.append(card)
                drawn += 1
        
        return EffectResult(
            success=True,
            message=f"Se robaron {drawn} cartas",
            data={"cards_drawn": drawn}
        )
```

### 2. Crear un Efecto Pasivo

```python
from engine.effects import PassiveEffect, EffectTrigger, StatModifierEffect
from models import Zone

# Efecto de ambiente: +1 DEF a todos los luchadores
environment_effect = StatModifierEffect(
    effect_id="barricadas",
    name="Barricadas improvisadas",
    description="Todos los LUCHADORES aliados ganan +1 DEF",
    defense_mod=1,
    filter_func=lambda card: card.zone == Zone.FIGHTER
)
```

### 3. Crear un Efecto Multi-Paso

```python
class RevealAndDiscardEffect(ImmediateEffect):
    def __init__(self, effect_id: str):
        super().__init__(
            effect_id=effect_id,
            name="Interrogatorio",
            description="Mira la mano del rival y descarta una carta",
            requires_choice=True,
            is_multi_step=True
        )
    
    def execute(self, context: EffectContext) -> EffectResult:
        # Paso 1: Mostrar opciones
        if "chosen_card" not in context.additional_data:
            opponent = self._get_opponent(context)
            choices = [{"game_id": card.game_id, "name": card.name} 
                      for card in opponent.hand]
            
            return EffectResult(
                success=True,
                message="Elige una carta para descartar",
                requires_choice=True,
                choices=choices,
                next_step="discard_chosen"
            )
        
        # Paso 2: Ejecutar acción elegida
        chosen_card_id = context.additional_data.get("chosen_card")
        # ... procesar la elección
```

## Integración con el Motor del Juego

### Registrar Efectos

```python
from engine.effects import effect_manager
from engine.card_effects import register_all_card_effects

# Registrar todos los efectos de cartas
register_all_card_effects()
```

### Ejecutar un Efecto Inmediato

```python
from engine.effects import EffectContext, effect_manager

# Crear contexto
context = EffectContext(
    game_state=game,
    source_player_id=player_id,
    source_card=card
)

# Ejecutar efecto
result = effect_manager.execute_immediate_effect(
    effect_id="draw_2",
    context=context
)

if result.success:
    print(result.message)
    
    # Si requiere elección del jugador
    if result.requires_choice:
        # Enviar opciones al cliente
        send_choices_to_client(result.choices)
```

### Activar Efectos Pasivos

```python
from engine.effects import EffectTrigger

# Al inicio del turno
results = effect_manager.trigger_effects(
    game_id=game.game_id,
    trigger=EffectTrigger.ON_TURN_START,
    context=context
)

for result in results:
    print(result.message)
```

### Calcular Stats con Modificadores

```python
# Obtener modificadores para una carta
attack_mod, defense_mod = effect_manager.get_stat_modifiers(
    game_id=game.game_id,
    card=card
)

# Aplicar modificadores
effective_attack = card.attack + attack_mod
effective_defense = card.defense + defense_mod
```

## Efectos Implementados

### Efectos de Cartas POLICE

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| 7 | Sirenas en la noche | Inmediato | Cancela la acción de un enemigo |
| 8 | Prisión preventiva | Inmediato | Devuelve una carta enemiga a la mano |
| 9 | Sobrecarga de trabajo | Inmediato | El rival descarta una carta al azar |
| 10 | Protección del Estado | Inmediato | Recupera 2 de Reputación |
| 11 | Luz de patrulla | Asíncrono | Impide que Ladrones usen habilidades este turno |
| 13 | Barricadas improvisadas | Pasivo | +1 DEF a LUCHADORES aliados |
| 14 | Pedir refuerzos | Inmediato | Roba 2 cartas |
| 15 | Control de multitudes | Asíncrono | El rival no puede atacar este turno |

### Efectos de Cartas MAFIA

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| 16 | Don Vito (Líder) | Pasivo | Gana 1 Reputación cuando un aliado es destruido |
| 22 | Soborno | Inmediato | Roba una carta y gana 1 Reputación |
| 23 | Amenaza velada | Inmediato | Destruye carta enemiga de valor ≤3 |
| 24 | Extorsión | Inmediato | El rival pierde 2 de Reputación |
| 25 | Red de influencias | Inmediato | Roba 3 cartas |
| 26 | Contrabando | Inmediato | Gana 3 de Reputación |
| 28 | Club nocturno | Pasivo | +1 DEF a PERSUASORES aliados |
| 29 | Lavado de dinero | Inmediato | Reduce el coste de cartas en mano en 1 este turno |
| 30 | Ataque sorpresa | Asíncrono | Ignora la defensa de un enemigo este turno |

### Efectos de Cartas DETECTIVE

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| 31 | Detective Marlowe (Líder) | Pasivo | Mira la mano del rival al inicio del turno |
| 36 | Tácticas de interrogatorio | Inmediato Multi-paso | Mira la mano del rival y descarta una carta |
| 37 | Orden de registro | Inmediato | Destruye carta enemiga de valor ≤4 |
| 38 | Informantes confiables | Inmediato | Roba 2 cartas |
| 39 | Evidencia incriminatoria | Asíncrono | El rival no puede atacar en su siguiente turno |
| 42 | Refugio seguro | Pasivo | +1 DEF a PERSUASORES aliados |
| 43 | Red de vigilancia | Inmediato | Mira la mano del rival |
| 44 | Testigo protegido | Inmediato | Recupera 2 de Reputación |
| 45 | Emboscada | Inmediato | Destruye carta enemiga de valor ≤5 |

### Efectos de Cartas THIEF

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| 51 | Robo relámpago | Inmediato | Roba una carta y gana 1 Reputación |
| 52 | Trampa para incautos | Inmediato | Destruye carta enemiga de valor ≤3 |
| 53 | Callejones oscuros | Pasivo | +1 ATK a LUCHADORES aliados |
| 54 | Escape audaz | Inmediato | Devuelve una carta descartada a tu mazo |
| 55 | Red de contrabando | Inmediato | Gana 3 de Reputación |
| 58 | Botín valioso | Inmediato | Roba 2 cartas |
| 59 | Pacto oscuro | Inmediato | El rival pierde 2 de Reputación |
| 60 | Golpe maestro | Inmediato | Destruye carta enemiga de valor ≤4 |

### Efectos de Cartas WILDCARD

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| 68 | Electrocutar | Inmediato | Pierde 1 de Reputación para destruir una carta enemiga |
| 69 | Cambio de identidad | Inmediato | Intercambia carta aleatoria de tu mano con una del rival |
| 70 | Caos controlado | Inmediato Multi-paso | Roba 2 cartas y descarta 1 |
| 71 | Mente maestra | Inmediato Multi-paso | Mira la mano del rival y roba una carta |
| 72 | Muestra gratuita | Inmediato | Juega una carta sin pagar su coste |
| 73 | Bomba atómica | Inmediato | Destruye todas las cartas en juego |
| 74 | Circo ambulante | Pasivo | +1 ATK y +1 DEF a todas las cartas aliadas |
| 75 | Misterio | Inmediato Multi-paso | Toma monedas del pozo perdiendo reputación |

## Añadir Nuevos Efectos

### 1. Crear la Clase del Efecto

```python
# En engine/card_effects.py o un nuevo módulo

class MyCustomEffect(ImmediateEffect):
    def __init__(self):
        super().__init__(
            effect_id="my_custom_effect",
            name="Mi Efecto",
            description="Descripción del efecto"
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        # Verificar si se puede ejecutar
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        # Implementar lógica del efecto
        return EffectResult(success=True, message="Efecto ejecutado")
```

### 2. Mapear la Carta al Efecto

```python
# En engine/card_effects.py

def get_card_effect(card_id: int) -> Optional[Effect]:
    effect_mapping = {
        # ... otros efectos
        999: lambda: MyCustomEffect(),  # ID de tu nueva carta
    }
    
    if card_id in effect_mapping:
        return effect_mapping[card_id]()
    
    return None
```

### 3. Registrar el Efecto

```python
# En engine/card_effects.py, función register_all_card_effects()

def register_all_card_effects():
    # Registrar efectos existentes
    for card_id in [7, 8, 9, ...]:
        effect = get_card_effect(card_id)
        if effect:
            effect_manager.register_effect(effect)
    
    # Registrar tu nuevo efecto
    effect = get_card_effect(999)
    if effect:
        effect_manager.register_effect(effect)
```

## Triggers de Eventos

Los siguientes triggers están disponibles para efectos pasivos y asíncronos:

- `ON_PLAY`: Al jugarse la carta
- `ON_DESTROY`: Al destruirse la carta
- `ON_ALLY_DESTROY`: Al destruirse una carta aliada
- `ON_ENEMY_DESTROY`: Al destruirse una carta enemiga
- `ON_TURN_START`: Al inicio del turno
- `ON_TURN_END`: Al final del turno
- `ON_ATTACK`: Al atacar
- `ON_RECEIVE_DAMAGE`: Al recibir daño
- `ON_DRAW`: Al robar carta
- `ALWAYS`: Siempre activo (para modificadores de stats)

## Consideraciones de Implementación

### Efectos Multi-Paso

Los efectos multi-paso requieren:
1. Establecer `is_multi_step=True` y `requires_choice=True`
2. En el primer paso, devolver `EffectResult` con `choices` y `next_step`
3. En pasos subsecuentes, usar `context.additional_data` para acceder a la elección del jugador

### Efectos que Revelan Información

Usar el campo `revealed_info` del `EffectResult` para enviar información al cliente:

```python
return EffectResult(
    success=True,
    message="Viendo la mano del rival",
    revealed_info={
        "opponent_hand": [
            {"game_id": card.game_id, "name": card.name}
            for card in opponent.hand
        ]
    }
)
```

### Gestión de Efectos Activos

- Los efectos pasivos se mantienen mientras la carta esté en juego
- Los efectos asíncronos se eliminan automáticamente al expirar o consumirse
- Usar `clear_game_effects(game_id)` al finalizar un juego

## Testing

```python
# Ejemplo de test para un efecto

def test_draw_cards_effect():
    # Setup
    game = create_test_game()
    player = game.players[0]
    
    # Añadir cartas al mazo
    player.deck = [create_test_card() for _ in range(5)]
    
    # Crear contexto
    context = EffectContext(
        game_state=game,
        source_player_id=player.id,
        source_card=None
    )
    
    # Ejecutar efecto
    effect = DrawCardsEffect("test_draw", 2)
    result = effect.execute(context)
    
    # Verificar
    assert result.success
    assert len(player.hand) == 2
    assert len(player.deck) == 3
```

## Próximos Pasos

1. Integrar el sistema de efectos con `engine/base.py`
2. Implementar el manejo de efectos multi-paso en el servidor WebSocket
3. Añadir soporte para la pila de descarte
4. Implementar efectos de líder faltantes (ej: "Redada" del Capitán O'Reilly)
5. Crear tests unitarios para todos los efectos

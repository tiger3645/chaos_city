"""
Ejemplo de integración del sistema de efectos con el motor del juego.

Este archivo muestra cómo modificar base.py para usar el sistema de efectos.
"""

from typing import Optional, Any
from models import GameState, Card, Zone
from engine.effects import (
    EffectContext,
    EffectTrigger,
    effect_manager
)
from engine.card_effects import (
    get_card_effect,
    get_environment_effect,
    get_leader_passive_effect
)


# ============================================================================
# INTEGRACIÓN CON GameEngine
# ============================================================================

def play_card_with_effects(
    game: GameState,
    player_id: str,
    card: Card,
    zone: Optional[Zone] = None
) -> dict:
    """
    Versión mejorada de play_card que maneja efectos.
    
    Retorna un diccionario con información sobre la ejecución:
    - success: bool
    - message: str
    - requires_choice: bool (opcional)
    - choices: list (opcional)
    - revealed_info: dict (opcional)
    - next_step: str (opcional)
    """
    
    # Buscar al jugador
    player = None
    for p in game.players:
        if p.id == player_id:
            player = p
            break
    
    if not player:
        return {"success": False, "message": "Jugador no encontrado"}
    
    # Verificar que el jugador tiene suficientes monedas
    if player.coins < card.value:
        return {"success": False, "message": "No tienes suficientes monedas"}
    
    # Deducir monedas
    player.coins -= card.value
    
    # Crear contexto para efectos
    context = EffectContext(
        game_state=game,
        source_player_id=player_id,
        source_card=card
    )
    
    # Manejar según el tipo de carta
    if card.type.value == "effect":
        # Carta de efecto: ejecutar y descartar
        effect = get_card_effect(card.id)
        
        if not effect:
            return {
                "success": False,
                "message": f"Efecto no implementado para {card.name}"
            }
        
        result = effect_manager.execute_immediate_effect(
            effect_id=effect.effect_id,
            context=context
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "requires_choice": result.requires_choice,
            "choices": result.choices,
            "revealed_info": result.revealed_info,
            "next_step": result.next_step,
            "data": result.data
        }
    
    elif card.type.value == "environment":
        # Carta de ambiente: reemplazar ambiente activo
        if game.active_environment_card:
            # Remover efecto del ambiente anterior
            # (en una implementación completa, habría que trackear esto)
            pass
        
        game.active_environment_card = card
        
        # Activar efecto pasivo del ambiente
        env_effect = get_environment_effect(card.id)
        if env_effect:
            effect_manager.add_passive_effect(game.game_id, env_effect)
        
        return {
            "success": True,
            "message": f"{card.name} está ahora activo"
        }
    
    elif card.type.value in ("character", "leader"):
        # Carta de personaje: colocar en el campo
        if not card.zone:
            return {
                "success": False,
                "message": "La carta no tiene zona definida"
            }
        
        player.field[card.zone].append(card)
        
        # Si es líder, activar su efecto pasivo
        if card.type.value == "leader":
            leader_effect = get_leader_passive_effect(card.id)
            if leader_effect:
                effect_manager.add_passive_effect(game.game_id, leader_effect)
        
        # Disparar trigger ON_PLAY
        trigger_results = effect_manager.trigger_effects(
            game_id=game.game_id,
            trigger=EffectTrigger.ON_PLAY,
            context=context
        )
        
        return {
            "success": True,
            "message": f"{card.name} fue colocado en {card.zone.value}",
            "triggered_effects": [r.message for r in trigger_results]
        }
    
    return {"success": False, "message": "Tipo de carta no reconocido"}


def attack_with_effects(
    game: GameState,
    player_id: str,
    attacker: Card,
    target: Optional[Card],
    target_zone: Zone
) -> dict:
    """
    Versión mejorada de attack que considera modificadores de stats.
    """
    
    # Buscar jugador y oponente
    player = None
    opponent = None
    for p in game.players:
        if p.id == player_id:
            player = p
        else:
            opponent = p
    
    if not player or not opponent:
        return {"success": False, "message": "Jugadores no encontrados"}
    
    # Obtener modificadores de stats para el atacante
    attack_mod, defense_mod = effect_manager.get_stat_modifiers(
        game_id=game.game_id,
        card=attacker
    )
    
    effective_attack = attacker.attack + attack_mod
    
    # Crear contexto para disparar efectos ON_ATTACK
    context = EffectContext(
        game_state=game,
        source_player_id=player_id,
        source_card=attacker,
        target_card=target
    )
    
    # Disparar efectos ON_ATTACK
    attack_effects = effect_manager.trigger_effects(
        game_id=game.game_id,
        trigger=EffectTrigger.ON_ATTACK,
        context=context
    )
    
    # Verificar si hay efectos que ignoren defensa
    ignore_defense = any(
        effect.data.get("ignore_defense", False)
        for effect in attack_effects
    )
    
    if target:
        # Ataque a carta específica
        target_def_mod, _ = effect_manager.get_stat_modifiers(
            game_id=game.game_id,
            card=target
        )
        
        effective_defense = target.defense + target_def_mod
        
        if ignore_defense:
            damage = effective_attack
            effective_defense = 0
        else:
            damage = effective_attack
        
        target.defense -= damage
        
        if target.defense <= 0:
            # Carta destruida
            opponent.field[target_zone].remove(target)
            
            # Disparar efectos ON_DESTROY y ON_ENEMY_DESTROY
            destroy_context = EffectContext(
                game_state=game,
                source_player_id=opponent.id,
                source_card=target
            )
            
            effect_manager.trigger_effects(
                game_id=game.game_id,
                trigger=EffectTrigger.ON_DESTROY,
                context=destroy_context
            )
            
            effect_manager.trigger_effects(
                game_id=game.game_id,
                trigger=EffectTrigger.ON_ENEMY_DESTROY,
                context=context
            )
            
            return {
                "success": True,
                "message": f"{attacker.name} destruyó a {target.name}",
                "destroyed": True,
                "target": target.name
            }
        else:
            return {
                "success": True,
                "message": f"{attacker.name} infligió {damage} de daño a {target.name}",
                "damage": damage,
                "remaining_defense": target.defense
            }
    else:
        # Ataque directo a la reputación
        
        # Verificar si hay efectos que prevengan el ataque
        damage_context = EffectContext(
            game_state=game,
            source_player_id=opponent.id,
            source_card=None,
            trigger=EffectTrigger.ON_RECEIVE_DAMAGE
        )
        
        prevent_effects = effect_manager.trigger_effects(
            game_id=game.game_id,
            trigger=EffectTrigger.ON_RECEIVE_DAMAGE,
            context=damage_context
        )
        
        if any(effect.data.get("damage_prevented") for effect in prevent_effects):
            return {
                "success": True,
                "message": "¡El ataque directo fue prevenido!",
                "prevented": True
            }
        
        opponent.reputation -= effective_attack
        
        if opponent.reputation <= 0:
            game.winner = player_id
            return {
                "success": True,
                "message": f"¡{player.name} ganó el juego!",
                "game_over": True,
                "winner": player.name
            }
        
        return {
            "success": True,
            "message": f"{attacker.name} infligió {effective_attack} de daño a la reputación",
            "reputation_damage": effective_attack,
            "opponent_reputation": opponent.reputation
        }


def start_turn_with_effects(game: GameState) -> list:
    """
    Inicia el turno del jugador actual y dispara efectos ON_TURN_START.
    """
    
    current_player = game.players[game.current_player]
    
    context = EffectContext(
        game_state=game,
        source_player_id=current_player.id,
        source_card=None,
        trigger=EffectTrigger.ON_TURN_START
    )
    
    results = effect_manager.trigger_effects(
        game_id=game.game_id,
        trigger=EffectTrigger.ON_TURN_START,
        context=context
    )
    
    messages = [result.message for result in results if result.success]
    
    return messages


def end_turn_with_effects(game: GameState) -> list:
    """
    Finaliza el turno del jugador actual y dispara efectos ON_TURN_END.
    """
    
    current_player = game.players[game.current_player]
    
    context = EffectContext(
        game_state=game,
        source_player_id=current_player.id,
        source_card=None,
        trigger=EffectTrigger.ON_TURN_END
    )
    
    results = effect_manager.trigger_effects(
        game_id=game.game_id,
        trigger=EffectTrigger.ON_TURN_END,
        context=context
    )
    
    # Eliminar efectos que hayan expirado
    expired_messages = [
        result.message
        for result in results
        if result.data.get("expired") or result.data.get("consumed")
    ]
    
    return expired_messages


def continue_multi_step_effect(
    game: GameState,
    player_id: str,
    effect_id: str,
    chosen_value: Any
) -> dict:
    """
    Continúa un efecto multi-paso con la elección del jugador.
    """
    
    # Buscar el efecto original
    effect = effect_manager.registered_effects.get(effect_id)
    
    if not effect:
        return {"success": False, "message": "Efecto no encontrado"}
    
    # Crear contexto con la elección del jugador
    context = EffectContext(
        game_state=game,
        source_player_id=player_id,
        source_card=None,
        additional_data={
            "chosen_card": chosen_value,  # o el key apropiado según el efecto
            "discarded_card": chosen_value,
            "stolen_card": chosen_value,
            "coins_taken": chosen_value,
            # etc.
        }
    )
    
    result = effect.execute(context)
    
    return {
        "success": result.success,
        "message": result.message,
        "requires_choice": result.requires_choice,
        "choices": result.choices,
        "next_step": result.next_step,
        "data": result.data
    }


# ============================================================================
# EJEMPLO DE USO COMPLETO
# ============================================================================

def example_complete_turn():
    """
    Ejemplo completo de cómo se vería un turno usando el sistema de efectos.
    """
    
    # Supongamos que ya tenemos un juego creado
    from models import GameState, Player, Card, Faction, CardType, Zone, CARDS_DB
    import uuid
    
    # Crear juego de prueba
    game = GameState(
        game_id=str(uuid.uuid4()),
        players=[
            Player(
                id=str(uuid.uuid4()),
                name="Jugador 1",
                coins=5
            ),
            Player(
                id=str(uuid.uuid4()),
                name="Jugador 2",
                coins=5
            )
        ]
    )
    
    player1 = game.players[0]
    player2 = game.players[1]
    
    # 1. INICIO DEL TURNO
    print("=== INICIO DEL TURNO ===")
    start_messages = start_turn_with_effects(game)
    for msg in start_messages:
        print(f"  - {msg}")
    
    # 2. FASE DE ROBO
    print("\n=== FASE DE ROBO ===")
    if player1.deck:
        card = player1.deck.pop()
        player1.hand.append(card)
        print(f"  {player1.name} robó {card.name}")
    
    # 3. FASE DE DESPLIEGUE - Jugar una carta de ambiente
    print("\n=== FASE DE DESPLIEGUE ===")
    
    # Simular que el jugador tiene "Barricadas improvisadas" (ID 13)
    environment_card = CARDS_DB[13]
    environment_card.game_id = str(uuid.uuid4())
    player1.hand.append(environment_card)
    
    result = play_card_with_effects(
        game=game,
        player_id=player1.id,
        card=environment_card
    )
    print(f"  {result['message']}")
    
    # 4. JUGAR UNA CARTA DE EFECTO - "Pedir refuerzos" (ID 14)
    effect_card = CARDS_DB[14]
    effect_card.game_id = str(uuid.uuid4())
    player1.hand.append(effect_card)
    player1.coins = 10  # Dar monedas suficientes
    
    result = play_card_with_effects(
        game=game,
        player_id=player1.id,
        card=effect_card
    )
    print(f"  {result['message']}")
    
    if result.get("requires_choice"):
        print(f"  Esperando elección del jugador:")
        for choice in result.get("choices", []):
            print(f"    - {choice}")
    
    # 5. JUGAR UNA CARTA DE PERSONAJE
    character_card = CARDS_DB[2]  # Agentes de patrulla
    character_card.game_id = str(uuid.uuid4())
    player1.hand.append(character_card)
    
    result = play_card_with_effects(
        game=game,
        player_id=player1.id,
        card=character_card
    )
    print(f"  {result['message']}")
    
    # 6. FASE DE ACCIÓN - Atacar
    print("\n=== FASE DE ACCIÓN ===")
    
    # Colocar una carta enemiga para atacar
    enemy_card = CARDS_DB[17]  # Matones a sueldo
    enemy_card.game_id = str(uuid.uuid4())
    player2.field[Zone.FIGHTER].append(enemy_card)
    
    # Atacar con los Agentes de patrulla
    result = attack_with_effects(
        game=game,
        player_id=player1.id,
        attacker=character_card,
        target=enemy_card,
        target_zone=Zone.FIGHTER
    )
    print(f"  {result['message']}")
    
    # 7. FIN DEL TURNO
    print("\n=== FIN DEL TURNO ===")
    end_messages = end_turn_with_effects(game)
    for msg in end_messages:
        print(f"  - {msg}")
    
    # 8. MOSTRAR ESTADO
    print("\n=== ESTADO FINAL ===")
    print(f"  {player1.name}:")
    print(f"    - Reputación: {player1.reputation}")
    print(f"    - Monedas: {player1.coins}")
    print(f"    - Cartas en mano: {len(player1.hand)}")
    print(f"    - Cartas en campo: {sum(len(cards) for cards in player1.field.values())}")
    
    print(f"\n  {player2.name}:")
    print(f"    - Reputación: {player2.reputation}")
    print(f"    - Monedas: {player2.coins}")
    print(f"    - Cartas en mano: {len(player2.hand)}")
    print(f"    - Cartas en campo: {sum(len(cards) for cards in player2.field.values())}")
    
    if game.active_environment_card:
        print(f"\n  Ambiente activo: {game.active_environment_card.name}")
    
    # Mostrar modificadores activos
    print("\n  Modificadores activos:")
    for player in game.players:
        for zone, cards in player.field.items():
            for card in cards:
                atk_mod, def_mod = effect_manager.get_stat_modifiers(game.game_id, card)
                if atk_mod != 0 or def_mod != 0:
                    print(f"    - {card.name}: {card.attack + atk_mod}/{card.defense + def_mod} "
                          f"(base: {card.attack}/{card.defense})")


if __name__ == "__main__":
    print("Ejecutando ejemplo de turno completo...\n")
    example_complete_turn()

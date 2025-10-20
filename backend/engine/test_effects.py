"""
Tests unitarios de ejemplo para el sistema de efectos.

Este archivo muestra cómo testear los efectos implementados.
"""

import uuid
import pytest
from models import GameState, Player, Card, Faction, CardType, Zone, CARDS_DB
from engine.effects import (
    EffectContext,
    EffectTrigger,
    effect_manager,
    DrawCardsEffect,
    DealDamageEffect,
    HealReputationEffect,
    DestroyCardEffect,
    StatModifierEffect
)
from engine.card_effects import (
    get_card_effect,
    get_environment_effect,
    get_leader_passive_effect
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def game_state():
    """Crea un estado de juego básico para tests"""
    player1 = Player(
        id=str(uuid.uuid4()),
        name="Jugador 1",
        reputation=20,
        coins=10
    )
    
    player2 = Player(
        id=str(uuid.uuid4()),
        name="Jugador 2",
        reputation=20,
        coins=10
    )
    
    # Añadir algunas cartas al mazo de ambos jugadores
    for _ in range(10):
        card1 = CARDS_DB[2].copy()  # Agentes de patrulla
        card1.game_id = str(uuid.uuid4())
        player1.deck.append(card1)
        
        card2 = CARDS_DB[17].copy()  # Matones a sueldo
        card2.game_id = str(uuid.uuid4())
        player2.deck.append(card2)
    
    game = GameState(
        game_id=str(uuid.uuid4()),
        players=[player1, player2]
    )
    
    return game


@pytest.fixture
def effect_context(game_state):
    """Crea un contexto de efecto básico"""
    return EffectContext(
        game_state=game_state,
        source_player_id=game_state.players[0].id,
        source_card=None
    )


# ============================================================================
# TESTS DE EFECTOS INMEDIATOS
# ============================================================================

def test_draw_cards_effect(game_state, effect_context):
    """Test del efecto de robar cartas"""
    player = game_state.players[0]
    initial_hand_size = len(player.hand)
    initial_deck_size = len(player.deck)
    
    # Crear y ejecutar efecto
    effect = DrawCardsEffect("test_draw", 2)
    result = effect.execute(effect_context)
    
    # Verificaciones
    assert result.success
    assert len(player.hand) == initial_hand_size + 2
    assert len(player.deck) == initial_deck_size - 2
    assert result.data["cards_drawn"] == 2


def test_draw_cards_effect_empty_deck(game_state, effect_context):
    """Test del efecto de robar cartas con mazo vacío"""
    player = game_state.players[0]
    player.deck.clear()
    
    effect = DrawCardsEffect("test_draw", 2)
    result = effect.execute(effect_context)
    
    # Debería fallar o no robar cartas
    assert len(player.hand) == 0


def test_deal_damage_effect(game_state, effect_context):
    """Test del efecto de infligir daño"""
    opponent = game_state.players[1]
    initial_reputation = opponent.reputation
    
    effect = DealDamageEffect("test_damage", 3, to_opponent=True)
    result = effect.execute(effect_context)
    
    assert result.success
    assert opponent.reputation == initial_reputation - 3


def test_deal_damage_effect_game_over(game_state, effect_context):
    """Test del efecto de daño que termina el juego"""
    opponent = game_state.players[1]
    opponent.reputation = 2  # Poca reputación
    
    effect = DealDamageEffect("test_damage", 3, to_opponent=True)
    result = effect.execute(effect_context)
    
    assert result.success
    assert opponent.reputation <= 0
    assert result.data.get("game_over") == True
    assert game_state.winner == game_state.players[0].id


def test_heal_reputation_effect(game_state, effect_context):
    """Test del efecto de curación"""
    player = game_state.players[0]
    player.reputation = 10
    
    effect = HealReputationEffect("test_heal", 5)
    result = effect.execute(effect_context)
    
    assert result.success
    assert player.reputation == 15


def test_destroy_card_effect(game_state, effect_context):
    """Test del efecto de destruir carta"""
    opponent = game_state.players[1]
    
    # Colocar una carta en el campo enemigo
    card = CARDS_DB[17]  # Matones a sueldo (valor 2)
    card.game_id = str(uuid.uuid4())
    opponent.field[Zone.FIGHTER].append(card)
    
    # Actualizar contexto con la carta objetivo
    effect_context.target_card = card
    
    # Ejecutar efecto que destruye cartas de valor 3 o menos
    effect = DestroyCardEffect("test_destroy", max_value=3)
    result = effect.execute(effect_context)
    
    assert result.success
    assert card not in opponent.field[Zone.FIGHTER]


def test_destroy_card_effect_value_too_high(game_state, effect_context):
    """Test del efecto de destruir carta con valor demasiado alto"""
    opponent = game_state.players[1]
    
    # Colocar una carta de valor alto
    card = CARDS_DB[16]  # Don Vito (valor 9)
    card.game_id = str(uuid.uuid4())
    opponent.field[Zone.TALKER].append(card)
    
    effect_context.target_card = card
    
    # Efecto que solo destruye cartas de valor 3 o menos
    effect = DestroyCardEffect("test_destroy", max_value=3)
    
    # can_execute debería retornar False
    assert not effect.can_execute(effect_context)


# ============================================================================
# TESTS DE EFECTOS PASIVOS
# ============================================================================

def test_stat_modifier_effect(game_state):
    """Test de modificadores de estadísticas"""
    player = game_state.players[0]
    
    # Colocar cartas en el campo
    fighter1 = CARDS_DB[2]  # Agentes de patrulla (luchador)
    fighter1.game_id = str(uuid.uuid4())
    player.field[Zone.FIGHTER].append(fighter1)
    
    talker1 = CARDS_DB[4]  # Detective de turno (persuasor)
    talker1.game_id = str(uuid.uuid4())
    player.field[Zone.TALKER].append(talker1)
    
    # Crear efecto que da +1 DEF a luchadores
    effect = StatModifierEffect(
        effect_id="test_modifier",
        name="Test Modifier",
        description="+1 DEF a luchadores",
        defense_mod=1,
        filter_func=lambda card: card.zone == Zone.FIGHTER
    )
    
    # Añadir efecto al juego
    effect_manager.add_passive_effect(game_state.game_id, effect)
    
    # Verificar modificadores
    fighter_atk_mod, fighter_def_mod = effect_manager.get_stat_modifiers(
        game_state.game_id, fighter1
    )
    assert fighter_def_mod == 1
    assert fighter_atk_mod == 0
    
    talker_atk_mod, talker_def_mod = effect_manager.get_stat_modifiers(
        game_state.game_id, talker1
    )
    assert talker_def_mod == 0  # No aplica a persuasores


def test_environment_card_effect(game_state):
    """Test de efectos de cartas de ambiente"""
    player = game_state.players[0]
    
    # Colocar luchadores en el campo
    fighter = CARDS_DB[2]
    fighter.game_id = str(uuid.uuid4())
    player.field[Zone.FIGHTER].append(fighter)
    
    # Activar "Barricadas improvisadas" (ID 13) - +1 DEF a luchadores
    env_effect = get_environment_effect(13)
    assert env_effect is not None
    
    effect_manager.add_passive_effect(game_state.game_id, env_effect)
    
    # Verificar que el modificador se aplica
    atk_mod, def_mod = effect_manager.get_stat_modifiers(
        game_state.game_id, fighter
    )
    assert def_mod == 1


def test_multiple_environment_effects(game_state):
    """Test de múltiples efectos de ambiente acumulados"""
    player = game_state.players[0]
    
    fighter = CARDS_DB[2]
    fighter.game_id = str(uuid.uuid4())
    player.field[Zone.FIGHTER].append(fighter)
    
    # Activar "Circo ambulante" (ID 74) - +1 ATK y +1 DEF a todos
    env1 = get_environment_effect(74)
    effect_manager.add_passive_effect(game_state.game_id, env1)
    
    # Activar "Barricadas improvisadas" (ID 13) - +1 DEF a luchadores
    env2 = get_environment_effect(13)
    effect_manager.add_passive_effect(game_state.game_id, env2)
    
    # Deberían acumularse: +1 ATK, +2 DEF
    atk_mod, def_mod = effect_manager.get_stat_modifiers(
        game_state.game_id, fighter
    )
    assert atk_mod == 1
    assert def_mod == 2


# ============================================================================
# TESTS DE EFECTOS DE CARTAS ESPECÍFICAS
# ============================================================================

def test_card_effect_pedir_refuerzos(game_state, effect_context):
    """Test de 'Pedir refuerzos' (ID 14) - Roba 2 cartas"""
    player = game_state.players[0]
    initial_hand_size = len(player.hand)
    
    effect = get_card_effect(14)
    assert effect is not None
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert len(player.hand) == initial_hand_size + 2


def test_card_effect_extorsion(game_state, effect_context):
    """Test de 'Extorsión' (ID 24) - El rival pierde 2 de reputación"""
    opponent = game_state.players[1]
    initial_reputation = opponent.reputation
    
    effect = get_card_effect(24)
    assert effect is not None
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert opponent.reputation == initial_reputation - 2


def test_card_effect_amenaza_velada(game_state, effect_context):
    """Test de 'Amenaza velada' (ID 23) - Destruye carta de valor ≤3"""
    opponent = game_state.players[1]
    
    # Colocar carta de valor 2
    card = CARDS_DB[17]  # Matones a sueldo
    card.game_id = str(uuid.uuid4())
    opponent.field[Zone.FIGHTER].append(card)
    
    effect_context.target_card = card
    
    effect = get_card_effect(23)
    assert effect is not None
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert card not in opponent.field[Zone.FIGHTER]


def test_card_effect_red_vigilancia(game_state, effect_context):
    """Test de 'Red de vigilancia' (ID 43) - Mira la mano del rival"""
    opponent = game_state.players[1]
    
    # Dar cartas al oponente
    for _ in range(3):
        card = opponent.deck.pop()
        opponent.hand.append(card)
    
    effect = get_card_effect(43)
    assert effect is not None
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert result.revealed_info is not None
    assert "opponent_hand" in result.revealed_info
    assert len(result.revealed_info["opponent_hand"]) == 3


def test_card_effect_sobrecarga_trabajo(game_state, effect_context):
    """Test de 'Sobrecarga de trabajo' (ID 9) - El rival descarta al azar"""
    opponent = game_state.players[1]
    
    # Dar cartas al oponente
    for _ in range(5):
        card = opponent.deck.pop()
        opponent.hand.append(card)
    
    initial_hand_size = len(opponent.hand)
    
    effect = get_card_effect(9)
    assert effect is not None
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert len(opponent.hand) == initial_hand_size - 1


# ============================================================================
# TESTS DE EFECTOS MULTI-PASO
# ============================================================================

def test_multi_step_effect_tacticas_interrogatorio(game_state, effect_context):
    """Test de 'Tácticas de interrogatorio' (ID 36) - Multi-paso"""
    opponent = game_state.players[1]
    
    # Dar cartas al oponente
    for _ in range(3):
        card = opponent.deck.pop()
        opponent.hand.append(card)
    
    effect = get_card_effect(36)
    assert effect is not None
    
    # Paso 1: Debería mostrar opciones
    result = effect.execute(effect_context)
    
    assert result.success
    assert result.requires_choice
    assert len(result.choices) == 3
    assert result.next_step == "discard_chosen"
    
    # Paso 2: Elegir una carta para descartar
    chosen_card = opponent.hand[0]
    effect_context.additional_data = {"chosen_card": chosen_card.game_id}
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert chosen_card not in opponent.hand


def test_multi_step_effect_caos_controlado(game_state, effect_context):
    """Test de 'Caos controlado' (ID 70) - Roba 2 y descarta 1"""
    player = game_state.players[0]
    initial_hand_size = len(player.hand)
    
    effect = get_card_effect(70)
    assert effect is not None
    
    # Paso 1: Robar cartas
    result = effect.execute(effect_context)
    
    assert result.success
    assert result.requires_choice
    assert len(player.hand) == initial_hand_size + 2
    
    # Paso 2: Descartar una carta
    card_to_discard = player.hand[0]
    effect_context.additional_data = {"discarded_card": card_to_discard.game_id}
    
    result = effect.execute(effect_context)
    
    assert result.success
    assert len(player.hand) == initial_hand_size + 1


# ============================================================================
# TESTS DE EFECTOS DE LÍDERES
# ============================================================================

def test_leader_don_vito_passive(game_state):
    """Test de habilidad pasiva de Don Vito (ID 16)"""
    player = game_state.players[0]
    
    # Colocar a Don Vito en el campo
    don_vito = CARDS_DB[16]
    don_vito.game_id = str(uuid.uuid4())
    player.field[Zone.TALKER].append(don_vito)
    
    # Activar su efecto pasivo
    leader_effect = get_leader_passive_effect(16)
    assert leader_effect is not None
    
    effect_manager.add_passive_effect(game_state.game_id, leader_effect)
    
    # Colocar un aliado
    ally = CARDS_DB[17]
    ally.game_id = str(uuid.uuid4())
    player.field[Zone.FIGHTER].append(ally)
    
    initial_reputation = player.reputation
    
    # Simular destrucción del aliado
    context = EffectContext(
        game_state=game_state,
        source_player_id=player.id,
        source_card=ally,
        trigger=EffectTrigger.ON_ALLY_DESTROY
    )
    
    results = effect_manager.trigger_effects(
        game_id=game_state.game_id,
        trigger=EffectTrigger.ON_ALLY_DESTROY,
        context=context
    )
    
    # Don Vito debería haber ganado reputación
    # Nota: Este test es simplificado, en la implementación real
    # el callback debería modificar la reputación


# ============================================================================
# TESTS DE INTEGRACIÓN
# ============================================================================

def test_effect_manager_lifecycle(game_state):
    """Test del ciclo de vida completo de efectos"""
    
    # 1. Registrar un efecto inmediato
    effect = DrawCardsEffect("lifecycle_test", 2)
    effect_manager.register_effect(effect)
    
    # 2. Añadir un efecto pasivo
    passive = StatModifierEffect(
        effect_id="passive_test",
        name="Test Passive",
        description="Test",
        attack_mod=1
    )
    effect_manager.add_passive_effect(game_state.game_id, passive)
    
    # 3. Verificar que los efectos están activos
    assert game_state.game_id in effect_manager.active_passive_effects
    assert len(effect_manager.active_passive_effects[game_state.game_id]) > 0
    
    # 4. Limpiar efectos del juego
    effect_manager.clear_game_effects(game_state.game_id)
    
    # 5. Verificar que se limpiaron
    assert game_state.game_id not in effect_manager.active_passive_effects
    assert game_state.game_id not in effect_manager.active_async_effects


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v"])

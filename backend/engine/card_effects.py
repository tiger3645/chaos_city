"""
Implementaciones específicas de efectos de cartas del juego Chaos City.

Este módulo contiene todos los efectos concretos definidos en las cartas del juego,
mapeados por el ID de la carta.
"""

from typing import Dict, Callable, Optional
from models import Card, Zone, Faction, CardType
from engine.effects import (
    Effect,
    ImmediateEffect,
    PassiveEffect,
    AsyncEffect,
    EffectContext,
    EffectResult,
    EffectTrigger,
    DrawCardsEffect,
    DealDamageEffect,
    HealReputationEffect,
    DestroyCardEffect,
    ReturnToHandEffect,
    DiscardRandomEffect,
    RevealOpponentHandEffect,
    RevealAndDiscardEffect,
    StatModifierEffect,
    OnAllyDestroyEffect,
    OnTurnStartEffect,
    DelayedStatModifierEffect,
    PreventNextAttackEffect,
    effect_manager
)


# ============================================================================
# EFECTOS ESPECÍFICOS DE CARTAS
# ============================================================================

class ReduceHandCostEffect(ImmediateEffect):
    """Efecto que reduce el costo de cartas en la mano (Lavado de dinero - ID 29)"""
    
    def __init__(self):
        super().__init__(
            effect_id="reduce_hand_cost",
            name="Reducir costo de mano",
            description="Reduce el coste de todas las cartas en tu mano en 1 este turno"
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
        # Crear efecto temporal que reduce costos
        # Nota: Esto requeriría un sistema de modificadores temporales
        # Por ahora, retornamos información para que el servidor lo maneje
        
        return EffectResult(
            success=True,
            message="Todas las cartas en tu mano cuestan 1 menos este turno",
            data={
                "effect_type": "cost_reduction",
                "amount": 1,
                "duration": "this_turn",
                "affected_cards": [card.game_id for card in player.hand]
            }
        )
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None


class PreventAttackEffect(AsyncEffect):
    """Efecto que previene ataques (Control de multitudes - ID 15, Evidencia incriminatoria - ID 39)"""
    
    def __init__(self, effect_id: str = "prevent_attack"):
        super().__init__(
            effect_id=effect_id,
            name="Prevenir ataque",
            description="El rival no puede atacar en su siguiente turno",
            trigger=EffectTrigger.ON_TURN_START,
            expires_after_turns=1
        )
        self.activated = False
    
    def can_execute(self, context: EffectContext) -> bool:
        # El efecto se activa en el turno del oponente
        opponent_id = None
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                opponent_id = player.id
                break
        
        current_player = context.game_state.players[context.game_state.current_player]
        return current_player.id == opponent_id
    
    def execute(self, context: EffectContext) -> EffectResult:
        if not self.activated:
            self.activated = True
            return EffectResult(
                success=True,
                message="El oponente no puede atacar este turno",
                data={"prevent_attacks": True}
            )
        
        return EffectResult(
            success=True,
            message="Efecto de prevención de ataque expirado",
            data={"expired": True}
        )


class IgnoreDefenseEffect(AsyncEffect):
    """Efecto que ignora la defensa (Ataque sorpresa - ID 30)"""
    
    def __init__(self):
        super().__init__(
            effect_id="ignore_defense",
            name="Ignorar defensa",
            description="Ignora la defensa de un enemigo este turno",
            trigger=EffectTrigger.ON_ATTACK,
            expires_after_turns=1
        )
        self.consumed = False
    
    def can_execute(self, context: EffectContext) -> bool:
        return not self.consumed
    
    def execute(self, context: EffectContext) -> EffectResult:
        if context.trigger == EffectTrigger.ON_ATTACK:
            self.consumed = True
            return EffectResult(
                success=True,
                message="¡La defensa del enemigo es ignorada!",
                data={"ignore_defense": True, "consumed": True}
            )
        
        return EffectResult(
            success=True,
            message="Efecto listo para activarse en ataque"
        )


class CancelEnemyActionEffect(ImmediateEffect):
    """Efecto que cancela una acción enemiga (Sirenas en la noche - ID 7)"""
    
    def __init__(self):
        super().__init__(
            effect_id="cancel_enemy_action",
            name="Cancelar acción",
            description="Cancela la acción de un enemigo este turno",
            requires_target=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return context.target_card is not None
    
    def execute(self, context: EffectContext) -> EffectResult:
        if not context.target_card:
            return EffectResult(False, "No se especificó objetivo")
        
        # Este efecto requiere interacción con el sistema de acciones
        # Por ahora retornamos información para que el servidor lo maneje
        
        return EffectResult(
            success=True,
            message=f"La acción de {context.target_card.name} ha sido cancelada",
            data={
                "cancelled_card": context.target_card.game_id,
                "effect_type": "cancel_action"
            }
        )


class DisableThiefAbilitiesEffect(AsyncEffect):
    """Efecto que deshabilita habilidades de ladrones (Luz de patrulla - ID 11)"""
    
    def __init__(self):
        super().__init__(
            effect_id="disable_thief_abilities",
            name="Deshabilitar ladrones",
            description="Impide que cualquier Ladrón use habilidades este turno",
            trigger=EffectTrigger.ON_TURN_END,
            expires_after_turns=1
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        return EffectResult(
            success=True,
            message="Los ladrones no pueden usar habilidades este turno",
            data={
                "disabled_faction": Faction.THIEF.value,
                "expires_next_turn": True
            }
        )


class ReturnDiscardedToDeckEffect(ImmediateEffect):
    """Efecto que devuelve una carta descartada al mazo (Escape audaz - ID 54)"""
    
    def __init__(self):
        super().__init__(
            effect_id="return_discarded_to_deck",
            name="Devolver descartada al mazo",
            description="Devuelve una carta descartada a tu mazo",
            requires_choice=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        # Requeriría un sistema de pila de descarte
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        # Por ahora, placeholder para cuando se implemente el descarte
        return EffectResult(
            success=True,
            message="Carta devuelta al mazo",
            data={"effect_type": "return_to_deck"}
        )


class SwapRandomHandCardEffect(ImmediateEffect):
    """Efecto que intercambia cartas aleatorias (Cambio de identidad - ID 69)"""
    
    def __init__(self):
        super().__init__(
            effect_id="swap_random_hand_card",
            name="Intercambiar carta de mano",
            description="Intercambia una carta aleatoria de tu mano con una del rival"
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        player = self._get_player(context)
        opponent = self._get_opponent(context)
        return bool(player and opponent and player.hand and opponent.hand)
    
    def execute(self, context: EffectContext) -> EffectResult:
        import random
        
        player = self._get_player(context)
        opponent = self._get_opponent(context)
        
        if not player or not opponent:
            return EffectResult(False, "Jugadores no encontrados")
        
        if not player.hand or not opponent.hand:
            return EffectResult(False, "No hay cartas para intercambiar")
        
        player_card = random.choice(player.hand)
        opponent_card = random.choice(opponent.hand)
        
        player.hand.remove(player_card)
        opponent.hand.remove(opponent_card)
        
        player.hand.append(opponent_card)
        opponent.hand.append(player_card)
        
        return EffectResult(
            success=True,
            message=f"Intercambiaste {player_card.name} por {opponent_card.name}",
            data={
                "player_gave": player_card.game_id,
                "player_received": opponent_card.game_id
            }
        )
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None
    
    def _get_opponent(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


class DrawAndDiscardEffect(ImmediateEffect):
    """Efecto que roba cartas y descarta (Caos controlado - ID 70)"""
    
    def __init__(self):
        super().__init__(
            effect_id="draw_and_discard",
            name="Robar y descartar",
            description="Roba 2 cartas y descarta 1 carta",
            requires_choice=True,
            is_multi_step=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
        # Paso 1: Robar cartas
        if "discarded_card" not in context.additional_data:
            drawn = 0
            for _ in range(2):
                if player.deck:
                    card = player.deck.pop()
                    player.hand.append(card)
                    drawn += 1
            
            if drawn == 0:
                return EffectResult(False, "No hay cartas para robar")
            
            # Solicitar elección de carta para descartar
            choices = [
                {
                    "game_id": card.game_id,
                    "name": card.name,
                    "value": card.value,
                    "type": card.type.value
                }
                for card in player.hand
            ]
            
            return EffectResult(
                success=True,
                message=f"Robaste {drawn} cartas. Elige una para descartar",
                requires_choice=True,
                choices=choices,
                next_step="discard_chosen"
            )
        
        # Paso 2: Descartar carta elegida
        chosen_game_id = context.additional_data.get("discarded_card")
        card_to_discard = None
        for card in player.hand:
            if card.game_id == chosen_game_id:
                card_to_discard = card
                break
        
        if card_to_discard:
            player.hand.remove(card_to_discard)
            return EffectResult(
                success=True,
                message=f"Descartaste {card_to_discard.name}",
                data={"discarded_card": card_to_discard.game_id}
            )
        
        return EffectResult(False, "Carta no encontrada")
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None


class RevealAndStealCardEffect(ImmediateEffect):
    """Efecto que ve la mano y roba una carta (Mente maestra - ID 71)"""
    
    def __init__(self):
        super().__init__(
            effect_id="reveal_and_steal",
            name="Robar carta elegida",
            description="Mira la mano del rival y roba una carta de tu elección",
            requires_choice=True,
            is_multi_step=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        opponent = self._get_opponent(context)
        if not opponent:
            return EffectResult(False, "Oponente no encontrado")
        
        # Paso 1: Revelar mano
        if "stolen_card" not in context.additional_data:
            if not opponent.hand:
                return EffectResult(False, "El oponente no tiene cartas")
            
            choices = [
                {
                    "game_id": card.game_id,
                    "name": card.name,
                    "value": card.value,
                    "type": card.type.value
                }
                for card in opponent.hand
            ]
            
            return EffectResult(
                success=True,
                message="Elige una carta para robar",
                requires_choice=True,
                choices=choices,
                next_step="steal_chosen"
            )
        
        # Paso 2: Robar carta elegida
        player = self._get_player(context)
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
        chosen_game_id = context.additional_data.get("stolen_card")
        card_to_steal = None
        for card in opponent.hand:
            if card.game_id == chosen_game_id:
                card_to_steal = card
                break
        
        if card_to_steal:
            opponent.hand.remove(card_to_steal)
            player.hand.append(card_to_steal)
            return EffectResult(
                success=True,
                message=f"Robaste {card_to_steal.name}",
                data={"stolen_card": card_to_steal.game_id}
            )
        
        return EffectResult(False, "Carta no encontrada")
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None
    
    def _get_opponent(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


class PlayCardFreeEffect(ImmediateEffect):
    """Efecto que permite jugar una carta gratis (Muestra gratuita - ID 72)"""
    
    def __init__(self):
        super().__init__(
            effect_id="play_card_free",
            name="Jugar carta gratis",
            description="Juega una carta de tu mano sin pagar su coste",
            requires_choice=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        if not player or not player.hand:
            return EffectResult(False, "No hay cartas en la mano")
        
        choices = [
            {
                "game_id": card.game_id,
                "name": card.name,
                "value": card.value,
                "type": card.type.value
            }
            for card in player.hand
        ]
        
        return EffectResult(
            success=True,
            message="Elige una carta para jugar gratis",
            requires_choice=True,
            choices=choices,
            data={"effect_type": "play_free"}
        )
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None


class DestroyAllCardsEffect(ImmediateEffect):
    """Efecto que destruye todas las cartas en juego (Bomba atómica - ID 73)"""
    
    def __init__(self):
        super().__init__(
            effect_id="destroy_all_cards",
            name="Destruir todas las cartas",
            description="Destruye todas las cartas en juego"
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        destroyed_count = 0
        
        for player in context.game_state.players:
            for zone, cards in player.field.items():
                destroyed_count += len(cards)
                cards.clear()
        
        # También destruir ambiente activo
        if context.game_state.active_environment_card:
            context.game_state.active_environment_card = None
            destroyed_count += 1
        
        return EffectResult(
            success=True,
            message=f"¡Bomba atómica! Se destruyeron {destroyed_count} cartas",
            data={"destroyed_count": destroyed_count}
        )


class TakeCoinsLoseReputationEffect(ImmediateEffect):
    """Efecto que permite tomar monedas perdiendo reputación (Misterio - ID 75)"""
    
    def __init__(self):
        super().__init__(
            effect_id="take_coins_lose_reputation",
            name="Tomar monedas",
            description="Toma monedas del pozo común y pierde 1 de reputación por cada moneda",
            requires_choice=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return context.game_state.available_coins > 0
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
        # Si no se ha elegido cantidad, mostrar opciones
        if "coins_taken" not in context.additional_data:
            max_coins = min(context.game_state.available_coins, player.reputation)
            choices = [
                {"amount": i, "reputation_cost": i}
                for i in range(1, max_coins + 1)
            ]
            
            return EffectResult(
                success=True,
                message=f"¿Cuántas monedas quieres tomar? (Máximo {max_coins})",
                requires_choice=True,
                choices=choices,
                next_step="take_coins"
            )
        
        # Tomar monedas y perder reputación
        coins_taken = context.additional_data.get("coins_taken", 0)
        
        if coins_taken > context.game_state.available_coins:
            return EffectResult(False, "No hay suficientes monedas disponibles")
        
        if coins_taken > player.reputation:
            return EffectResult(False, "No tienes suficiente reputación")
        
        player.coins += coins_taken
        context.game_state.available_coins -= coins_taken
        player.reputation -= coins_taken
        
        return EffectResult(
            success=True,
            message=f"Tomaste {coins_taken} monedas y perdiste {coins_taken} de reputación",
            data={"coins_taken": coins_taken, "reputation_lost": coins_taken}
        )
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None


class SelfDamageDestroyEffect(ImmediateEffect):
    """Efecto que destruye una carta a costa de reputación (Electrocutar - ID 68)"""
    
    def __init__(self):
        super().__init__(
            effect_id="self_damage_destroy",
            name="Electrocutar",
            description="Pierde 1 de Reputación para destruir una carta enemiga",
            requires_target=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        player = self._get_player(context)
        return bool(player and player.reputation > 1 and context.target_card is not None)
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
        if player.reputation <= 1:
            return EffectResult(False, "No tienes suficiente reputación")
        
        if not context.target_card:
            return EffectResult(False, "No se especificó objetivo")
        
        opponent = self._get_opponent(context)
        if not opponent:
            return EffectResult(False, "Oponente no encontrado")
        
        # Buscar y destruir la carta
        destroyed = False
        for zone, cards in opponent.field.items():
            if context.target_card in cards:
                cards.remove(context.target_card)
                destroyed = True
                break
        
        if destroyed:
            player.reputation -= 1
            return EffectResult(
                success=True,
                message=f"Destruiste {context.target_card.name} perdiendo 1 de reputación",
                data={"destroyed_card": context.target_card.game_id, "self_damage": 1}
            )
        
        return EffectResult(False, "No se pudo destruir la carta")
    
    def _get_player(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None
    
    def _get_opponent(self, context: EffectContext):
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


# ============================================================================
# MAPEO DE CARTAS A EFECTOS
# ============================================================================

def get_card_effect(card_id: int) -> Optional[Effect]:
    """Retorna el efecto asociado a una carta específica"""
    
    # Mapeo de IDs de cartas a efectos
    effect_mapping: Dict[int, Callable[[], Effect]] = {
        # POLICE
        7: lambda: CancelEnemyActionEffect(),           # Sirenas en la noche
        8: lambda: ReturnToHandEffect("return_to_hand"), # Prisión preventiva
        9: lambda: DiscardRandomEffect("discard_random"), # Sobrecarga de trabajo
        10: lambda: HealReputationEffect("heal_2", 2),   # Protección del Estado
        11: lambda: DisableThiefAbilitiesEffect(),       # Luz de patrulla
        14: lambda: DrawCardsEffect("draw_2", 2),        # Pedir refuerzos
        15: lambda: PreventAttackEffect("prevent_attack_police"), # Control de multitudes
        
        # MAFIA
        22: lambda: DrawCardsEffect("draw_1_heal_1", 1), # Soborno (también cura 1)
        23: lambda: DestroyCardEffect("destroy_3", 3),   # Amenaza velada
        24: lambda: DealDamageEffect("damage_2", 2),     # Extorsión
        25: lambda: DrawCardsEffect("draw_3", 3),        # Red de influencias
        26: lambda: HealReputationEffect("heal_3", 3),   # Contrabando
        29: lambda: ReduceHandCostEffect(),              # Lavado de dinero
        30: lambda: IgnoreDefenseEffect(),               # Ataque sorpresa
        
        # DETECTIVE
        36: lambda: RevealAndDiscardEffect("reveal_discard"), # Tácticas de interrogatorio
        37: lambda: DestroyCardEffect("destroy_4", 4),   # Orden de registro
        38: lambda: DrawCardsEffect("draw_2_detective", 2), # Informantes confiables
        39: lambda: PreventAttackEffect("prevent_attack_detective"), # Evidencia incriminatoria
        43: lambda: RevealOpponentHandEffect("reveal_hand"), # Red de vigilancia
        44: lambda: HealReputationEffect("heal_2_detective", 2), # Testigo protegido
        45: lambda: DestroyCardEffect("destroy_5", 5),   # Emboscada
        
        # THIEF
        51: lambda: DrawCardsEffect("draw_1_heal_1_thief", 1), # Robo relámpago
        52: lambda: DestroyCardEffect("destroy_3_thief", 3), # Trampa para incautos
        54: lambda: ReturnDiscardedToDeckEffect(),       # Escape audaz
        55: lambda: HealReputationEffect("heal_3_thief", 3), # Red de contrabando
        58: lambda: DrawCardsEffect("draw_2_thief", 2),  # Botín valioso
        59: lambda: DealDamageEffect("damage_2_thief", 2), # Pacto oscuro
        60: lambda: DestroyCardEffect("destroy_4_thief", 4), # Golpe maestro
        
        # WILDCARD
        68: lambda: SelfDamageDestroyEffect(),           # Electrocutar
        69: lambda: SwapRandomHandCardEffect(),          # Cambio de identidad
        70: lambda: DrawAndDiscardEffect(),              # Caos controlado
        71: lambda: RevealAndStealCardEffect(),          # Mente maestra
        72: lambda: PlayCardFreeEffect(),                # Muestra gratuita
        73: lambda: DestroyAllCardsEffect(),             # Bomba atómica
        75: lambda: TakeCoinsLoseReputationEffect(),     # Misterio
    }
    
    if card_id in effect_mapping:
        return effect_mapping[card_id]()
    
    return None


def get_environment_effect(card_id: int) -> Optional[PassiveEffect]:
    """Retorna el efecto de ambiente de una carta específica"""
    
    environment_effects = {
        # Barricadas improvisadas (ID 13): +1 DEF a luchadores aliados
        13: lambda: StatModifierEffect(
            effect_id="barricadas",
            name="Barricadas improvisadas",
            description="Todos los LUCHADORES aliados ganan +1 DEF",
            defense_mod=1,
            filter_func=lambda card: card.zone == Zone.FIGHTER
        ),
        
        # Club nocturno (ID 28): +1 DEF a persuasores aliados
        28: lambda: StatModifierEffect(
            effect_id="club_nocturno",
            name="Club nocturno",
            description="Todos los PERSUASORES aliados ganan +1 DEF",
            defense_mod=1,
            filter_func=lambda card: card.zone == Zone.TALKER
        ),
        
        # Refugio seguro (ID 42): +1 DEF a persuasores aliados
        42: lambda: StatModifierEffect(
            effect_id="refugio_seguro",
            name="Refugio seguro",
            description="Todos los PERSUASORES aliados ganan +1 DEF",
            defense_mod=1,
            filter_func=lambda card: card.zone == Zone.TALKER
        ),
        
        # Callejones oscuros (ID 53): +1 ATK a luchadores aliados
        53: lambda: StatModifierEffect(
            effect_id="callejones_oscuros",
            name="Callejones oscuros",
            description="Todos los LUCHADORES aliados ganan +1 ATK",
            attack_mod=1,
            filter_func=lambda card: card.zone == Zone.FIGHTER
        ),
        
        # Circo ambulante (ID 74): +1 ATK y +1 DEF a todas las cartas aliadas
        74: lambda: StatModifierEffect(
            effect_id="circo_ambulante",
            name="Circo ambulante",
            description="Todas las cartas aliadas ganan +1 ATK y +1 DEF",
            attack_mod=1,
            defense_mod=1,
            filter_func=lambda card: True  # Aplica a todas
        ),
    }
    
    if card_id in environment_effects:
        return environment_effects[card_id]()
    
    return None


def get_leader_passive_effect(card_id: int) -> Optional[PassiveEffect]:
    """Retorna el efecto pasivo de un líder"""
    
    leader_effects = {
        # Don Vito (ID 16): Gana 1 reputación cuando un aliado es destruido
        16: lambda: OnAllyDestroyEffect(
            effect_id="don_vito_passive",
            name="Negociación",
            description="Gana 1 Reputación cada vez que un aliado es destruido",
            callback=lambda context: EffectResult(
                success=True,
                message="Don Vito ganó 1 de reputación",
                data={"reputation_gain": 1}
            )
        ),
        
        # Detective Marlowe (ID 31): Mira la mano del rival al inicio del turno
        31: lambda: OnTurnStartEffect(
            effect_id="marlowe_passive",
            name="Intuición",
            description="Mira la mano del rival al inicio de tu turno",
            callback=lambda context: RevealOpponentHandEffect("marlowe_reveal").execute(context)
        ),
        
        # Capitán O'Reilly (ID 1): -1 ATK a todos los LUCHADORES enemigos este turno
        1: lambda: OnTurnStartEffect(
            effect_id="oreilly_passive",
            name="Redada",
            description="-1 ATK a todos los LUCHADORES enemigos este turno",
            callback=lambda context: _capitan_oreilly_effect(context)
        ),
        
        # Sombra (ID 46): Al inicio del turno, si Sombra está en el campo, gana +1 ATK
        46: lambda: OnTurnStartEffect(
            effect_id="sombra_passive",
            name="Maestro del Sigilo",
            description="Gana +1 ATK al inicio de cada uno de tus turnos",
            callback=lambda context: _sombra_effect(context)
        ),
        
        # Risas el payaso alegre (ID 61): Lanza moneda al inicio del turno
        61: lambda: OnTurnStartEffect(
            effect_id="risas_passive",
            name="Caos",
            description="Lanza una moneda, si sale cara, roba una carta, si sale cruz, devuelve una carta de tu mano al mazo",
            callback=lambda context: _risas_effect(context)
        ),
    }
    
    if card_id in leader_effects:
        return leader_effects[card_id]()
    
    return None


def _capitan_oreilly_effect(context: EffectContext) -> EffectResult:
    """Efecto de Capitán O'Reilly: -1 ATK a todos los LUCHADORES enemigos"""
    player = None
    opponent = None
    
    for p in context.game_state.players:
        if p.id == context.source_player_id:
            player = p
        else:
            opponent = p
    
    if not opponent:
        return EffectResult(False, "Oponente no encontrado")
    
    # Aplicar -1 ATK a todos los luchadores enemigos en el campo
    affected_cards = []
    fighters = opponent.field.get(Zone.FIGHTER, [])
    
    for card in fighters:
        # Crear modificador temporal de -1 ATK para cada carta
        # El modificador se aplica solo a esta carta específica
        modifier = DelayedStatModifierEffect(
            effect_id=f"oreilly_debuff_{card.game_id}",
            name="Redada",
            description="-1 ATK (Redada del Capitán O'Reilly)",
            attack_mod=-1,
            defense_mod=0,
            duration_turns=1,
            filter_func=lambda c, target_id=card.game_id: c.game_id == target_id
        )
        effect_manager.add_async_effect(context.game_state.game_id, modifier)
        affected_cards.append(card.name)
    
    if affected_cards:
        return EffectResult(
            success=True,
            message=f"Redada: {', '.join(affected_cards)} perdieron 1 ATK este turno",
            data={
                "affected_cards": affected_cards,
                "attack_reduction": -1
            }
        )
    else:
        return EffectResult(
            success=True,
            message="Redada: No hay luchadores enemigos para afectar",
            data={}
        )


def _sombra_effect(context: EffectContext) -> EffectResult:
    """Efecto de Sombra: Gana +1 ATK permanente al inicio del turno"""
    player = None
    sombra_card = None
    
    for p in context.game_state.players:
        if p.id == context.source_player_id:
            player = p
            break
    
    if not player:
        return EffectResult(False, "Jugador no encontrado")
    
    # Buscar a Sombra en el campo (recorrer todas las zonas)
    for zone in Zone:
        cards_in_zone = player.field.get(zone, [])
        for card in cards_in_zone:
            if card.id == 46:  # ID de Sombra
                sombra_card = card
                break
        if sombra_card:
            break
    
    if not sombra_card:
        return EffectResult(
            success=False,
            message="Sombra no está en el campo"
        )
    
    # Aplicar +1 ATK permanente acumulativo (dura 999 turnos = permanente)
    modifier = DelayedStatModifierEffect(
        effect_id=f"sombra_buff_{sombra_card.game_id}_turn{context.game_state.turn}",
        name="Maestro del Sigilo",
        description="+1 ATK (Sigilo de Sombra)",
        attack_mod=1,
        defense_mod=0,
        duration_turns=999,  # Permanente mientras esté en el campo
        filter_func=lambda c, target_id=sombra_card.game_id: c.game_id == target_id
    )
    effect_manager.add_async_effect(context.game_state.game_id, modifier)
    
    # Calcular ATK total actual
    current_attack = sombra_card.attack
    attack_mod, _ = effect_manager.get_stat_modifiers(context.game_state.game_id, sombra_card)
    new_attack = current_attack + attack_mod
    
    return EffectResult(
        success=True,
        message=f"Sombra ganó +1 ATK (ahora tiene {new_attack} ATK)",
        data={
            "card_id": sombra_card.game_id,
            "attack_gain": 1,
            "new_attack": new_attack
        }
    )


def _risas_effect(context: EffectContext) -> EffectResult:
    """Efecto de Risas: Lanza moneda - cara roba 1, cruz devuelve 1 al mazo"""
    import random
    
    player = None
    for p in context.game_state.players:
        if p.id == context.source_player_id:
            player = p
            break
    
    if not player:
        return EffectResult(False, "Jugador no encontrado")
    
    # Lanzar moneda
    coin_flip = random.choice([True, False])  # True = cara, False = cruz
    
    if coin_flip:
        # CARA: Roba una carta
        if player.deck:
            card = player.deck.pop(0)
            player.hand.append(card)
            return EffectResult(
                success=True,
                message=f"¡Caos! La moneda cayó en CARA - Risas robó '{card.name}'",
                data={
                    "coin_result": "cara",
                    "action": "draw",
                    "card_drawn": card.name
                }
            )
        else:
            return EffectResult(
                success=True,
                message="¡Caos! La moneda cayó en CARA, pero el mazo está vacío",
                data={
                    "coin_result": "cara",
                    "action": "draw_failed"
                }
            )
    else:
        # CRUZ: Devolver carta aleatoria de la mano al mazo
        if len(player.hand) > 0:
            returned_card = random.choice(player.hand)
            player.hand.remove(returned_card)
            player.deck.append(returned_card)
            # Barajar el mazo
            random.shuffle(player.deck)
            
            return EffectResult(
                success=True,
                message=f"¡Caos! La moneda cayó en CRUZ - '{returned_card.name}' volvió al mazo",
                data={
                    "coin_result": "cruz",
                    "action": "return_to_deck",
                    "card_returned": returned_card.name
                },
                requires_choice=False
            )
        else:
            return EffectResult(
                success=True,
                message="¡Caos! La moneda cayó en CRUZ, pero no hay cartas en la mano",
                data={
                    "coin_result": "cruz",
                    "action": "return_failed"
                }
            )



# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def register_all_card_effects():
    """Registra todos los efectos de cartas en el gestor de efectos"""
    
    # Registrar efectos de cartas de efecto
    for card_id in [7, 8, 9, 10, 11, 14, 15, 22, 23, 24, 25, 26, 29, 30,
                    36, 37, 38, 39, 43, 44, 45, 51, 52, 54, 55, 58, 59, 60,
                    68, 69, 70, 71, 72, 73, 75]:
        effect = get_card_effect(card_id)
        if effect:
            effect_manager.register_effect(effect)
    
    # Registrar efectos de ambiente
    for card_id in [13, 28, 42, 53, 74]:
        effect = get_environment_effect(card_id)
        if effect:
            effect_manager.register_effect(effect)
    
    # Registrar efectos de líderes
    for card_id in [1, 16, 31, 46, 61]:
        effect = get_leader_passive_effect(card_id)
        if effect:
            effect_manager.register_effect(effect)


# Registrar todos los efectos al importar el módulo
register_all_card_effects()

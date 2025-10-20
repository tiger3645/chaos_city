"""
Sistema de efectos para cartas del juego Chaos City.

Este módulo implementa un sistema flexible de efectos que permite:
- Efectos inmediatos: se ejecutan una vez al activarse
- Efectos pasivos: modifican estadísticas o ejecutan acciones reactivas
- Efectos asíncronos: se activan una vez en el futuro

Algunos efectos requieren:
- Cartas objetivo (target)
- Información mostrada al jugador (reveal)
- Múltiples pasos (multi-step)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from enum import Enum
import random

if TYPE_CHECKING:
    from models import GameState, Player, Card, Zone

class EffectType(Enum):
    """Tipos de efectos disponibles"""
    IMMEDIATE = "immediate"  # Se ejecuta inmediatamente
    PASSIVE = "passive"      # Modifica estadísticas o ejecuta acciones reactivas
    ASYNC = "async"          # Se ejecuta una vez en el futuro


class EffectTrigger(Enum):
    """Eventos que pueden disparar efectos pasivos"""
    ON_PLAY = "on_play"                      # Al jugarse la carta
    ON_DESTROY = "on_destroy"                # Al destruirse la carta
    ON_ALLY_DESTROY = "on_ally_destroy"      # Al destruirse una carta aliada
    ON_ENEMY_DESTROY = "on_enemy_destroy"    # Al destruirse una carta enemiga
    ON_TURN_START = "on_turn_start"          # Al inicio del turno
    ON_TURN_END = "on_turn_end"              # Al final del turno
    ON_ATTACK = "on_attack"                  # Al atacar
    ON_RECEIVE_DAMAGE = "on_receive_damage"  # Al recibir daño
    ON_DRAW = "on_draw"                      # Al robar carta
    ALWAYS = "always"                        # Siempre activo (para modificadores de stats)


class EffectResult:
    """Resultado de la ejecución de un efecto"""
    def __init__(
        self,
        success: bool,
        message: str = "",
        requires_choice: bool = False,
        choices: Optional[List[Dict[str, Any]]] = None,
        revealed_info: Optional[Dict[str, Any]] = None,
        next_step: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.message = message
        self.requires_choice = requires_choice  # Si el efecto requiere que el jugador elija
        self.choices = choices or []            # Opciones disponibles para elegir
        self.revealed_info = revealed_info      # Información revelada al jugador
        self.next_step = next_step              # ID del siguiente paso (para efectos multi-paso)
        self.data = data or {}                  # Datos adicionales


@dataclass
class EffectContext:
    """Contexto en el que se ejecuta un efecto"""
    game_state: 'GameState'
    source_player_id: str           # Jugador que activó el efecto
    source_card: Optional['Card']   # Carta que generó el efecto
    target_card: Optional['Card'] = None
    target_player_id: Optional[str] = None
    trigger: Optional[EffectTrigger] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class Effect(ABC):
    """Clase base abstracta para todos los efectos"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        effect_type: EffectType
    ):
        self.effect_id = effect_id
        self.name = name
        self.description = description
        self.effect_type = effect_type
    
    @abstractmethod
    def can_execute(self, context: EffectContext) -> bool:
        """Verifica si el efecto puede ejecutarse en el contexto dado"""
        pass
    
    @abstractmethod
    def execute(self, context: EffectContext) -> EffectResult:
        """Ejecuta el efecto"""
        pass


class ImmediateEffect(Effect):
    """Efecto que se ejecuta inmediatamente al activarse"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        requires_target: bool = False,
        requires_choice: bool = False,
        is_multi_step: bool = False
    ):
        super().__init__(effect_id, name, description, EffectType.IMMEDIATE)
        self.requires_target = requires_target
        self.requires_choice = requires_choice
        self.is_multi_step = is_multi_step


class PassiveEffect(Effect):
    """Efecto pasivo que modifica estadísticas o reacciona a eventos"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        trigger: EffectTrigger,
        duration: Optional[int] = None  # None = permanente
    ):
        super().__init__(effect_id, name, description, EffectType.PASSIVE)
        self.trigger = trigger
        self.duration = duration  # En turnos, None = hasta que la carta salga del campo


class AsyncEffect(Effect):
    """Efecto que se activa una vez pero en el futuro"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        trigger: EffectTrigger,
        expires_after_turns: Optional[int] = None
    ):
        super().__init__(effect_id, name, description, EffectType.ASYNC)
        self.trigger = trigger
        self.expires_after_turns = expires_after_turns


# ============================================================================
# EFECTOS INMEDIATOS CONCRETOS
# ============================================================================

class DrawCardsEffect(ImmediateEffect):
    """Efecto que permite robar cartas"""
    
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
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
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
    
    def _get_player(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None


class DealDamageEffect(ImmediateEffect):
    """Efecto que inflige daño directo a la reputación"""
    
    def __init__(self, effect_id: str, damage: int, to_opponent: bool = True):
        super().__init__(
            effect_id=effect_id,
            name=f"Infligir {damage} de daño",
            description=f"Inflige {damage} de daño a la reputación"
        )
        self.damage = damage
        self.to_opponent = to_opponent
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        target_player = self._get_target_player(context)
        if not target_player:
            return EffectResult(False, "Objetivo no encontrado")
        
        target_player.reputation -= self.damage
        
        # Verificar si el juego terminó
        if target_player.reputation <= 0:
            context.game_state.winner = context.source_player_id
            return EffectResult(
                success=True,
                message=f"¡{target_player.name} ha sido derrotado!",
                data={"game_over": True, "winner": context.source_player_id}
            )
        
        return EffectResult(
            success=True,
            message=f"{target_player.name} perdió {self.damage} de reputación",
            data={"damage_dealt": self.damage}
        )
    
    def _get_target_player(self, context: EffectContext) -> Optional['Player']:
        if self.to_opponent:
            for player in context.game_state.players:
                if player.id != context.source_player_id:
                    return player
        else:
            for player in context.game_state.players:
                if player.id == context.source_player_id:
                    return player
        return None


class HealReputationEffect(ImmediateEffect):
    """Efecto que recupera reputación"""
    
    def __init__(self, effect_id: str, heal_amount: int):
        super().__init__(
            effect_id=effect_id,
            name=f"Recuperar {heal_amount} de reputación",
            description=f"Recupera {heal_amount} de reputación"
        )
        self.heal_amount = heal_amount
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        player = self._get_player(context)
        if not player:
            return EffectResult(False, "Jugador no encontrado")
        
        player.reputation += self.heal_amount
        
        return EffectResult(
            success=True,
            message=f"{player.name} recuperó {self.heal_amount} de reputación",
            data={"heal_amount": self.heal_amount}
        )
    
    def _get_player(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id == context.source_player_id:
                return player
        return None


class DestroyCardEffect(ImmediateEffect):
    """Efecto que destruye una carta objetivo"""
    
    def __init__(self, effect_id: str, max_value: Optional[int] = None):
        super().__init__(
            effect_id=effect_id,
            name="Destruir carta",
            description=f"Destruye una carta enemiga" + (f" de valor {max_value} o menos" if max_value else ""),
            requires_target=True
        )
        self.max_value = max_value
    
    def can_execute(self, context: EffectContext) -> bool:
        if not context.target_card:
            return False
        if self.max_value and context.target_card.value > self.max_value:
            return False
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        if not context.target_card:
            return EffectResult(False, "No se especificó carta objetivo")
        
        # Buscar la carta en el campo del oponente
        opponent = self._get_opponent(context)
        if not opponent:
            return EffectResult(False, "Oponente no encontrado")
        
        destroyed = False
        for zone, cards in opponent.field.items():
            if context.target_card in cards:
                cards.remove(context.target_card)
                destroyed = True
                break
        
        if destroyed:
            return EffectResult(
                success=True,
                message=f"Se destruyó {context.target_card.name}",
                data={"destroyed_card": context.target_card.game_id}
            )
        
        return EffectResult(False, "No se pudo destruir la carta")
    
    def _get_opponent(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


class ReturnToHandEffect(ImmediateEffect):
    """Efecto que devuelve una carta a la mano"""
    
    def __init__(self, effect_id: str, to_owner_hand: bool = True):
        super().__init__(
            effect_id=effect_id,
            name="Devolver carta a la mano",
            description="Devuelve una carta enemiga a la mano",
            requires_target=True
        )
        self.to_owner_hand = to_owner_hand
    
    def can_execute(self, context: EffectContext) -> bool:
        return context.target_card is not None
    
    def execute(self, context: EffectContext) -> EffectResult:
        if not context.target_card:
            return EffectResult(False, "No se especificó carta objetivo")
        
        opponent = self._get_opponent(context)
        if not opponent:
            return EffectResult(False, "Oponente no encontrado")
        
        # Buscar y remover la carta del campo
        returned = False
        for zone, cards in opponent.field.items():
            if context.target_card in cards:
                cards.remove(context.target_card)
                opponent.hand.append(context.target_card)
                returned = True
                break
        
        if returned:
            return EffectResult(
                success=True,
                message=f"{context.target_card.name} fue devuelta a la mano",
                data={"returned_card": context.target_card.game_id}
            )
        
        return EffectResult(False, "No se pudo devolver la carta")
    
    def _get_opponent(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


class DiscardRandomEffect(ImmediateEffect):
    """Efecto que hace descartar una carta al azar al oponente"""
    
    def __init__(self, effect_id: str):
        super().__init__(
            effect_id=effect_id,
            name="Descartar carta al azar",
            description="El rival descarta una carta al azar"
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        opponent = self._get_opponent(context)
        return opponent is not None and len(opponent.hand) > 0
    
    def execute(self, context: EffectContext) -> EffectResult:
        opponent = self._get_opponent(context)
        if not opponent or not opponent.hand:
            return EffectResult(False, "El oponente no tiene cartas")
        
        discarded_card = random.choice(opponent.hand)
        opponent.hand.remove(discarded_card)
        
        return EffectResult(
            success=True,
            message=f"{opponent.name} descartó {discarded_card.name}",
            data={"discarded_card": discarded_card.game_id}
        )
    
    def _get_opponent(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


class RevealOpponentHandEffect(ImmediateEffect):
    """Efecto que permite ver la mano del oponente"""
    
    def __init__(self, effect_id: str):
        super().__init__(
            effect_id=effect_id,
            name="Ver mano del rival",
            description="Mira la mano del rival"
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        opponent = self._get_opponent(context)
        if not opponent:
            return EffectResult(False, "Oponente no encontrado")
        
        hand_info = [
            {
                "game_id": card.game_id,
                "name": card.name,
                "value": card.value,
                "type": card.type.value,
                "faction": card.faction.value
            }
            for card in opponent.hand
        ]
        
        return EffectResult(
            success=True,
            message=f"Viendo la mano de {opponent.name}",
            revealed_info={"opponent_hand": hand_info}
        )
    
    def _get_opponent(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


class RevealAndDiscardEffect(ImmediateEffect):
    """Efecto multi-paso: ver la mano del rival y elegir una carta para descartar"""
    
    def __init__(self, effect_id: str):
        super().__init__(
            effect_id=effect_id,
            name="Interrogatorio",
            description="Mira la mano del rival y descarta una carta",
            requires_choice=True,
            is_multi_step=True
        )
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        # Paso 1: Revelar mano
        if "chosen_card" not in context.additional_data:
            opponent = self._get_opponent(context)
            if not opponent or not opponent.hand:
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
                message="Elige una carta para descartar",
                requires_choice=True,
                choices=choices,
                next_step="discard_chosen"
            )
        
        # Paso 2: Descartar carta elegida
        opponent = self._get_opponent(context)
        if not opponent:
            return EffectResult(False, "Oponente no encontrado")
        
        chosen_game_id = context.additional_data.get("chosen_card")
        card_to_discard = None
        for card in opponent.hand:
            if card.game_id == chosen_game_id:
                card_to_discard = card
                break
        
        if card_to_discard:
            opponent.hand.remove(card_to_discard)
            return EffectResult(
                success=True,
                message=f"{opponent.name} descartó {card_to_discard.name}",
                data={"discarded_card": card_to_discard.game_id}
            )
        
        return EffectResult(False, "Carta no encontrada")
    
    def _get_opponent(self, context: EffectContext) -> Optional['Player']:
        for player in context.game_state.players:
            if player.id != context.source_player_id:
                return player
        return None


# ============================================================================
# EFECTOS PASIVOS CONCRETOS
# ============================================================================

class StatModifierEffect(PassiveEffect):
    """Efecto pasivo que modifica estadísticas de cartas"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        attack_mod: int = 0,
        defense_mod: int = 0,
        filter_func: Optional[Callable[['Card'], bool]] = None
    ):
        super().__init__(
            effect_id=effect_id,
            name=name,
            description=description,
            trigger=EffectTrigger.ALWAYS
        )
        self.attack_mod = attack_mod
        self.defense_mod = defense_mod
        self.filter_func = filter_func  # Función para filtrar qué cartas se modifican
    
    def can_execute(self, context: EffectContext) -> bool:
        return True
    
    def execute(self, context: EffectContext) -> EffectResult:
        """Este efecto no se 'ejecuta', sino que se aplica continuamente"""
        return EffectResult(
            success=True,
            message=f"Modificador activo: ATK{self.attack_mod:+d} DEF{self.defense_mod:+d}"
        )
    
    def applies_to(self, card: 'Card') -> bool:
        """Verifica si el modificador se aplica a una carta específica"""
        if self.filter_func:
            return self.filter_func(card)
        return True


class OnAllyDestroyEffect(PassiveEffect):
    """Efecto que se activa cuando un aliado es destruido"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        callback: Callable[[EffectContext], EffectResult]
    ):
        super().__init__(
            effect_id=effect_id,
            name=name,
            description=description,
            trigger=EffectTrigger.ON_ALLY_DESTROY
        )
        self.callback = callback
    
    def can_execute(self, context: EffectContext) -> bool:
        return context.trigger == EffectTrigger.ON_ALLY_DESTROY
    
    def execute(self, context: EffectContext) -> EffectResult:
        return self.callback(context)


class OnTurnStartEffect(PassiveEffect):
    """Efecto que se activa al inicio del turno"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        callback: Callable[[EffectContext], EffectResult]
    ):
        super().__init__(
            effect_id=effect_id,
            name=name,
            description=description,
            trigger=EffectTrigger.ON_TURN_START
        )
        self.callback = callback
    
    def can_execute(self, context: EffectContext) -> bool:
        return context.trigger == EffectTrigger.ON_TURN_START
    
    def execute(self, context: EffectContext) -> EffectResult:
        return self.callback(context)


# ============================================================================
# EFECTOS ASÍNCRONOS CONCRETOS
# ============================================================================

class DelayedStatModifierEffect(AsyncEffect):
    """Efecto que modifica stats durante un número de turnos"""
    
    def __init__(
        self,
        effect_id: str,
        name: str,
        description: str,
        attack_mod: int = 0,
        defense_mod: int = 0,
        duration_turns: int = 1,
        filter_func: Optional[Callable[['Card'], bool]] = None
    ):
        super().__init__(
            effect_id=effect_id,
            name=name,
            description=description,
            trigger=EffectTrigger.ON_TURN_END,
            expires_after_turns=duration_turns
        )
        self.attack_mod = attack_mod
        self.defense_mod = defense_mod
        self.filter_func = filter_func
        self.turns_remaining = duration_turns
    
    def can_execute(self, context: EffectContext) -> bool:
        return self.turns_remaining > 0
    
    def execute(self, context: EffectContext) -> EffectResult:
        if context.trigger == EffectTrigger.ON_TURN_END:
            self.turns_remaining -= 1
            
            if self.turns_remaining <= 0:
                return EffectResult(
                    success=True,
                    message=f"El efecto {self.name} ha expirado",
                    data={"expired": True}
                )
        
        return EffectResult(
            success=True,
            message=f"Efecto activo por {self.turns_remaining} turnos más"
        )
    
    def applies_to(self, card: 'Card') -> bool:
        """Verifica si el modificador se aplica a una carta específica"""
        if self.filter_func:
            return self.filter_func(card)
        return True


class PreventNextAttackEffect(AsyncEffect):
    """Efecto que previene el próximo ataque directo"""
    
    def __init__(self, effect_id: str):
        super().__init__(
            effect_id=effect_id,
            name="Prevenir ataque",
            description="Previene el siguiente ataque directo",
            trigger=EffectTrigger.ON_RECEIVE_DAMAGE
        )
        self.consumed = False
    
    def can_execute(self, context: EffectContext) -> bool:
        return not self.consumed and context.trigger == EffectTrigger.ON_RECEIVE_DAMAGE
    
    def execute(self, context: EffectContext) -> EffectResult:
        self.consumed = True
        return EffectResult(
            success=True,
            message="¡Ataque directo prevenido!",
            data={"damage_prevented": True, "consumed": True}
        )


# ============================================================================
# GESTOR DE EFECTOS
# ============================================================================

class EffectManager:
    """Gestor centralizado de efectos"""
    
    def __init__(self):
        self.registered_effects: Dict[str, Effect] = {}
        self.active_passive_effects: Dict[str, List[PassiveEffect]] = {}  # game_id -> effects
        self.active_async_effects: Dict[str, List[AsyncEffect]] = {}      # game_id -> effects
    
    def register_effect(self, effect: Effect):
        """Registra un nuevo tipo de efecto"""
        self.registered_effects[effect.effect_id] = effect
    
    def execute_immediate_effect(
        self,
        effect_id: str,
        context: EffectContext
    ) -> EffectResult:
        """Ejecuta un efecto inmediato"""
        effect = self.registered_effects.get(effect_id)
        if not effect:
            return EffectResult(False, f"Efecto {effect_id} no encontrado")
        
        if effect.effect_type != EffectType.IMMEDIATE:
            return EffectResult(False, f"Efecto {effect_id} no es inmediato")
        
        if not effect.can_execute(context):
            return EffectResult(False, "El efecto no puede ejecutarse en este contexto")
        
        return effect.execute(context)
    
    def add_passive_effect(self, game_id: str, effect: PassiveEffect):
        """Añade un efecto pasivo al juego"""
        if game_id not in self.active_passive_effects:
            self.active_passive_effects[game_id] = []
        self.active_passive_effects[game_id].append(effect)
    
    def add_async_effect(self, game_id: str, effect: AsyncEffect):
        """Añade un efecto asíncrono al juego"""
        if game_id not in self.active_async_effects:
            self.active_async_effects[game_id] = []
        self.active_async_effects[game_id].append(effect)
    
    def trigger_effects(
        self,
        game_id: str,
        trigger: EffectTrigger,
        context: EffectContext
    ) -> List[EffectResult]:
        """Dispara todos los efectos que respondan a un trigger específico"""
        results = []
        
        # Efectos pasivos
        passive_effects = self.active_passive_effects.get(game_id, [])
        for effect in passive_effects:
            if effect.trigger == trigger and effect.can_execute(context):
                result = effect.execute(context)
                results.append(result)
        
        # Efectos asíncronos
        async_effects = self.active_async_effects.get(game_id, [])
        expired_effects = []
        for effect in async_effects:
            if effect.trigger == trigger and effect.can_execute(context):
                result = effect.execute(context)
                results.append(result)
                
                # Marcar para eliminar si expiró
                if result.data.get("expired") or result.data.get("consumed"):
                    expired_effects.append(effect)
        
        # Eliminar efectos expirados
        for effect in expired_effects:
            self.active_async_effects[game_id].remove(effect)
        
        return results
    
    def get_stat_modifiers(
        self,
        game_id: str,
        card: 'Card'
    ) -> tuple[int, int]:
        """Calcula los modificadores totales de ATK y DEF para una carta"""
        total_attack_mod = 0
        total_defense_mod = 0
        
        # Efectos pasivos
        passive_effects = self.active_passive_effects.get(game_id, [])
        for effect in passive_effects:
            if isinstance(effect, StatModifierEffect) and effect.applies_to(card):
                total_attack_mod += effect.attack_mod
                total_defense_mod += effect.defense_mod
        
        # Efectos asíncronos
        async_effects = self.active_async_effects.get(game_id, [])
        for effect in async_effects:
            if isinstance(effect, DelayedStatModifierEffect) and effect.applies_to(card):
                total_attack_mod += effect.attack_mod
                total_defense_mod += effect.defense_mod
        
        return total_attack_mod, total_defense_mod
    
    def clear_game_effects(self, game_id: str):
        """Limpia todos los efectos de un juego"""
        if game_id in self.active_passive_effects:
            del self.active_passive_effects[game_id]
        if game_id in self.active_async_effects:
            del self.active_async_effects[game_id]


# Instancia global del gestor de efectos
effect_manager = EffectManager()

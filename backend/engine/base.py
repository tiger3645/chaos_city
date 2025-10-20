import random
import uuid
from typing import Dict, List, Optional, Tuple, Any
from models import GameState, Player, Card, CARDS_DB, get_starter_deck, Faction, Zone, CardType, Phase
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

class GameEngine:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        # Registrar todos los efectos de cartas
        register_all_card_effects()
    
    def create_game(self, player_name: str, player_faction: Faction) -> Tuple[str, str]:
        """Create a new game with one player

        Returns a tuple (game_id, player_id) so the caller can inform the client
        which player id was assigned to the creator.
        """
        game_id = str(uuid.uuid4())

        # Create player with starter deck
        player = self._create_player(player_name, player_faction)

        # Create game state with single player
        game = GameState(
            game_id=game_id,
            players=[player]
        )

        # Don't deal initial hands yet - wait for second player

        self.games[game_id] = game
        return game_id, player.id
    
    def join_game(self, game_id: str, player_name: str, player_faction: Faction) -> Optional[str]:
        """Add a second player to an existing game.

        Returns the assigned player_id on success, or None on failure.
        """
        if game_id not in self.games:
            return None

        game = self.games[game_id]

        # Check if game already has 2 players
        if len(game.players) >= 2:
            return None

        # Create and add second player
        player = self._create_player(player_name, player_faction)
        game.players.append(player)

        # Now deal initial hands to both players
        self._deal_initial_hands(game)

        return player.id
    
    def _create_player(self, name: str, faction: Faction) -> Player:
        """Create a player with a starter deck"""
        player_id = str(uuid.uuid4())
        
        # Get starter deck card IDs
        starter_card_ids = get_starter_deck(faction)
        
        # Convert to Card objects and shuffle
        deck = [CARDS_DB[card_id] for card_id in starter_card_ids if card_id in CARDS_DB]
        for card in deck:
            card.game_id = str(uuid.uuid4())  # Assign unique game instance ID to each card
        
        random.shuffle(deck)
        
        return Player(
            id=player_id,
            name=name,
            deck=deck,
        )
    
    def set_starting_player(self, game_id: str, player_id: str) -> bool:
        """Set which player starts the game"""
        if game_id not in self.games:
            return False
        
        game = self.games[game_id]
        
        for i, player in enumerate(game.players):
            if player.id == player_id:
                game.current_player = i
                return True
        
        return False

    def _deal_initial_hands(self, game: GameState):
        """Deal 5 cards to each player"""
        for player in game.players:
            for _ in range(5):
                if player.deck:
                    card = player.deck.pop()
                    player.hand.append(card)

            # Give each player 5 coins to start
            player.coins += 5
            game.available_coins -= 5

    def draw_card(self, game_id: str, player_id: str) -> Optional[Card]:
        """Player draws a card from their deck"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        if not player or not player.deck:
            return None
        
        if game.phase == "draw":
            card = player.deck.pop()
            player.hand.append(card)
            game.phase = "deploy"
            return card

        return None
    
    def continue_effect(self, game_id: str, player_id: str, effect_id: str, chosen_value: Any) -> Dict[str, Any]:
        """Continue a multi-step effect with player's choice
        
        Args:
            game_id: Game ID
            player_id: Player making the choice
            effect_id: ID of the effect being continued
            chosen_value: The value chosen by the player (card ID, amount, etc.)
        
        Returns:
            Dict with effect result
        """
        if game_id not in self.games:
            return {"success": False, "message": "Game not found"}
        
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Get the effect
        effect = effect_manager.registered_effects.get(effect_id)
        
        if not effect:
            return {"success": False, "message": "Effect not found"}
        
        # Create context with the chosen value
        context = EffectContext(
            game_state=game,
            source_player_id=player_id,
            source_card=None,
            additional_data={
                "chosen_card": chosen_value,
                "discarded_card": chosen_value,
                "stolen_card": chosen_value,
                "coins_taken": chosen_value,
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

    def get_turn_coins(self, game_id: str, player_id: str) -> Optional[int]:
        """Get 3 coins for the player's turn"""
        if game_id not in self.games:
            return None

        game = self.games[game_id]
        player = self._get_player(game, player_id)

        if not player:
            return None
        
        # Ensure it's the player's turn
        if game.players[game.current_player].id != player_id:
            return None

        # Give player up to 3 coins, limited by available coins in game
        if game.available_coins < 3:
            player.coins += game.available_coins
            game.available_coins = 0

            return player.coins
        
        player.coins += 3
        game.available_coins -= 3
        return player.coins

    def play_card(self, game_id: str, player_id: str, card_game_id: str, zone: Optional[Zone] = None) -> Dict[str, Any]:
        """Player plays a card from their hand
        
        Returns:
            Dict with keys:
                - success: bool
                - message: str
                - requires_choice: bool (optional, for multi-step effects)
                - choices: list (optional, for multi-step effects)
                - revealed_info: dict (optional, for reveal effects)
                - next_step: str (optional, for multi-step effects)
                - data: dict (optional, additional effect data)
        """
        if game_id not in self.games:
            return {"success": False, "message": "Game not found"}
        
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        if not player:
            return {"success": False, "message": "Player not found"}
        
        # Find card in hand
        card = None
        card_index = -1
        for i, hand_card in enumerate(player.hand):
            if hand_card.game_id == card_game_id:
                card = hand_card
                card_index = i
                break
        
        if not card:
            return {"success": False, "message": "Card not found in hand"}
        
        # Check if player has enough coins
        if player.coins < card.value:
            return {"success": False, "message": "Not enough coins"}
        
        # Remove card from hand
        player.hand.pop(card_index)
        
        # Deduct coins
        player.coins -= card.value
        
        # Create effect context
        context = EffectContext(
            game_state=game,
            source_player_id=player_id,
            source_card=card
        )
        
        # Handle based on card type
        if card.type == CardType.EFFECT:
            # Effect card: execute immediately
            effect = get_card_effect(card.id)
            
            if not effect:
                return {
                    "success": False,
                    "message": f"Effect not implemented for {card.name}"
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
        
        elif card.type == CardType.ENVIRONMENT:
            # Environment card: replace active environment
            if game.active_environment_card:
                # TODO: Remove old environment effect
                # For now, we'll just replace it
                pass
            
            game.active_environment_card = card
            
            # Activate passive effect
            env_effect = get_environment_effect(card.id)
            if env_effect:
                effect_manager.add_passive_effect(game.game_id, env_effect)
            
            return {
                "success": True,
                "message": f"{card.name} is now active"
            }
        
        elif card.type in (CardType.CHARACTER, CardType.LEADER):
            # Character/Leader: place on field
            if not card.zone:
                # Return card to hand if no zone
                player.hand.append(card)
                player.coins += card.value  # Refund coins
                return {
                    "success": False,
                    "message": "Card has no zone defined"
                }
            
            player.field[card.zone].append(card)
            
            # If it's a leader, activate passive effect
            if card.type == CardType.LEADER:
                leader_effect = get_leader_passive_effect(card.id)
                if leader_effect:
                    effect_manager.add_passive_effect(game.game_id, leader_effect)
            
            # Trigger ON_PLAY effects
            trigger_results = effect_manager.trigger_effects(
                game_id=game.game_id,
                trigger=EffectTrigger.ON_PLAY,
                context=context
            )
            
            triggered_messages = [r.message for r in trigger_results if r.success]
            
            return {
                "success": True,
                "message": f"{card.name} was placed in {card.zone.value}",
                "triggered_effects": triggered_messages
            }
        
        return {"success": False, "message": "Unknown card type"}

    def attack(self, game_id: str, player_id: str, attacker_id: str, defender_id: Optional[str], target_zone: Zone) -> Dict:
        """Perform an attack with a character
        
        Args:
            defender_id: ID of defender card, or None for direct attack
        """
        if game_id not in self.games:
            return {"success": False, "message": "Game not found"}
        
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        opponent = self._get_opponent(game, player_id)
        
        if not player or not opponent:
            return {"success": False, "message": "Player not found"}
        
        # Find attacker
        attacker = None
        for zone_cards in player.field.values():
            for card in zone_cards:
                if card.game_id == attacker_id:
                    attacker = card
                    break
        
        if not attacker:
            return {"success": False, "message": "Attacker not found"}
        
        # Get stat modifiers for attacker
        attack_mod, _ = effect_manager.get_stat_modifiers(game.game_id, attacker)
        effective_attack = attacker.attack + attack_mod
        
        # Find target card if specified
        target = None
        if defender_id:
            defenders = opponent.field[target_zone]
            target = next((card for card in defenders if card.game_id == defender_id), None)
            if not target:
                return {"success": False, "message": "Defender not found"}
        
        # Create context for attack triggers
        context = EffectContext(
            game_state=game,
            source_player_id=player_id,
            source_card=attacker,
            target_card=target,
            trigger=EffectTrigger.ON_ATTACK
        )
        
        # Trigger ON_ATTACK effects
        attack_effects = effect_manager.trigger_effects(
            game_id=game.game_id,
            trigger=EffectTrigger.ON_ATTACK,
            context=context
        )
        
        # Check for special attack effects (ignore defense, etc.)
        ignore_defense = any(
            effect.data.get("ignore_defense", False)
            for effect in attack_effects
        )
        
        if target:
            # Attack target card
            target_attack_mod, target_def_mod = effect_manager.get_stat_modifiers(
                game.game_id, target
            )
            effective_defense = target.defense + target_def_mod
            
            if ignore_defense:
                # Ignore defense, deal full attack as damage
                damage = effective_attack
                target.defense = 0
            else:
                damage = effective_attack
                target.defense -= damage
            
            if target.defense <= 0:
                # Card destroyed
                opponent.field[target_zone].remove(target)
                
                # Trigger ON_DESTROY
                destroy_context = EffectContext(
                    game_state=game,
                    source_player_id=opponent.id,
                    source_card=target,
                    trigger=EffectTrigger.ON_DESTROY
                )
                effect_manager.trigger_effects(
                    game_id=game.game_id,
                    trigger=EffectTrigger.ON_DESTROY,
                    context=destroy_context
                )
                
                # Trigger ON_ENEMY_DESTROY for attacker's player
                enemy_destroy_context = EffectContext(
                    game_state=game,
                    source_player_id=player_id,
                    source_card=target,
                    trigger=EffectTrigger.ON_ENEMY_DESTROY
                )
                effect_manager.trigger_effects(
                    game_id=game.game_id,
                    trigger=EffectTrigger.ON_ENEMY_DESTROY,
                    context=enemy_destroy_context
                )
                
                # Trigger ON_ALLY_DESTROY for opponent
                ally_destroy_context = EffectContext(
                    game_state=game,
                    source_player_id=opponent.id,
                    source_card=target,
                    trigger=EffectTrigger.ON_ALLY_DESTROY
                )
                ally_effects = effect_manager.trigger_effects(
                    game_id=game.game_id,
                    trigger=EffectTrigger.ON_ALLY_DESTROY,
                    context=ally_destroy_context
                )
                
                # Apply ally destroy effects (like Don Vito gaining reputation)
                for effect_result in ally_effects:
                    if effect_result.success and "reputation_gain" in effect_result.data:
                        opponent.reputation += effect_result.data["reputation_gain"]
                
                return {
                    "success": True,
                    "message": f"{attacker.name} destroyed {target.name}",
                    "destroyed": target.name,
                    "attacker_stats": f"{attacker.attack + attack_mod}/{attacker.defense}"
                }
            else:
                return {
                    "success": True,
                    "message": f"{attacker.name} dealt {damage} damage to {target.name}",
                    "damage": damage,
                    "remaining_defense": target.defense,
                    "attacker_stats": f"{attacker.attack + attack_mod}/{attacker.defense}"
                }
        else:
            # Direct attack to reputation
            # Check for prevention effects
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
                    "message": "Direct attack was prevented!",
                    "prevented": True
                }
            
            opponent.reputation -= effective_attack
            
            if opponent.reputation <= 0:
                game.winner = player.id
                # Clean up effects when game ends
                effect_manager.clear_game_effects(game.game_id)
                return {
                    "success": True,
                    "message": f"{attacker.name} dealt {effective_attack} damage. {player.name} wins!",
                    "game_over": True,
                    "winner": player.name
                }
            
            return {
                "success": True,
                "message": f"{attacker.name} dealt {effective_attack} damage to reputation",
                "reputation_damage": effective_attack,
                "opponent_reputation": opponent.reputation
            }
    
    def next_phase(self, game_id: str) -> Dict[str, Any]:
        """Advance to next phase or next player's turn
        
        Returns:
            Dict with phase change info and triggered effects
        """
        if game_id not in self.games:
            return {"success": False, "message": "Game not found"}
        
        game = self.games[game_id]
        current_player = game.players[game.current_player]
        
        phases: List[Phase] = ["draw", "deploy", "action"]
        current_index = phases.index(game.phase)
        
        triggered_messages = []
        
        if current_index < len(phases) - 1:
            # Next phase
            game.phase = phases[current_index + 1]
            return {
                "success": True,
                "phase": game.phase,
                "message": f"Phase changed to {game.phase}"
            }
        else:
            # End of turn - trigger ON_TURN_END effects
            end_context = EffectContext(
                game_state=game,
                source_player_id=current_player.id,
                source_card=None,
                trigger=EffectTrigger.ON_TURN_END
            )
            
            end_effects = effect_manager.trigger_effects(
                game_id=game.game_id,
                trigger=EffectTrigger.ON_TURN_END,
                context=end_context
            )
            
            for effect in end_effects:
                if effect.success:
                    triggered_messages.append(effect.message)
            
            # Next player's turn
            game.current_player = (game.current_player + 1) % len(game.players)
            game.phase = "draw"
            
            new_current_player = game.players[game.current_player]
            
            # Give player 3 coins at start of turn
            self.get_turn_coins(game_id, new_current_player.id)
            
            if game.current_player == 0:  # Back to first player
                game.turn += 1
            
            # Trigger ON_TURN_START effects for new player
            start_context = EffectContext(
                game_state=game,
                source_player_id=new_current_player.id,
                source_card=None,
                trigger=EffectTrigger.ON_TURN_START
            )
            
            start_effects = effect_manager.trigger_effects(
                game_id=game.game_id,
                trigger=EffectTrigger.ON_TURN_START,
                context=start_context
            )
            
            for effect in start_effects:
                if effect.success:
                    triggered_messages.append(effect.message)
            
            return {
                "success": True,
                "phase": game.phase,
                "turn": game.turn,
                "current_player": new_current_player.name,
                "message": f"Turn changed to {new_current_player.name}",
                "triggered_effects": triggered_messages
            }
    
    def get_card_effective_stats(self, game_id: str, card_game_id: str) -> Optional[Dict[str, int]]:
        """Get the effective attack and defense of a card including modifiers
        
        Returns:
            Dict with 'attack' and 'defense' keys, or None if card not found
        """
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        
        # Find card in any player's field
        for player in game.players:
            for zone_cards in player.field.values():
                for card in zone_cards:
                    if card.game_id == card_game_id:
                        attack_mod, defense_mod = effect_manager.get_stat_modifiers(
                            game_id, card
                        )
                        return {
                            "attack": card.attack + attack_mod,
                            "defense": card.defense + defense_mod,
                            "base_attack": card.attack,
                            "base_defense": card.defense,
                            "attack_mod": attack_mod,
                            "defense_mod": defense_mod
                        }
        
        return None

    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get current game state"""
        return self.games.get(game_id)
    
    def end_game(self, game_id: str) -> bool:
        """End a game and clean up resources
        
        Returns:
            True if game was ended successfully
        """
        if game_id not in self.games:
            return False
        
        # Clean up all effects for this game
        effect_manager.clear_game_effects(game_id)
        
        # Remove game from active games
        del self.games[game_id]
        
        return True
    
    def _get_player(self, game: GameState, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        for player in game.players:
            if player.id == player_id:
                return player
        return None
    
    def _get_opponent(self, game: GameState, player_id: str) -> Optional[Player]:
        """Get opponent player"""
        for player in game.players:
            if player.id != player_id:
                return player
        return None

    # Temp helpers to change game state for testing
    def add_player_reputation(self, game_id: str, player_id: str, reputation: int) -> bool:
        """Add reputation for a player (for testing)"""
        if game_id not in self.games:
            return False
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        if not player:
            return False
        player.reputation += reputation
        return True

    def add_player_coins(self, game_id: str, player_id: str, coins: int) -> bool:
        """Add coins to a player (for testing)"""
        if game_id not in self.games:
            return False
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        if not player:
            return False
        player.coins += coins
        game.available_coins -= coins
        return True
    
    def add_card_defense(self, game_id: str, player_id: str, card_game_id: str, defense: int) -> bool:
        """Add defense to a card (for testing)"""
        if game_id not in self.games:
            return False
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        if not player:
            return False
        for zone_cards in player.field.values():
            for card in zone_cards:
                if card.game_id == card_game_id:
                    card.defense += defense
                    return True
        return False
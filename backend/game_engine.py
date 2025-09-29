import random
import uuid
from typing import Dict, List, Optional
from models import GameState, Player, Card, CARDS_DB, get_starter_deck, Faction, Zone, CardType, Phase

class GameEngine:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
    
    def create_game(self, player_name: str, player_faction: Faction) -> str:
        """Create a new game with one player"""
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
        return game_id
    
    def join_game(self, game_id: str, player_name: str, player_faction: Faction) -> bool:
        """Add a second player to an existing game"""
        if game_id not in self.games:
            return False
        
        game = self.games[game_id]
        
        # Check if game already has 2 players
        if len(game.players) >= 2:
            return False
        
        # Create and add second player
        player = self._create_player(player_name, player_faction)
        game.players.append(player)
        
        # Now deal initial hands to both players
        self._deal_initial_hands(game)
        
        return True
    
    def _create_player(self, name: str, faction: Faction) -> Player:
        """Create a player with a starter deck"""
        player_id = str(uuid.uuid4())
        
        # Get starter deck card IDs
        starter_card_ids = get_starter_deck(faction)
        
        # Convert to Card objects and shuffle
        deck = [CARDS_DB[card_id] for card_id in starter_card_ids if card_id in CARDS_DB]
        random.shuffle(deck)
        
        # Find leader card
        leader = None
        for card in deck:
            if card.card_type == CardType.LEADER:
                leader = card
                break
        
        return Player(
            id=player_id,
            name=name,
            deck=deck,
            leader=leader
        )
    
    def _deal_initial_hands(self, game: GameState):
        """Deal 5 cards to each player"""
        for player in game.players:
            for _ in range(5):
                if player.deck:
                    card = player.deck.pop()
                    player.hand.append(card)
    
    def draw_card(self, game_id: str, player_id: str) -> Optional[Card]:
        """Player draws a card from their deck"""
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        if not player or not player.deck:
            return None
        
        card = player.deck.pop()
        player.hand.append(card)
        return card
    
    def play_card(self, game_id: str, player_id: str, card_id: str, zone: Optional[Zone] = None) -> bool:
        """Player plays a card from their hand"""
        if game_id not in self.games:
            return False
        
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        if not player:
            return False
        
        # Find card in hand
        card = None
        for i, hand_card in enumerate(player.hand):
            if hand_card.id == card_id:
                card = player.hand.pop(i)
                break
        
        if not card:
            return False
        
        # Place card based on type
        if card.card_type == CardType.CHARACTER and card.zone:
            player.field[card.zone].append(card)
        elif card.card_type == CardType.EFFECT:
            # Effects are played immediately and discarded
            self._apply_effect(game, player_id, card)
        elif card.card_type == CardType.ENVIRONMENT and zone:
            # Place environment in specified zone
            game.active_environments[zone] = card
        
        return True
    
    def _apply_effect(self, game: GameState, player_id: str, effect_card: Card):
        """Apply the effect of an effect card"""
        # This would contain the logic for different effect cards
        # For now, just a placeholder
        pass
    
    def attack(self, game_id: str, player_id: str, attacker_id: str, target_zone: Zone) -> Dict:
        """Perform an attack with a character"""
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
                if card.id == attacker_id:
                    attacker = card
                    break
        
        if not attacker:
            return {"success": False, "message": "Attacker not found"}
        
        # Check for defenders in target zone
        defenders = opponent.field[target_zone]
        
        if defenders:
            # Attack first defender
            target = defenders[0]
            damage_dealt = attacker.attack
            
            # Apply damage
            target.defense -= damage_dealt
            
            if target.defense <= 0:
                # Remove destroyed card
                opponent.field[target_zone].remove(target)
                return {
                    "success": True, 
                    "message": f"{attacker.name} destroyed {target.name}",
                    "destroyed": target.name
                }
            else:
                return {
                    "success": True,
                    "message": f"{attacker.name} dealt {damage_dealt} damage to {target.name}",
                    "damage": damage_dealt
                }
        else:
            # Direct damage to reputation
            damage = attacker.attack
            opponent.reputation -= damage
            
            if opponent.reputation <= 0:
                game.winner = player.id
                return {
                    "success": True,
                    "message": f"{attacker.name} dealt {damage} damage to reputation. {player.name} wins!",
                    "game_over": True,
                    "winner": player.name
                }
            
            return {
                "success": True,
                "message": f"{attacker.name} dealt {damage} damage to reputation",
                "reputation_damage": damage
            }
    
    def next_phase(self, game_id: str) -> bool:
        """Advance to next phase or next player's turn"""
        if game_id not in self.games:
            return False
        
        game = self.games[game_id]
        
        phases: List[Phase] = ["draw", "deploy", "action", "resolution"]
        current_index = phases.index(game.phase)
        
        if current_index < len(phases) - 1:
            # Next phase
            game.phase = phases[current_index + 1]
        else:
            # Next player's turn
            game.current_player = (game.current_player + 1) % len(game.players)
            game.phase = "draw"
            if game.current_player == 0:  # Back to first player
                game.turn += 1
        
        return True
    
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get current game state"""
        return self.games.get(game_id)
    
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
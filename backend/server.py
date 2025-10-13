import asyncio
import json
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Dict, Set
import logging
from game_engine import GameEngine
from models import Card, Faction, GameState, Zone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameServer:
    def __init__(self):
        self.game_engine = GameEngine()
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.client_games: Dict[WebSocketServerProtocol, str] = {}
        self.game_clients: Dict[str, Set[WebSocketServerProtocol]] = {}
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        # Send welcome message
        await self.send_message(websocket, {
            "type": "connected",
            "message": "Connected to Ciudad del Caos server"
        })
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection"""
        self.connected_clients.discard(websocket)
        
        # Remove from game if connected
        if websocket in self.client_games:
            game_id = self.client_games[websocket]
            if game_id in self.game_clients:
                self.game_clients[game_id].discard(websocket)
            del self.client_games[websocket]
        
        logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "create_game":
                await self.handle_create_game(websocket, data)
            elif message_type == "join_game":
                await self.handle_join_game(websocket, data)
            elif message_type == "resume_session":
                await self.handle_resume_session(websocket, data)
            elif message_type == "play_card":
                await self.handle_play_card(websocket, data)
            elif message_type == "attack":
                await self.handle_attack(websocket, data)
            elif message_type == "draw_card":
                await self.handle_draw_card(websocket, data)
            elif message_type == "next_phase":
                await self.handle_next_phase(websocket, data)
            elif message_type == "get_game_state":
                await self.handle_get_game_state(websocket, data)
            else:
                await self.send_error(websocket, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(websocket, f"Server error: {str(e)}")
    
    async def handle_create_game(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle game creation"""
        try:
            player_name = data.get("player_name", "Player 1")
            player_faction = Faction(data.get("player_faction", "police"))
            
            # create_game now returns (game_id, player_id)
            game_id, player_id = self.game_engine.create_game(player_name, player_faction)
            
            # Associate websocket with game
            self.client_games[websocket] = game_id
            if game_id not in self.game_clients:
                self.game_clients[game_id] = set()
            self.game_clients[game_id].add(websocket)
            
            await self.send_message(websocket, {
                "type": "game_created",
                "game_id": game_id,
                "player_id": player_id,
                "message": "Game created successfully. Waiting for second player to join."
            })
            
            # Send initial game state to all clients in game
            await self.broadcast_game_state(game_id)
            
        except Exception as e:
            await self.send_error(websocket, f"Failed to create game: {str(e)}")
    
    async def handle_join_game(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle player joining existing game"""
        game_id = data.get("game_id")
        player_name = data.get("player_name", "Player 2")
        player_faction = Faction(data.get("player_faction", "mafia"))
        
        if not game_id or game_id not in self.game_engine.games:
            await self.send_error(websocket, "Game not found")
            return
        
        # Try to join the game; join_game now returns player_id or None
        player_id = self.game_engine.join_game(game_id, player_name, player_faction)

        if not player_id:
            await self.send_error(websocket, "Unable to join game (game may be full)")
            return
        
        # Associate websocket with game
        self.client_games[websocket] = game_id
        if game_id not in self.game_clients:
            self.game_clients[game_id] = set()
        self.game_clients[game_id].add(websocket)
        
        await self.send_message(websocket, {
            "type": "joined_game",
            "game_id": game_id,
            "player_id": player_id,
            "message": "Joined game successfully"
        })
        
        # Send game state to all clients in game
        await self.broadcast_game_state(game_id)
    
    async def handle_play_card(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle playing a card"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return

        player_id = str(data.get("player_id"))
        card_game_id = str(data.get("card_game_id"))
        zone = None
        if data.get("zone"):
            zone = Zone(data.get("zone"))

        success = self.game_engine.play_card(game_id, player_id, card_game_id, zone)
        
        if success:
            await self.broadcast_game_state(game_id)
            await self.broadcast_to_game(game_id, {
                "type": "card_played",
                "player_id": player_id,
                "card_game_id": card_game_id,
                "zone": zone.value if zone else None
            })
        else:
            await self.send_error(websocket, "Failed to play card")
    
    async def handle_attack(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle attack action"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return

        player_id = str(data.get("player_id"))
        attacker_id = str(data.get("attacker_id"))
        defender_id = str(data.get("defender_id"))
        target_zone = Zone(data.get("target_zone"))

        result = self.game_engine.attack(game_id, player_id, attacker_id, defender_id, target_zone)

        await self.broadcast_to_game(game_id, {
            "type": "attack_result",
            "result": result
        })
        
        if result.get("success"):
            await self.broadcast_game_state(game_id)
    
    async def handle_draw_card(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle drawing a card"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return

        player_id = str(data.get("player_id"))
        card = self.game_engine.draw_card(game_id, player_id)
        
        if card:
            await self.broadcast_game_state(game_id)
        else:
            await self.send_error(websocket, "Failed to draw card")
    
    async def handle_next_phase(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle phase transition"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return
        
        success = self.game_engine.next_phase(game_id)
        
        if success:
            await self.broadcast_game_state(game_id)
        else:
            await self.send_error(websocket, "Failed to advance phase")
    
    async def handle_get_game_state(self, websocket: WebSocketServerProtocol, data: dict):
        """Send current game state"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return
        
        await self.send_game_state(websocket, game_id)

    async def handle_resume_session(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle resuming a previously-saved session (re-associate websocket with game and player)"""
        game_id = data.get("game_id")
        player_id = data.get("player_id")

        if not game_id or not player_id:
            await self.send_error(websocket, "Invalid resume session data")
            return

        game_state = self.game_engine.get_game_state(game_id)
        if not game_state:
            await self.send_error(websocket, "Game not found")
            return

        # Verify player exists in the game
        player_exists = any(p.id == player_id for p in game_state.players)
        if not player_exists:
            await self.send_error(websocket, "Player not found in game")
            return

        # Associate websocket with game
        self.client_games[websocket] = game_id
        if game_id not in self.game_clients:
            self.game_clients[game_id] = set()
        self.game_clients[game_id].add(websocket)

        # Send confirmation and current state
        await self.send_message(websocket, {
            "type": "resumed_session",
            "game_id": game_id,
            "player_id": player_id,
            "message": "Session resumed successfully"
        })

        await self.send_game_state(websocket, game_id)
    
    # Testing utils
    async def add_player_reputation(self, websocket: WebSocketServerProtocol, data: dict):
        """Utility to add reputation to a player (for testing)"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return
        
        player_id = str(data.get("player_id"))
        amount = int(data.get("amount", 0))
        
        success = self.game_engine.add_player_reputation(game_id, player_id, amount)
        
        if success:
            await self.broadcast_game_state(game_id)
            await self.broadcast_to_game(game_id, {
                "type": "reputation_changed",
                "player_id": player_id,
                "amount": amount
            })
        else:
            await self.send_error(websocket, "Failed to change reputation")
    
    async def add_player_coins(self, websocket: WebSocketServerProtocol, data: dict):
        """Utility to add coins to a player (for testing)"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return
        
        player_id = str(data.get("player_id"))
        amount = int(data.get("amount", 0))
        
        success = self.game_engine.add_player_coins(game_id, player_id, amount)
        
        if success:
            await self.broadcast_game_state(game_id)
            await self.broadcast_to_game(game_id, {
                "type": "coins_changed",
                "player_id": player_id,
                "amount": amount
            })
        else:
            await self.send_error(websocket, "Failed to change coins")
    
    async def add_card_defense(self, websocket: WebSocketServerProtocol, data: dict):
        """Utility to add defense to a card (for testing)"""
        game_id = self.client_games.get(websocket)
        if not game_id:
            await self.send_error(websocket, "Not in a game")
            return
        
        player_id = str(data.get("player_id"))
        card_game_id = str(data.get("card_game_id"))
        amount = int(data.get("amount", 0))
        
        success = self.game_engine.add_card_defense(game_id, player_id, card_game_id, amount)
        
        if success:
            await self.broadcast_game_state(game_id)
            await self.broadcast_to_game(game_id, {
                "type": "card_defense_changed",
                "player_id": player_id,
                "card_game_id": card_game_id,
                "amount": amount
            })
        else:
            await self.send_error(websocket, "Failed to change card defense")



    async def broadcast_game_state(self, game_id: str):
        """Broadcast game state to all clients in the game"""
        if game_id in self.game_clients:
            for client in self.game_clients[game_id].copy():
                await self.send_game_state(client, game_id)
    
    async def send_game_state(self, websocket: WebSocketServerProtocol, game_id: str):
        """Send game state to a specific client"""
        game_state = self.game_engine.get_game_state(game_id)
        if game_state:
            # Convert game state to JSON serializable format
            serialized_state = self.serialize_game_state(game_state)
            await self.send_message(websocket, {
                "type": "game_state",
                "game_state": serialized_state
            })

    def serialize_game_state(self, game_state: GameState) -> dict:
        """Convert game state to JSON serializable format"""
        return {
            "game_id": game_state.game_id,
            "current_player": game_state.current_player,
            "turn": game_state.turn,
            "phase": game_state.phase,
            "winner": game_state.winner,
            "players": [
                {
                    "id": player.id,
                    "name": player.name,
                    "reputation": player.reputation,
                    "hand_cards": [self.serialize_card(card) for card in player.hand],
                    "deck_count": len(player.deck),
                    "field": {
                        zone.value: [self.serialize_card(card) for card in cards]
                        for zone, cards in player.field.items()
                    },
                    "coins": player.coins,
                }
                for player in game_state.players
            ],
            # serialize environment card if exists, else None
            "active_environment_card": self.serialize_card(game_state.active_environment_card) if game_state.active_environment_card else None,
            "available_coins": game_state.available_coins
        }
    
    def serialize_card(self, card: Card) -> dict:
        """Convert card to JSON serializable format"""
        return {
            "id": card.id,
            "name": card.name,
            "faction": card.faction.value,
            "type": card.type.value,
            "zone": card.zone.value if card.zone else None,
            "attack": card.attack,
            "defense": card.defense,
            "value": card.value,
            "description": card.description,
            "ability": card.ability,
            "game_id": card.game_id
        }
    
    async def broadcast_to_game(self, game_id: str, message: dict):
        """Broadcast a message to all clients in a game"""
        if game_id in self.game_clients:
            for client in self.game_clients[game_id].copy():
                try:
                    await self.send_message(client, message)
                except websockets.exceptions.ConnectionClosed:
                    self.game_clients[game_id].discard(client)
    
    async def send_message(self, websocket: WebSocketServerProtocol, message: dict):
        """Send a message to a specific client"""
        try:
            if websocket.closed:
                logger.warning("Attempted to send message to closed websocket")
                await self.unregister_client(websocket)
                return
                
            await websocket.send(json.dumps(message))
            logger.debug(f"Sent message type '{message.get('type')}' to client")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed while sending message")
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await self.unregister_client(websocket)
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send an error message to a client"""
        await self.send_message(websocket, {
            "type": "error",
            "message": error_message
        })

# Global server instance
game_server = GameServer()

async def handle_client(websocket: WebSocketServerProtocol, path: str):
    """Handle new client connections"""
    client_ip = websocket.remote_address
    logger.info(f"New client connecting from {client_ip}")
    
    await game_server.register_client(websocket)
    try:
        async for message in websocket:
            if isinstance(message, str):
                await game_server.handle_message(websocket, message)
            else:
                logger.warning(f"Received non-string message: {type(message)}")
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {client_ip} disconnected normally")
    except websockets.exceptions.WebSocketException as e:
        logger.warning(f"WebSocket exception for client {client_ip}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error for client {client_ip}: {e}")
    finally:
        await game_server.unregister_client(websocket)

def main():
    """Start the WebSocket server"""
    logger.info("Starting Ciudad del Caos WebSocket server...")
    
    # Configure server with better settings
    start_server = websockets.serve(
        handle_client, 
        "localhost", 
        8000,
        ping_interval=20,  # Send ping every 20 seconds
        ping_timeout=10,   # Wait 10 seconds for pong
        close_timeout=10,  # Wait 10 seconds when closing
        max_size=2**20,    # 1MB max message size
        max_queue=32       # Max queued messages
    )
    
    logger.info("Server listening on ws://localhost:8000")
    logger.info("Server configuration: ping_interval=20s, ping_timeout=10s")
    
    # The first line starts the WebSocket server and waits until it is fully initialized.
    asyncio.get_event_loop().run_until_complete(start_server)
    # The second line keeps the server running indefinitely, handling incoming connections and messages.
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
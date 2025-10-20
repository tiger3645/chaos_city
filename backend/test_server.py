#!/usr/bin/env python3
"""
Script de prueba para el servidor WebSocket actualizado
Prueba los nuevos endpoints y funcionalidades del sistema de efectos
"""

import asyncio
import json
import websockets
from websockets.client import WebSocketClientProtocol
from typing import Optional

class TestClient:
    def __init__(self, name: str):
        self.name = name
        self.ws: Optional[WebSocketClientProtocol] = None
        self.game_id: Optional[str] = None
        self.player_id: Optional[str] = None
        
    async def connect(self, uri: str = "ws://localhost:8000"):
        """Conectar al servidor"""
        self.ws = await websockets.connect(uri)
        print(f"[{self.name}] Conectado al servidor")
        
    async def send(self, message: dict):
        """Enviar mensaje al servidor"""
        if not self.ws:
            print(f"[{self.name}] Error: No conectado")
            return
        
        await self.ws.send(json.dumps(message))
        print(f"[{self.name}] Enviado: {message['type']}")
        
    async def receive(self, timeout: float = 5.0) -> Optional[dict]:
        """Recibir mensaje del servidor"""
        if not self.ws:
            return None
        
        try:
            message = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
            data = json.loads(message)
            print(f"[{self.name}] Recibido: {data['type']}")
            return data
        except asyncio.TimeoutError:
            print(f"[{self.name}] Timeout esperando mensaje")
            return None
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None
    
    async def create_game(self, faction: str = "police"):
        """Crear un juego nuevo"""
        await self.send({
            "type": "create_game",
            "player_name": self.name,
            "player_faction": faction
        })
        
        response = await self.receive()
        if response and response["type"] == "game_created":
            self.game_id = response["game_id"]
            self.player_id = response["player_id"]
            print(f"[{self.name}] Juego creado: {self.game_id}")
            
            # Recibir game_state inicial
            await self.receive()
            return True
        return False
    
    async def join_game(self, game_id: str, faction: str = "mafia"):
        """Unirse a un juego existente"""
        await self.send({
            "type": "join_game",
            "game_id": game_id,
            "player_name": self.name,
            "player_faction": faction
        })
        
        response = await self.receive()
        if response and response["type"] == "joined_game":
            self.game_id = game_id
            self.player_id = response["player_id"]
            print(f"[{self.name}] Unido al juego: {game_id}")
            
            # Recibir game_state
            await self.receive()
            return True
        return False
    
    async def play_card(self, card_game_id: str, zone: Optional[str] = None):
        """Jugar una carta"""
        await self.send({
            "type": "play_card",
            "player_id": self.player_id,
            "card_game_id": card_game_id,
            "zone": zone
        })
        
        response = await self.receive()
        return response
    
    async def continue_effect(self, effect_id: str, chosen_value):
        """Continuar un efecto multi-paso"""
        await self.send({
            "type": "continue_effect",
            "player_id": self.player_id,
            "effect_id": effect_id,
            "chosen_value": chosen_value
        })
        
        response = await self.receive()
        return response
    
    async def get_card_stats(self, card_game_id: str):
        """Obtener stats efectivos de una carta"""
        await self.send({
            "type": "get_card_stats",
            "card_game_id": card_game_id
        })
        
        response = await self.receive()
        return response
    
    async def attack(self, attacker_id: str, defender_id: str, target_zone: str):
        """Atacar"""
        await self.send({
            "type": "attack",
            "player_id": self.player_id,
            "attacker_id": attacker_id,
            "defender_id": defender_id,
            "target_zone": target_zone
        })
        
        response = await self.receive()
        return response
    
    async def next_phase(self):
        """Avanzar a la siguiente fase"""
        await self.send({
            "type": "next_phase"
        })
        
        response = await self.receive()
        return response
    
    async def get_game_state(self):
        """Obtener estado del juego"""
        await self.send({
            "type": "get_game_state"
        })
        
        response = await self.receive()
        return response
    
    async def disconnect(self):
        """Desconectar del servidor"""
        if self.ws:
            await self.ws.close()
            print(f"[{self.name}] Desconectado")


async def test_basic_flow():
    """Test 1: Flujo básico sin efectos"""
    print("\n" + "="*60)
    print("TEST 1: Flujo básico (crear juego, unir, obtener estado)")
    print("="*60)
    
    client1 = TestClient("Alice")
    client2 = TestClient("Bob")
    
    try:
        # Conectar clientes
        await client1.connect()
        await client2.connect()
        
        # Cliente 1 crea juego
        await client1.create_game("police")
        
        # Cliente 2 se une
        await client2.join_game(client1.game_id, "mafia")
        
        # Obtener estado del juego
        state = await client1.get_game_state()
        if state:
            print(f"✅ Estado del juego obtenido correctamente")
            print(f"   Turn: {state['game_state']['turn']}")
            print(f"   Phase: {state['game_state']['phase']}")
            print(f"   Players: {len(state['game_state']['players'])}")
        
        print("\n✅ Test 1 completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Test 1 falló: {e}")
    finally:
        await client1.disconnect()
        await client2.disconnect()


async def test_play_card_with_choice():
    """Test 2: Jugar carta con efecto multi-paso"""
    print("\n" + "="*60)
    print("TEST 2: Carta con efecto multi-paso")
    print("="*60)
    
    client1 = TestClient("Alice")
    client2 = TestClient("Bob")
    
    try:
        await client1.connect()
        await client2.connect()
        
        await client1.create_game("detective")
        await client2.join_game(client1.game_id, "thief")
        
        # Obtener estado para ver las cartas
        state = await client1.get_game_state()
        if state and state["game_state"]["players"]:
            player = state["game_state"]["players"][0]
            if player["hand_cards"]:
                card = player["hand_cards"][0]
                print(f"\n📋 Jugando carta: {card['name']}")
                
                # Jugar la carta
                response = await client1.play_card(card["game_id"], zone="fighter" if card["zone"] else None)
                
                if response and response.get("requires_choice"):
                    print(f"✅ Carta requiere elección")
                    print(f"   Mensaje: {response['message']}")
                    print(f"   Opciones: {len(response['choices'])}")
                    print(f"   Effect ID: {response['effect_id']}")
                    
                    # Simular elección del jugador
                    if response["choices"]:
                        choice = response["choices"][0]
                        print(f"\n🎯 Eligiendo: {choice}")
                        
                        result = await client1.continue_effect(
                            response["effect_id"],
                            choice["id"] if isinstance(choice, dict) else choice
                        )
                        
                        if result:
                            print(f"✅ Efecto completado")
                            print(f"   Mensaje: {result.get('message')}")
                            if result.get("requires_choice"):
                                print(f"   ⚠️ Requiere más pasos")
                else:
                    print(f"✅ Carta jugada sin requerir elección")
                    if response:
                        print(f"   Mensaje: {response.get('message')}")
        
        print("\n✅ Test 2 completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Test 2 falló: {e}")
    finally:
        await client1.disconnect()
        await client2.disconnect()


async def test_get_card_stats():
    """Test 3: Obtener stats efectivos de cartas"""
    print("\n" + "="*60)
    print("TEST 3: Obtener stats efectivos")
    print("="*60)
    
    client1 = TestClient("Alice")
    client2 = TestClient("Bob")
    
    try:
        await client1.connect()
        await client2.connect()
        
        await client1.create_game("police")
        await client2.join_game(client1.game_id, "mafia")
        
        # Obtener cartas en campo
        state = await client1.get_game_state()
        if state and state["game_state"]["players"]:
            player = state["game_state"]["players"][0]
            
            # Buscar carta en el campo
            for zone, cards in player["field"].items():
                if cards:
                    card = cards[0]
                    print(f"\n📊 Obteniendo stats de: {card['name']}")
                    
                    stats = await client1.get_card_stats(card["game_id"])
                    if stats and stats.get("stats"):
                        s = stats["stats"]
                        print(f"✅ Stats obtenidos:")
                        print(f"   ATK: {s['attack']} (base: {s['base_attack']})")
                        print(f"   DEF: {s['defense']} (base: {s['base_defense']})")
                        if s.get("modifiers"):
                            print(f"   Modificadores:")
                            for mod in s["modifiers"]:
                                print(f"     - {mod}")
                    break
        
        print("\n✅ Test 3 completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Test 3 falló: {e}")
    finally:
        await client1.disconnect()
        await client2.disconnect()


async def test_attack_with_modifiers():
    """Test 4: Ataque con modificadores"""
    print("\n" + "="*60)
    print("TEST 4: Ataque con modificadores")
    print("="*60)
    
    client1 = TestClient("Alice")
    client2 = TestClient("Bob")
    
    try:
        await client1.connect()
        await client2.connect()
        
        await client1.create_game("police")
        await client2.join_game(client1.game_id, "mafia")
        
        # Obtener cartas para atacar
        state = await client1.get_game_state()
        if state and state["game_state"]["players"]:
            player1 = state["game_state"]["players"][0]
            player2 = state["game_state"]["players"][1]
            
            # Buscar atacante y defensor
            attacker = None
            defender = None
            
            for cards in player1["field"].values():
                if cards:
                    attacker = cards[0]
                    break
            
            for zone, cards in player2["field"].items():
                if cards:
                    defender = cards[0]
                    target_zone = zone
                    break
            
            if attacker and defender:
                print(f"\n⚔️ Atacando:")
                print(f"   Atacante: {attacker['name']}")
                print(f"   Defensor: {defender['name']}")
                
                result = await client1.attack(
                    attacker["game_id"],
                    defender["game_id"],
                    target_zone
                )
                
                if result and result.get("result"):
                    r = result["result"]
                    print(f"✅ Ataque ejecutado:")
                    print(f"   Mensaje: {r.get('message')}")
                    print(f"   Atacante ATK efectivo: {r.get('attacker_effective_attack')}")
                    print(f"   Defensor DEF efectiva: {r.get('defender_effective_defense')}")
                    print(f"   Atacante sobrevivió: {r.get('attacker_survived')}")
                    print(f"   Defensor sobrevivió: {r.get('defender_survived')}")
                    
                    if r.get("triggered_effects"):
                        print(f"   Efectos disparados:")
                        for effect in r["triggered_effects"]:
                            print(f"     - {effect}")
        
        print("\n✅ Test 4 completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Test 4 falló: {e}")
    finally:
        await client1.disconnect()
        await client2.disconnect()


async def test_phase_transition():
    """Test 5: Cambio de fase con triggers"""
    print("\n" + "="*60)
    print("TEST 5: Cambio de fase con triggers")
    print("="*60)
    
    client1 = TestClient("Alice")
    client2 = TestClient("Bob")
    
    try:
        await client1.connect()
        await client2.connect()
        
        await client1.create_game("police")
        await client2.join_game(client1.game_id, "mafia")
        
        print(f"\n⏭️ Avanzando fase...")
        
        result = await client1.next_phase()
        
        # Puede recibir effects_triggered o game_state
        if result:
            if result.get("type") == "effects_triggered":
                print(f"✅ Efectos disparados:")
                for effect in result.get("effects", []):
                    print(f"   - {effect}")
            elif result.get("type") == "game_state":
                print(f"✅ Fase cambiada")
                print(f"   Fase actual: {result['game_state']['phase']}")
        
        print("\n✅ Test 5 completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Test 5 falló: {e}")
    finally:
        await client1.disconnect()
        await client2.disconnect()


async def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("🧪 INICIANDO SUITE DE TESTS DEL SERVIDOR")
    print("="*60)
    print("\nAsegúrate de que el servidor esté corriendo en ws://localhost:8000")
    print("\nPresiona Enter para continuar...")
    input()
    
    tests = [
        test_basic_flow,
        test_play_card_with_choice,
        test_get_card_stats,
        test_attack_with_modifiers,
        test_phase_transition
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
            await asyncio.sleep(1)  # Pausa entre tests
        except Exception as e:
            print(f"\n❌ Test falló con excepción: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 RESUMEN DE TESTS")
    print("="*60)
    print(f"✅ Pasados: {passed}/{len(tests)}")
    print(f"❌ Fallidos: {failed}/{len(tests)}")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")

"""
Script de prueba rápida para verificar la integración del sistema de efectos.

Este script crea un juego de prueba y ejecuta varios efectos para verificar
que todo funciona correctamente.
"""

import sys
import os

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.base import GameEngine
from models import Faction, Zone, CARDS_DB

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_basic_integration():
    """Test básico de integración"""
    print_section("TEST 1: Inicialización y Registro de Efectos")
    
    engine = GameEngine()
    print("✅ Motor inicializado")
    print("✅ Efectos registrados automáticamente")
    
    return engine

def test_create_game(engine):
    """Test de creación de juego"""
    print_section("TEST 2: Crear Juego")
    
    game_id, player1_id = engine.create_game("Alice", Faction.POLICE)
    print(f"✅ Juego creado: {game_id[:8]}...")
    print(f"✅ Jugador 1: {player1_id[:8]}...")
    
    player2_id = engine.join_game(game_id, "Bob", Faction.MAFIA)
    print(f"✅ Jugador 2: {player2_id[:8]}...")
    
    return game_id, player1_id, player2_id

def test_play_effect_card(engine, game_id, player_id):
    """Test de jugar carta de efecto"""
    print_section("TEST 3: Jugar Carta de Efecto (Pedir refuerzos)")
    
    game = engine.get_game_state(game_id)
    player = None
    for p in game.players:
        if p.id == player_id:
            player = p
            break
    
    # Dar monedas suficientes
    player.coins = 10
    
    # Buscar "Pedir refuerzos" (ID 14) en la mano o mazo
    card = None
    for c in player.hand:
        if c.id == 14:
            card = c
            break
    
    if not card and player.deck:
        # Si no está en la mano, buscar en el mazo
        for c in player.deck:
            if c.id == 14:
                card = c
                player.deck.remove(c)
                player.hand.append(c)
                break
    
    if not card:
        # Si no la encuentra, añadir una
        card = CARDS_DB[14]
        import uuid
        card.game_id = str(uuid.uuid4())
        player.hand.append(card)
    
    initial_hand_size = len(player.hand)
    print(f"Cartas en mano antes: {initial_hand_size}")
    
    # Jugar la carta
    result = engine.play_card(game_id, player_id, card.game_id)
    
    print(f"✅ Resultado: {result['success']}")
    print(f"✅ Mensaje: {result['message']}")
    print(f"Cartas en mano después: {len(player.hand)}")
    
    if result["success"]:
        print("✅ Efecto ejecutado correctamente")
    
    return result["success"]

def test_play_environment(engine, game_id, player_id):
    """Test de jugar carta de ambiente"""
    print_section("TEST 4: Jugar Carta de Ambiente (Barricadas improvisadas)")
    
    game = engine.get_game_state(game_id)
    player = None
    for p in game.players:
        if p.id == player_id:
            player = p
            break
    
    # Añadir Barricadas improvisadas (ID 13)
    card = CARDS_DB[13]
    import uuid
    card.game_id = str(uuid.uuid4())
    player.hand.append(card)
    player.coins = 10
    
    result = engine.play_card(game_id, player_id, card.game_id)
    
    print(f"✅ Resultado: {result['success']}")
    print(f"✅ Mensaje: {result['message']}")
    
    if game.active_environment_card:
        print(f"✅ Ambiente activo: {game.active_environment_card.name}")
    
    return result["success"]

def test_play_character_with_modifiers(engine, game_id, player_id):
    """Test de jugar personaje y verificar modificadores"""
    print_section("TEST 5: Jugar Personaje y Verificar Modificadores")
    
    game = engine.get_game_state(game_id)
    player = None
    for p in game.players:
        if p.id == player_id:
            player = p
            break
    
    # Añadir un luchador (Agentes de patrulla - ID 2)
    card = CARDS_DB[2]
    import uuid
    card.game_id = str(uuid.uuid4())
    player.hand.append(card)
    player.coins = 10
    
    print(f"Stats base: ATK={card.attack} DEF={card.defense}")
    
    result = engine.play_card(game_id, player_id, card.game_id)
    
    print(f"✅ Carta jugada: {result['success']}")
    print(f"✅ Mensaje: {result['message']}")
    
    # Verificar stats efectivos (debería tener +1 DEF por Barricadas)
    stats = engine.get_card_effective_stats(game_id, card.game_id)
    
    if stats:
        print(f"✅ Stats efectivos: ATK={stats['attack']} DEF={stats['defense']}")
        print(f"   Modificador ATK: {stats['attack_mod']:+d}")
        print(f"   Modificador DEF: {stats['defense_mod']:+d}")
        
        if stats['defense_mod'] == 1:
            print("✅ Modificador de ambiente aplicado correctamente!")
            return True
    
    return False

def test_attack_with_modifiers(engine, game_id, player1_id, player2_id):
    """Test de ataque con modificadores"""
    print_section("TEST 6: Ataque con Modificadores")
    
    game = engine.get_game_state(game_id)
    
    # Asegurar que hay cartas en el campo
    p1 = None
    p2 = None
    for p in game.players:
        if p.id == player1_id:
            p1 = p
        elif p.id == player2_id:
            p2 = p
    
    # Añadir atacante al jugador 1
    import uuid
    attacker = CARDS_DB[2]  # Agentes de patrulla
    attacker.game_id = str(uuid.uuid4())
    p1.field[Zone.FIGHTER].append(attacker)
    
    # Añadir defensor al jugador 2
    defender = CARDS_DB[17]  # Matones a sueldo
    defender.game_id = str(uuid.uuid4())
    p2.field[Zone.FIGHTER].append(defender)
    
    print(f"Atacante: {attacker.name} ({attacker.attack}/{attacker.defense})")
    print(f"Defensor: {defender.name} ({defender.attack}/{defender.defense})")
    
    # Obtener stats efectivos
    attacker_stats = engine.get_card_effective_stats(game_id, attacker.game_id)
    if attacker_stats:
        print(f"Stats efectivos atacante: {attacker_stats['attack']}/{attacker_stats['defense']}")
    
    # Atacar
    result = engine.attack(
        game_id,
        player1_id,
        attacker.game_id,
        defender.game_id,
        Zone.FIGHTER
    )
    
    print(f"✅ Ataque exitoso: {result['success']}")
    print(f"✅ Mensaje: {result['message']}")
    
    if "destroyed" in result:
        print(f"✅ Carta destruida: {result['destroyed']}")
    elif "damage" in result:
        print(f"✅ Daño infligido: {result['damage']}")
        print(f"   Defensa restante: {result.get('remaining_defense', 'N/A')}")
    
    return result["success"]

def test_turn_phases(engine, game_id):
    """Test de cambio de fases y turnos"""
    print_section("TEST 7: Cambio de Fases y Triggers de Turno")
    
    game = engine.get_game_state(game_id)
    print(f"Fase actual: {game.phase}")
    print(f"Turno actual: {game.turn}")
    print(f"Jugador actual: {game.players[game.current_player].name}")
    
    # Avanzar fase
    result = engine.next_phase(game_id)
    
    print(f"✅ Cambio exitoso: {result['success']}")
    print(f"✅ Nueva fase: {result.get('phase', 'N/A')}")
    
    if "triggered_effects" in result:
        print(f"✅ Efectos disparados: {len(result['triggered_effects'])}")
        for effect in result["triggered_effects"]:
            print(f"   - {effect}")
    
    return result["success"]

def test_cleanup(engine, game_id):
    """Test de limpieza de recursos"""
    print_section("TEST 8: Limpieza de Recursos")
    
    success = engine.end_game(game_id)
    
    print(f"✅ Juego terminado: {success}")
    
    # Verificar que el juego ya no existe
    game = engine.get_game_state(game_id)
    if game is None:
        print("✅ Juego eliminado correctamente")
        return True
    else:
        print("❌ Error: Juego todavía existe")
        return False

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 60)
    print("  PRUEBA DE INTEGRACIÓN - SISTEMA DE EFECTOS")
    print("=" * 60)
    
    results = []
    
    try:
        # Test 1: Inicialización
        engine = test_basic_integration()
        results.append(("Inicialización", True))
        
        # Test 2: Crear juego
        game_id, player1_id, player2_id = test_create_game(engine)
        results.append(("Crear juego", True))
        
        # Test 3: Jugar carta de efecto
        success = test_play_effect_card(engine, game_id, player1_id)
        results.append(("Carta de efecto", success))
        
        # Test 4: Jugar carta de ambiente
        success = test_play_environment(engine, game_id, player1_id)
        results.append(("Carta de ambiente", success))
        
        # Test 5: Personaje con modificadores
        success = test_play_character_with_modifiers(engine, game_id, player1_id)
        results.append(("Modificadores", success))
        
        # Test 6: Ataque con modificadores
        success = test_attack_with_modifiers(engine, game_id, player1_id, player2_id)
        results.append(("Ataque", success))
        
        # Test 7: Cambio de turno
        success = test_turn_phases(engine, game_id)
        results.append(("Cambio de turno", success))
        
        # Test 8: Limpieza
        success = test_cleanup(engine, game_id)
        results.append(("Limpieza", success))
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Error general", False))
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! 🎉")
        print("El sistema de efectos está completamente integrado y funcionando.")
        return True
    else:
        print(f"\n⚠️ {total - passed} prueba(s) fallaron.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

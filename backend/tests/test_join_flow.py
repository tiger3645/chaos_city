#!/usr/bin/env python3
"""Simple test: create a game with one client and join with another, print player_ids"""
import asyncio
import json
import websockets

URI = "ws://localhost:8000"

async def run_test():
    async with websockets.connect(URI) as ws1:
        # Receive connected message
        msg = await ws1.recv()
        print("Client1 connected:" , msg)

        # Create game
        await ws1.send(json.dumps({"type": "create_game", "player_name": "Alice", "player_faction": "police"}))
        resp = await ws1.recv()
        print("Create response:", resp)
        data = json.loads(resp)
        game_id = data.get("game_id")
        player1_id = data.get("player_id")
        print("Player 1 id:", player1_id)

        # Connect second client
        async with websockets.connect(URI) as ws2:
            msg2 = await ws2.recv()
            print("Client2 connected:", msg2)

            await ws2.send(json.dumps({"type": "join_game", "game_id": game_id, "player_name": "Bob", "player_faction": "mafia"}))
            resp2 = await ws2.recv()
            print("Join response:", resp2)
            data2 = json.loads(resp2)
            player2_id = data2.get("player_id")
            print("Player 2 id:", player2_id)

            print("IDs equal?", player1_id == player2_id)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_test())

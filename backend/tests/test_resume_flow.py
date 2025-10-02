#!/usr/bin/env python3
"""Test resume session: create game, then resume session with stored player_id"""
import asyncio
import json
import websockets

URI = "ws://localhost:8000"

async def run_test():
    # Client A creates game
    async with websockets.connect(URI) as ws1:
        await ws1.recv()  # connected
        await ws1.send(json.dumps({"type": "create_game", "player_name": "Alice", "player_faction": "police"}))
        resp = await ws1.recv()
        data = json.loads(resp)
        game_id = data.get("game_id")
        player_id = data.get("player_id")
        print("Created game", game_id, "player", player_id)

    # Simulate refresh: new websocket reconnects and resumes session
    async with websockets.connect(URI) as ws2:
        await ws2.recv()  # connected
        await ws2.send(json.dumps({"type": "resume_session", "game_id": game_id, "player_id": player_id}))
        resp = await ws2.recv()
        data = json.loads(resp)
        print("Resume response:", data)
        assert data.get("type") == "resumed_session"
        assert data.get("player_id") == player_id

        # Then expect a game_state message
        resp2 = await ws2.recv()
        data2 = json.loads(resp2)
        print("Follow-up message:", data2.get("type"))
        assert data2.get("type") == "game_state"

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_test())

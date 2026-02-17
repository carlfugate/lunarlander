#!/usr/bin/env python3
"""
Test script for waiting lobby functionality
"""
import asyncio
import websockets
import json

async def test_waiting_lobby():
    print("Testing waiting lobby functionality...")
    
    # Player 1: Create room
    print("Player 1: Creating room...")
    uri1 = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri1) as ws1:
        # Start game (creates room)
        start_msg = {
            "type": "start",
            "difficulty": "simple",
            "player_name": "Player1"
        }
        await ws1.send(json.dumps(start_msg))
        
        # Wait for room_created response
        response = await ws1.recv()
        data = json.loads(response)
        print(f"Player 1 response: {data}")
        
        if data.get("type") == "room_created":
            room_id = data.get("room_id")
            print(f"Room created: {room_id}")
            
            # Check if we get init message (should be waiting state)
            init_response = await ws1.recv()
            init_data = json.loads(init_response)
            print(f"Player 1 init: {init_data.get('type')}")
            
            # Player 2: Join room
            print("Player 2: Joining room...")
            uri2 = "ws://localhost:8000/ws"
            
            async with websockets.connect(uri2) as ws2:
                join_msg = {
                    "type": "join_room",
                    "room_id": room_id,
                    "player_name": "Player2"
                }
                await ws2.send(json.dumps(join_msg))
                
                # Wait for responses
                await asyncio.sleep(1)
                
                # Player 1 starts the game
                print("Player 1: Starting game...")
                start_game_msg = {"type": "start_game"}
                await ws1.send(json.dumps(start_game_msg))
                
                # Listen for game_started messages
                async def listen_for_start(ws, player_name):
                    try:
                        while True:
                            msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                            data = json.loads(msg)
                            if data.get("type") == "game_started":
                                print(f"{player_name}: Received game_started!")
                                return True
                            elif data.get("type") == "telemetry":
                                print(f"{player_name}: Game is running (telemetry received)")
                                return True
                    except asyncio.TimeoutError:
                        return False
                
                # Check if both players receive game_started
                task1 = asyncio.create_task(listen_for_start(ws1, "Player1"))
                task2 = asyncio.create_task(listen_for_start(ws2, "Player2"))
                
                results = await asyncio.gather(task1, task2, return_exceptions=True)
                
                if all(results):
                    print("✓ Waiting lobby test PASSED - Game started successfully!")
                else:
                    print("✗ Waiting lobby test FAILED - Game did not start properly")
                    print(f"Results: {results}")
        else:
            print(f"Unexpected response: {data}")

if __name__ == "__main__":
    asyncio.run(test_waiting_lobby())
#!/usr/bin/env python3
"""
Test script for multiplayer room joining functionality
"""
import asyncio
import websockets
import json

async def test_multiplayer():
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
                
                # Listen for messages from both players
                async def listen_player1():
                    try:
                        while True:
                            msg = await ws1.recv()
                            data = json.loads(msg)
                            print(f"Player 1 received: {data.get('type')}")
                            if data.get("type") == "player_joined":
                                print(f"  New player: {data.get('player_name')} ({data.get('player_color')})")
                    except:
                        pass
                
                async def listen_player2():
                    try:
                        while True:
                            msg = await ws2.recv()
                            data = json.loads(msg)
                            print(f"Player 2 received: {data.get('type')}")
                    except:
                        pass
                
                # Start listening tasks
                task1 = asyncio.create_task(listen_player1())
                task2 = asyncio.create_task(listen_player2())
                
                # Wait a bit to see messages
                await asyncio.sleep(2)
                
                print("Test completed successfully!")
                task1.cancel()
                task2.cancel()
        else:
            print(f"Unexpected response: {data}")

if __name__ == "__main__":
    asyncio.run(test_multiplayer())
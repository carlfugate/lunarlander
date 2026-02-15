#!/usr/bin/env python3
"""
Simple multiplayer test client
Usage: python test_multiplayer_client.py [room_id] [player_name]
"""
import asyncio
import websockets
import json
import sys

async def test_client(room_id=None, player_name="TestPlayer"):
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        if room_id:
            # Join existing room
            print(f"Joining room {room_id} as {player_name}...")
            await websocket.send(json.dumps({
                "type": "join_room",
                "room_id": room_id,
                "player_name": player_name
            }))
        else:
            # Create new room
            print(f"Creating new room as {player_name}...")
            await websocket.send(json.dumps({
                "type": "start",
                "difficulty": "simple",
                "player_name": player_name
            }))
        
        # Listen for messages
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(message)
                
                if data.get("type") == "room_created":
                    print(f"\n✅ Room created! Room ID: {data['room_id']}")
                    print(f"Share this ID with other players to join\n")
                
                elif data.get("type") == "player_joined":
                    print(f"✅ Player joined: {data['player_name']} (color: {data['color']})")
                
                elif data.get("type") == "player_left":
                    print(f"❌ Player left: {data['player_id']}")
                
                elif data.get("type") == "telemetry":
                    # Show player count
                    if "players" in data:
                        player_count = len(data["players"])
                        print(f"📊 {player_count} players in game", end="\r")
                
                elif data.get("type") == "error":
                    print(f"❌ Error: {data['message']}")
                    break
                    
            except asyncio.TimeoutError:
                # Send periodic input to keep game alive
                await websocket.send(json.dumps({
                    "type": "input",
                    "action": "thrust"
                }))
                await asyncio.sleep(0.1)
                await websocket.send(json.dumps({
                    "type": "input",
                    "action": "thrust_off"
                }))

if __name__ == "__main__":
    room_id = sys.argv[1] if len(sys.argv) > 1 else None
    player_name = sys.argv[2] if len(sys.argv) > 2 else f"Player{asyncio.get_event_loop().time():.0f}"
    
    print("🚀 Lunar Lander Multiplayer Test Client")
    print("=" * 50)
    
    try:
        asyncio.run(test_client(room_id, player_name))
    except KeyboardInterrupt:
        print("\n\n👋 Disconnected")

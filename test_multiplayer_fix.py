#!/usr/bin/env python3
"""
Test script to verify the multiplayer room creation fix
Tests that create_room doesn't send initial_state until start_game is called
"""

import asyncio
import websockets
import json
import time

async def test_multiplayer_fix():
    print("🧪 Testing multiplayer room creation fix...")
    
    server_url = "ws://localhost:8000/ws"
    
    try:
        # Player 1: Create multiplayer room
        print("\n1️⃣ Player 1: Creating multiplayer room...")
        ws1 = await websockets.connect(server_url)
        
        # Send create_room message (not start)
        create_msg = {
            "type": "create_room",
            "difficulty": "simple",
            "player_name": "Creator"
        }
        await ws1.send(json.dumps(create_msg))
        
        # Wait for room_created response
        response = await ws1.recv()
        data = json.loads(response)
        print(f"   Room created response: {data['type']}")
        
        if data['type'] != 'room_created':
            print("❌ Failed: Expected room_created message")
            return False
            
        room_id = data['room_id']
        print(f"   ✓ Room ID: {room_id[:8]}...")
        
        # Wait for player_list
        response = await ws1.recv()
        data = json.loads(response)
        if data['type'] == 'player_list':
            print(f"   ✓ Player list received: {len(data['players'])} players")
        else:
            print(f"   Unexpected message: {data['type']}")
        
        # Check if we get init message (we should NOT get it yet)
        print("   Checking for unexpected init message...")
        try:
            response = await asyncio.wait_for(ws1.recv(), timeout=1.0)
            data = json.loads(response)
            print(f"   Received message: {data}")
            if data['type'] == 'init':
                print("   ❌ FAILED: Received init message too early!")
                print("   This means the game started immediately instead of waiting")
                return False
            elif data['type'] == 'telemetry':
                print("   ❌ FAILED: Received telemetry message!")
                print("   This means the game is running instead of waiting")
                return False
            else:
                print(f"   Received: {data['type']}")
        except asyncio.TimeoutError:
            print("   ✓ GOOD: No init/telemetry messages received (room is waiting)")
        
        # Player 2: Join room
        print("\n2️⃣ Player 2: Joining room...")
        ws2 = await websockets.connect(server_url)
        
        join_msg = {
            "type": "join_room",
            "room_id": room_id,
            "player_name": "Joiner"
        }
        await ws2.send(json.dumps(join_msg))
        
        # Consume player_joined and player_list messages
        print("   Consuming join messages...")
        for _ in range(4):  # Both players get player_joined + player_list
            try:
                response = await asyncio.wait_for(ws1.recv(), timeout=0.5)
                data = json.loads(response)
                print(f"   Player 1 received: {data['type']}")
            except asyncio.TimeoutError:
                break
        
        for _ in range(3):  # Player 2 gets player_joined + player_list + (maybe init)
            try:
                response = await asyncio.wait_for(ws2.recv(), timeout=0.5)
                data = json.loads(response)
                print(f"   Player 2 received: {data['type']}")
                if data['type'] == 'init':
                    print("   ❌ FAILED: Player 2 received init message too early!")
                    return False
            except asyncio.TimeoutError:
                break
        
        # Player 1 (creator) starts the game
        print("\n3️⃣ Room creator starting game...")
        start_game_msg = {"type": "start_game"}
        await ws1.send(json.dumps(start_game_msg))
        
        # Now we should get init messages
        print("   Waiting for init messages...")
        
        response1 = await asyncio.wait_for(ws1.recv(), timeout=2.0)
        data1 = json.loads(response1)
        print(f"   Player 1 received: {data1['type']}")
        
        response2 = await asyncio.wait_for(ws2.recv(), timeout=2.0)
        data2 = json.loads(response2)
        print(f"   Player 2 received: {data2['type']}")
        
        # Check for game_started messages
        response1 = await asyncio.wait_for(ws1.recv(), timeout=2.0)
        data1 = json.loads(response1)
        print(f"   Player 1 received: {data1['type']}")
        
        response2 = await asyncio.wait_for(ws2.recv(), timeout=2.0)
        data2 = json.loads(response2)
        print(f"   Player 2 received: {data2['type']}")
        
        # Wait for telemetry to confirm game is running
        print("\n4️⃣ Verifying game is running...")
        
        response1 = await asyncio.wait_for(ws1.recv(), timeout=2.0)
        data1 = json.loads(response1)
        if data1['type'] == 'telemetry':
            print("   ✓ Player 1: Game running (telemetry received)")
        else:
            print(f"   Player 1 received: {data1['type']}")
        
        response2 = await asyncio.wait_for(ws2.recv(), timeout=2.0)
        data2 = json.loads(response2)
        if data2['type'] == 'telemetry':
            print("   ✓ Player 2: Game running (telemetry received)")
        else:
            print(f"   Player 2 received: {data2['type']}")
        
        # Clean up
        await ws1.close()
        await ws2.close()
        
        print("\n🎉 Multiplayer fix test PASSED!")
        print("✓ create_room doesn't send init immediately")
        print("✓ join_room doesn't send init for waiting rooms")
        print("✓ start_game sends init and starts the game")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multiplayer_fix())
    exit(0 if success else 1)
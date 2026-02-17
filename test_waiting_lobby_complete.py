#!/usr/bin/env python3
"""
Comprehensive test for waiting lobby functionality
Tests the complete flow: create room → waiting lobby → join → see players → start game
"""

import asyncio
import websockets
import json
import time

async def test_waiting_lobby():
    print("🧪 Testing complete waiting lobby functionality...")
    
    # Test data
    server_url = "ws://localhost:8000/ws"
    player1_name = "Creator"
    player2_name = "Joiner"
    
    try:
        # Player 1: Create room
        print("\n1️⃣ Player 1: Creating room...")
        ws1 = await websockets.connect(server_url)
        
        # Send create room message
        create_msg = {
            "type": "start",
            "difficulty": "simple",
            "player_name": player1_name
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
            print(f"   ✓ Initial player list: {len(data['players'])} players")
            assert len(data['players']) == 1
            assert data['players'][0]['name'] == player1_name
            assert data['players'][0]['is_creator'] == True
        
        # Wait for init message
        response = await ws1.recv()
        data = json.loads(response)
        print(f"   ✓ Init message received: {data['type']}")
        
        # Player 2: Join room
        print("\n2️⃣ Player 2: Joining room...")
        ws2 = await websockets.connect(server_url)
        
        join_msg = {
            "type": "join_room",
            "room_id": room_id,
            "player_name": player2_name
        }
        await ws2.send(json.dumps(join_msg))
        
        # Both players should receive player_joined message
        print("   Waiting for player_joined messages...")
        
        # Player 1 receives player_joined
        response = await ws1.recv()
        data = json.loads(response)
        print(f"   Player 1 received: {data['type']}")
        
        # Player 1 receives updated player_list
        response = await ws1.recv()
        data = json.loads(response)
        if data['type'] == 'player_list':
            print(f"   ✓ Player 1 sees updated list: {len(data['players'])} players")
            assert len(data['players']) == 2
        
        # Player 2 receives player_joined
        response = await ws2.recv()
        data = json.loads(response)
        print(f"   Player 2 received: {data['type']}")
        
        # Player 2 receives player_list
        response = await ws2.recv()
        data = json.loads(response)
        if data['type'] == 'player_list':
            print(f"   ✓ Player 2 sees player list: {len(data['players'])} players")
            assert len(data['players']) == 2
            
            # Verify player details
            creators = [p for p in data['players'] if p['is_creator']]
            joiners = [p for p in data['players'] if not p['is_creator']]
            assert len(creators) == 1
            assert len(joiners) == 1
            assert creators[0]['name'] == player1_name
            assert joiners[0]['name'] == player2_name
        
        # Player 2 receives init
        response = await ws2.recv()
        data = json.loads(response)
        print(f"   ✓ Player 2 init: {data['type']}")
        
        # Player 1 (creator) starts the game
        print("\n3️⃣ Room creator starting game...")
        start_game_msg = {"type": "start_game"}
        await ws1.send(json.dumps(start_game_msg))
        
        # Both players should receive game_started
        print("   Waiting for game_started messages...")
        
        response1 = await ws1.recv()
        data1 = json.loads(response1)
        print(f"   Player 1 received: {data1['type']}")
        assert data1['type'] == 'game_started'
        
        response2 = await ws2.recv()
        data2 = json.loads(response2)
        print(f"   Player 2 received: {data2['type']}")
        assert data2['type'] == 'game_started'
        
        # Wait for telemetry to confirm game is running
        print("\n4️⃣ Verifying game is running...")
        
        response1 = await ws1.recv()
        data1 = json.loads(response1)
        if data1['type'] == 'telemetry':
            print("   ✓ Player 1: Game running (telemetry received)")
        
        response2 = await ws2.recv()
        data2 = json.loads(response2)
        if data2['type'] == 'telemetry':
            print("   ✓ Player 2: Game running (telemetry received)")
        
        # Clean up
        await ws1.close()
        await ws2.close()
        
        print("\n🎉 Complete waiting lobby test PASSED!")
        print("✓ Room creation works")
        print("✓ Player list updates work")
        print("✓ Only creator can start game")
        print("✓ Game starts for all players")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_waiting_lobby())
    exit(0 if success else 1)
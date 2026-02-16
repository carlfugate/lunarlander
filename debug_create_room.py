#!/usr/bin/env python3
"""
Simple debug test for create_room
"""

import asyncio
import websockets
import json

async def debug_create_room():
    print("🔍 Debugging create_room flow...")
    
    try:
        ws = await websockets.connect("ws://localhost:8000/ws")
        
        # Send create_room message
        create_msg = {
            "type": "create_room",
            "difficulty": "simple",
            "player_name": "TestPlayer"
        }
        print(f"Sending: {create_msg}")
        await ws.send(json.dumps(create_msg))
        
        # Receive all messages for 3 seconds
        print("Receiving messages...")
        for i in range(10):
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=0.5)
                data = json.loads(response)
                print(f"Message {i+1}: {data['type']}")
                if data['type'] == 'init':
                    print("  ⚠️  INIT MESSAGE RECEIVED!")
                    print(f"  Terrain points: {len(data['terrain']['points'])}")
                    print(f"  Lander position: ({data['lander']['x']}, {data['lander']['y']})")
            except asyncio.TimeoutError:
                print(f"Timeout after message {i}")
                break
        
        await ws.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_create_room())
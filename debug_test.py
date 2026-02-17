#!/usr/bin/env python3
"""
Debug test to see what messages are being sent
"""

import asyncio
import websockets
import json

async def debug_test():
    print("🔍 Debug test - checking message flow...")
    
    server_url = "ws://localhost:8000/ws"
    
    try:
        # Create room
        print("\n1. Creating room...")
        ws1 = await websockets.connect(server_url)
        
        create_msg = {
            "type": "start",
            "difficulty": "simple",
            "player_name": "Creator"
        }
        await ws1.send(json.dumps(create_msg))
        
        # Collect all messages for 2 seconds
        messages = []
        try:
            while True:
                response = await asyncio.wait_for(ws1.recv(), timeout=2.0)
                data = json.loads(response)
                messages.append(data)
                print(f"   Received: {data['type']}")
                if data['type'] == 'room_created':
                    room_id = data['room_id']
        except asyncio.TimeoutError:
            pass
        
        print(f"\n   Total messages received: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"   {i+1}. {msg['type']}")
        
        # Send start_game
        print("\n2. Sending start_game...")
        start_msg = {"type": "start_game"}
        await ws1.send(json.dumps(start_msg))
        
        # Wait for response
        try:
            response = await asyncio.wait_for(ws1.recv(), timeout=2.0)
            data = json.loads(response)
            print(f"   Response: {data['type']}")
        except asyncio.TimeoutError:
            print("   No response received")
        
        await ws1.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_test())
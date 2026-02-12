import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket")
            
            # Start game
            await websocket.send(json.dumps({
                "type": "start",
                "difficulty": "simple"
            }))
            print("✓ Sent start message")
            
            # Receive initial state
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            init_data = json.loads(response)
            print(f"✓ Received init: {init_data['type']}")
            print(f"  Terrain points: {len(init_data['terrain']['points'])}")
            print(f"  Landing zones: {len(init_data['terrain']['landing_zones'])}")
            
            # Receive a few telemetry updates
            for i in range(5):
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(response)
                if data['type'] == 'telemetry':
                    lander = data['lander']
                    print(f"✓ Telemetry {i+1}: y={lander['y']:.1f}, vy={lander['vy']:.2f}, fuel={lander['fuel']:.0f}")
                await asyncio.sleep(0.1)
            
            # Test thrust input
            await websocket.send(json.dumps({
                "type": "input",
                "action": "thrust"
            }))
            print("✓ Sent thrust command")
            
            # Receive more updates
            for i in range(3):
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(response)
                if data['type'] == 'telemetry':
                    lander = data['lander']
                    print(f"✓ With thrust: y={lander['y']:.1f}, vy={lander['vy']:.2f}, fuel={lander['fuel']:.0f}")
                await asyncio.sleep(0.1)
            
            print("\n✅ WebSocket test passed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())

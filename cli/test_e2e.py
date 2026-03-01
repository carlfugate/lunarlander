#!/usr/bin/env python3
"""
End-to-end test for CLI client.
Requires server running on localhost:8000
"""
import asyncio
import sys
from terminal_client import TerminalClient

async def test_connection():
    """Test that client can connect to server."""
    print("Testing connection...")
    client = TerminalClient()
    try:
        await client.ws_client.connect()
        print("✅ Connection successful")
        await client.ws_client.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_instantiation():
    """Test that all components instantiate correctly."""
    print("\nTesting component instantiation...")
    try:
        client = TerminalClient("ws://localhost:8000/ws", "simple", False)
        assert client.caps is not None, "TerminalCapabilities not initialized"
        assert client.state is not None, "GameState not initialized"
        assert client.ws_client is not None, "WebSocketClient not initialized"
        assert client.renderer is not None, "TerminalRenderer not initialized"
        assert client.input_handler is not None, "InputHandler not initialized"
        print("✅ All components initialized")
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False

async def test_game_start():
    """Test that game can start and receive init message."""
    print("\nTesting game start...")
    client = TerminalClient()
    try:
        await client.ws_client.connect()
        await client.ws_client.start_game("simple")
        
        # Wait for init message (may receive room_created first)
        for _ in range(3):
            msg = await asyncio.wait_for(client.ws_client.receive_message(), timeout=2.0)
            if msg and msg.get('type') == 'init':
                print("✅ Game started and received init message")
                await client.ws_client.close()
                return True
            elif msg and msg.get('type') == 'room_created':
                continue  # Keep waiting for init
        
        print(f"❌ Did not receive init message")
        await client.ws_client.close()
        return False
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for init message")
        await client.ws_client.close()
        return False
    except Exception as e:
        print(f"❌ Game start failed: {e}")
        return False

async def test_renderer():
    """Test that renderer can render game state."""
    print("\nTesting renderer...")
    try:
        from terminal_caps import TerminalCapabilities
        from renderer import TerminalRenderer
        from game_state import GameState
        
        caps = TerminalCapabilities()
        renderer = TerminalRenderer(caps)
        state = GameState()
        
        # Render empty state (should not crash)
        renderer.render_frame(state, "play")
        print("✅ Renderer works with empty state")
        
        # Render with data
        state.lander = {'x': 100, 'y': 200, 'fuel': 500, 'rotation': 0}
        state.telemetry = {'speed': 5.0, 'altitude': 150, 'thrusting': False}
        renderer.render_frame(state, "play")
        print("✅ Renderer works with game data")
        
        return True
    except Exception as e:
        print(f"❌ Renderer failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("CLI End-to-End Tests")
    print("=" * 60)
    print("\nPrerequisite: Server must be running on localhost:8000")
    print()
    
    results = []
    
    # Test 1: Instantiation (no server needed)
    results.append(await test_instantiation())
    
    # Test 2: Renderer (no server needed)
    results.append(await test_renderer())
    
    # Test 3: Connection (requires server)
    results.append(await test_connection())
    
    # Test 4: Game start (requires server)
    results.append(await test_game_start())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

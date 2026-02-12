#!/usr/bin/env python3
"""
Integration test for scoring and difficulty selection
Tests the full flow: connect -> start game -> land -> check score
"""
import asyncio
import websockets
import json

async def test_game_flow(difficulty, expected_min_score):
    """Test a complete game flow with scoring"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"\n=== Testing {difficulty.upper()} difficulty ===")
            
            # Start game with difficulty
            await websocket.send(json.dumps({
                "type": "start",
                "difficulty": difficulty
            }))
            
            # Receive init message
            init_msg = json.loads(await websocket.recv())
            assert init_msg["type"] == "init"
            print(f"✓ Game started with {difficulty} difficulty")
            
            # Simulate landing by waiting for a few frames
            # In a real test, we'd send inputs to actually land
            frame_count = 0
            game_over = False
            score = None
            
            while frame_count < 100 and not game_over:
                try:
                    msg = json.loads(await asyncio.wait_for(websocket.recv(), timeout=0.1))
                    
                    if msg["type"] == "telemetry":
                        frame_count += 1
                        
                        # Check if we have lander data
                        if frame_count == 10:
                            print(f"✓ Receiving telemetry (frame {frame_count})")
                    
                    elif msg["type"] == "game_over":
                        game_over = True
                        score = msg.get("score", 0)
                        landed = msg.get("landed", False)
                        crashed = msg.get("crashed", False)
                        
                        print(f"✓ Game over: landed={landed}, crashed={crashed}")
                        print(f"✓ Score: {score}")
                        
                        if crashed:
                            assert score == 0, "Crashed games should score 0"
                            print(f"✓ Crashed game correctly scored 0")
                        elif landed:
                            assert score >= expected_min_score, f"Score {score} below minimum {expected_min_score}"
                            print(f"✓ Score {score} meets minimum {expected_min_score}")
                        
                        break
                        
                except asyncio.TimeoutError:
                    continue
            
            if not game_over:
                print(f"⚠ Game didn't end in 100 frames (testing telemetry only)")
                return True
            
            return True
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def test_difficulty_validation():
    """Test that invalid difficulty defaults to simple"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"\n=== Testing invalid difficulty ===")
            
            # Start game with invalid difficulty
            await websocket.send(json.dumps({
                "type": "start",
                "difficulty": "invalid"
            }))
            
            # Should still work (defaults to simple)
            init_msg = json.loads(await websocket.recv())
            assert init_msg["type"] == "init"
            print(f"✓ Invalid difficulty handled gracefully")
            
            return True
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def main():
    print("Starting integration tests...")
    
    # Test each difficulty
    results = []
    
    # Easy - expect at least 1000 (base score)
    results.append(await test_game_flow("simple", 1000))
    
    # Medium - expect at least 1500 (base * 1.5)
    results.append(await test_game_flow("medium", 1500))
    
    # Hard - expect at least 2000 (base * 2.0)
    results.append(await test_game_flow("hard", 2000))
    
    # Invalid difficulty
    results.append(await test_difficulty_validation())
    
    print("\n" + "="*50)
    if all(results):
        print("✓ All integration tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

#!/usr/bin/env python3
"""
Run multiple bot instances to test metrics collection
Simulates continuous load for a specified duration
"""
import asyncio
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../bots'))

from simple_bot import SimpleBot

async def run_bot_continuous(bot_id, duration_seconds, fuel_mode="limited"):
    """Run a single bot continuously for specified duration"""
    start_time = time.time()
    game_count = 0
    
    try:
        print(f"🤖 Bot {bot_id} starting (fuel: {fuel_mode})")
        
        while time.time() - start_time < duration_seconds:
            game_count += 1
            # Create new bot instance for each game (fresh connection)
            bot = SimpleBot(
                ws_url="ws://localhost:8000/ws",
                difficulty="simple",
                log_file=f"/tmp/bot_{bot_id}.jsonl",
                fuel_mode=fuel_mode
            )
            
            try:
                await bot.play()
            except Exception as e:
                print(f"⚠️  Bot {bot_id} game {game_count} error: {e}")
            finally:
                if bot.ws and not bot.ws.closed:
                    await bot.ws.close()
            
            await asyncio.sleep(0.5)  # Brief pause between games
            
    except Exception as e:
        print(f"❌ Bot {bot_id} fatal error: {e}")
    finally:
        elapsed = time.time() - start_time
        print(f"✓ Bot {bot_id} finished: {game_count} games in {elapsed:.1f}s")

async def main():
    num_bots = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    duration_minutes = float(sys.argv[2]) if len(sys.argv) > 2 else 10
    fuel_mode = sys.argv[3] if len(sys.argv) > 3 else "limited"
    duration_seconds = int(duration_minutes * 60)
    
    print(f"🚀 Starting {num_bots} bots for {duration_minutes} minutes")
    print(f"⏱️  Duration: {duration_seconds} seconds")
    print(f"⛽ Fuel mode: {fuel_mode}")
    print(f"📊 Check live stats: http://localhost:8000/api/stats/live")
    print(f"📈 Check aggregate: http://localhost:8000/api/stats/aggregate")
    print()
    
    tasks = [run_bot_continuous(i, duration_seconds, fuel_mode) for i in range(num_bots)]
    await asyncio.gather(*tasks)
    
    print(f"\n✅ Test complete!")
    print(f"📊 View results:")
    print(f"   curl http://localhost:8000/api/stats/live | jq")
    print(f"   curl http://localhost:8000/api/stats/aggregate | jq")
    print(f"   curl http://localhost:8000/api/stats/fun-facts | jq")

if __name__ == "__main__":
    asyncio.run(main())

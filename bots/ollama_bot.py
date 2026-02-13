#!/usr/bin/env python3
"""
LLM-powered bot for Lunar Lander using Ollama
Recommended models: qwen2.5:7b, llama3.2:3b, phi3:mini
"""
import asyncio
import websockets
import json
import sys
import requests

class OllamaBot:
    def __init__(self, ws_url="ws://localhost:8000/ws", difficulty="simple", 
                 model="qwen2.5:7b", update_rate=5):
        self.ws_url = ws_url
        self.difficulty = difficulty
        self.model = model
        self.update_rate = update_rate
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ws = None
        self.game_context = []
        
    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print(f"✓ Connected to server")
        
    async def start_game(self):
        await self.ws.send(json.dumps({
            "type": "start",
            "difficulty": self.difficulty,
            "telemetry_mode": "advanced",
            "update_rate": self.update_rate
        }))
        print(f"✓ Started game (difficulty: {self.difficulty}, model: {self.model}, rate: {self.update_rate}Hz)")
        
    def create_prompt(self, telemetry):
        """Create a concise prompt for the LLM"""
        lander = telemetry["lander"]
        
        prompt = f"""You are piloting a lunar lander. Analyze the situation and decide actions.

CURRENT STATE:
- Position: x={lander['x']:.0f}, y={lander['y']:.0f}
- Altitude: {telemetry['altitude']:.1f}m above ground
- Speed: {telemetry['speed']:.1f} m/s (SAFE: <5.0)
- Vertical speed: {telemetry.get('vertical_speed', 0):.1f} m/s (down is positive)
- Horizontal speed: {telemetry.get('horizontal_speed', 0):.1f} m/s
- Angle: {telemetry.get('angle_degrees', 0):.1f}° (SAFE: <17°)
- Fuel: {lander['fuel']:.0f}/1000 ({telemetry.get('fuel_remaining_percent', 0)*100:.0f}%)
- Over landing zone: {telemetry.get('is_over_landing_zone', False)}
- Landing zone center: x={telemetry.get('landing_zone_center_x', 0):.0f}
- Safe to land: speed={telemetry.get('is_safe_speed', False)}, angle={telemetry.get('is_safe_angle', False)}

SCORING:
- Estimated score if landed now: {telemetry.get('estimated_score', 0)}
- Max possible: {telemetry.get('max_possible_score', 0)}

CONTROLS:
- thrust_on / thrust_off: Fire thruster (pushes up, uses fuel)
- rotate_left / rotate_right / rotate_stop: Rotate craft

RESPOND WITH ONLY A JSON ARRAY OF ACTIONS, NO EXPLANATION:
Example: ["thrust_on", "rotate_stop"]
"""
        return prompt
    
    def query_ollama(self, prompt):
        """Query Ollama for decision"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower = more deterministic
                        "num_predict": 50    # Short response
                    }
                },
                timeout=2.0  # 2 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["response"].strip()
                
                # Extract JSON array from response
                import re
                match = re.search(r'\[.*?\]', text)
                if match:
                    actions = json.loads(match.group())
                    return actions
                else:
                    print(f"⚠ Could not parse: {text[:100]}")
                    return ["thrust_off", "rotate_stop"]
            else:
                print(f"✗ Ollama error: {response.status_code}")
                return ["thrust_off", "rotate_stop"]
                
        except requests.exceptions.Timeout:
            print("⚠ Ollama timeout")
            return ["thrust_off", "rotate_stop"]
        except Exception as e:
            print(f"✗ Ollama error: {e}")
            return ["thrust_off", "rotate_stop"]
    
    async def play(self):
        await self.connect()
        await self.start_game()
        
        frame_count = 0
        
        try:
            async for message in self.ws:
                data = json.loads(message)
                
                if data["type"] == "init":
                    print(f"✓ Game initialized")
                    print(f"✓ Landing zone at x={data['terrain']['landing_zones'][0]['x1']}-{data['terrain']['landing_zones'][0]['x2']}")
                    
                elif data["type"] == "telemetry":
                    frame_count += 1
                    
                    if data["lander"]["crashed"] or data["lander"]["landed"]:
                        continue
                    
                    # Create prompt and query LLM
                    prompt = self.create_prompt(data)
                    print(f"\n[Frame {frame_count}] Alt: {data['altitude']:.0f}m, Speed: {data['speed']:.1f}, Fuel: {data['lander']['fuel']:.0f}")
                    
                    actions = self.query_ollama(prompt)
                    print(f"→ Actions: {actions}")
                    
                    # Send actions
                    for action in actions:
                        await self.ws.send(json.dumps({
                            "type": "input",
                            "action": action
                        }))
                    
                elif data["type"] == "game_over":
                    score = data.get("score", 0)
                    landed = data.get("landed", False)
                    elapsed = data.get("elapsed_time", 0)
                    if landed:
                        print(f"\n✓ LANDED! Score: {score}, Time: {elapsed:.1f}s")
                    else:
                        print(f"\n✗ CRASHED! Score: {score}")
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        finally:
            await self.ws.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LLM-powered Lunar Lander bot")
    parser.add_argument("--difficulty", default="simple", choices=["simple", "medium", "hard"])
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama model name")
    parser.add_argument("--rate", type=int, default=5, help="Update rate in Hz (2-10)")
    args = parser.parse_args()
    
    bot = OllamaBot(
        difficulty=args.difficulty,
        model=args.model,
        update_rate=args.rate
    )
    asyncio.run(bot.play())

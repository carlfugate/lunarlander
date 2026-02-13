#!/usr/bin/env python3
"""
LLM-powered bot for Lunar Lander using Ollama
Recommended models: gemma3:4b (fast), llava:latest (good), qwen2.5:7b (excellent)
"""
import asyncio
import websockets
import json
import sys
import requests

class OllamaBot:
    def __init__(self, ws_url="ws://localhost:8000/ws", difficulty="simple", 
                 model="gemma3:4b", update_rate=10):
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
        zone = telemetry.get("nearest_landing_zone")
        
        if not zone:
            return "No landing zone found. Return: [\"thrust_off\", \"rotate_stop\"]"
        
        x_error = zone['center_x'] - lander['x']
        
        prompt = f"""Lunar lander pilot. Decide thrust and rotation.

STATE:
Alt: {telemetry['altitude']:.0f}m | Speed: {telemetry['speed']:.1f} m/s (SAFE<5.0)
Vx: {telemetry.get('horizontal_speed', 0):.1f} | Vy: {telemetry.get('vertical_speed', 0):.1f} (down=+)
Angle: {telemetry.get('angle_degrees', 0):.1f}° (SAFE<17°) | Fuel: {lander['fuel']:.0f}
X-error: {x_error:.0f}m (to landing zone center)
Over zone: {telemetry.get('is_over_landing_zone', False)}

STRATEGY:
1. If low (<100m) & off-target (>20m): tilt toward zone, hover
2. If fast horizontal (>3 m/s) & low (<200m): tilt opposite to brake
3. If high (>300m): let fall, thrust if Vy>7
4. If medium (150-300m): thrust if Vy>5
5. If low (<150m): thrust if Speed>4 or Vy>2.5

CONTROLS: ["thrust_on"/"thrust_off", "rotate_left"/"rotate_right"/"rotate_stop"]
RESPOND JSON ONLY:
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
    parser.add_argument("--model", default="gemma3:4b", help="Ollama model name")
    parser.add_argument("--rate", type=int, default=10, help="Update rate in Hz (2-10)")
    args = parser.parse_args()
    
    bot = OllamaBot(
        difficulty=args.difficulty,
        model=args.model,
        update_rate=args.rate
    )
    asyncio.run(bot.play())

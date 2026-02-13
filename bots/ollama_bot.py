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
import subprocess

def get_installed_models():
    """Get list of installed Ollama models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        return [line.split()[0] for line in lines if line.strip()]
    except:
        return []

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
            return "No zone. Reply: [\"thrust_off\", \"rotate_stop\"]"
        
        x_error = zone['center_x'] - lander['x']
        alt = telemetry['altitude']
        speed = telemetry['speed']
        vx = telemetry.get('horizontal_speed', 0)
        vy = telemetry.get('vertical_speed', 0)
        angle = telemetry.get('angle_degrees', 0)
        
        prompt = f"""Lander: Alt={alt:.0f}m Speed={speed:.1f} Vx={vx:.1f} Vy={vy:.1f} Angle={angle:.0f}° Fuel={lander['fuel']:.0f} XErr={x_error:.0f}m

Safe: Speed<5, Angle<17°
Strategy: High(>300m)→fall. Med(150-300)→thrust if Vy>5. Low(<150)→thrust if Speed>4. OffTarget→tilt.

Reply JSON array only: ["thrust_on"/"thrust_off", "rotate_left"/"rotate_right"/"rotate_stop"]
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
                        "temperature": 0.2,
                        "num_predict": 30
                    }
                },
                timeout=3.0  # 2 second timeout
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
    
    installed = get_installed_models()
    if not installed:
        print("Error: No Ollama models found. Run 'ollama pull <model>' first.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="LLM-powered Lunar Lander bot")
    parser.add_argument("--difficulty", default="simple", choices=["simple", "medium", "hard"])
    parser.add_argument("--model", choices=installed, help=f"Ollama model ({', '.join(installed[:3])}...)")
    parser.add_argument("--rate", type=int, default=10, help="Update rate in Hz (2-10)")
    parser.add_argument("--list", action="store_true", help="List installed models")
    args = parser.parse_args()
    
    if args.list:
        print("Installed Ollama models:")
        for model in installed:
            print(f"  - {model}")
        sys.exit(0)
    
    # Auto-select best model if not specified
    if not args.model:
        preferred = ['phi3:mini', 'gemma3:4b', 'llama3.2:3b', 'qwen2.5:7b']
        args.model = next((m for m in preferred if m in installed), installed[0])
        print(f"Auto-selected model: {args.model}")
    
    bot = OllamaBot(
        difficulty=args.difficulty,
        model=args.model,
        update_rate=args.rate
    )
    asyncio.run(bot.play())

#!/usr/bin/env python3
"""
Simple rule-based bot for Lunar Lander
Uses basic physics and heuristics to land safely
"""
import asyncio
import websockets
import json
import sys

class SimpleBot:
    def __init__(self, ws_url="ws://localhost:8000/ws", difficulty="simple"):
        self.ws_url = ws_url
        self.difficulty = difficulty
        self.ws = None
        
    async def connect(self):
        self.ws = await websockets.connect(self.ws_url)
        print("✓ Connected to server")
        
    async def start_game(self):
        await self.ws.send(json.dumps({
            "type": "start",
            "difficulty": self.difficulty,
            "telemetry_mode": "advanced",
            "update_rate": 60
        }))
        print(f"✓ Started game (difficulty: {self.difficulty}, mode: bot)")
        
    def decide_action(self, telemetry):
        """Rule-based decision making inspired by examples/simple_ai.py"""
        lander = telemetry["lander"]
        altitude = telemetry["altitude"]
        speed = telemetry["speed"]
        vertical_speed = telemetry.get("vertical_speed", lander["vy"])
        horizontal_speed = telemetry.get("horizontal_speed", lander["vx"])
        zone = telemetry.get("nearest_landing_zone")
        
        if not zone:
            return ["thrust_off", "rotate_stop"]
        
        x_error = zone['center_x'] - lander['x']
        
        # Rotation control
        target_angle = 0
        
        # Priority 1: Emergency navigation if low and off-target
        if abs(x_error) > 20 and altitude < 100:
            target_angle = max(-0.4, min(0.4, x_error * 0.005))
        # Priority 2: Brake horizontal velocity
        elif abs(horizontal_speed) > 2.0 and altitude < 200:
            target_angle = -horizontal_speed * 0.15
            target_angle = max(-0.5, min(0.5, target_angle))
        # Priority 3: Navigate when high
        elif abs(x_error) > 50 and altitude > 200:
            target_angle = max(-0.3, min(0.3, x_error * 0.001))
        
        angle_error = target_angle - lander['rotation']
        
        if angle_error > 0.1:
            rotate_action = "rotate_right"
        elif angle_error < -0.1:
            rotate_action = "rotate_left"
        else:
            rotate_action = "rotate_stop"
        
        # Thrust control
        thrust_action = "thrust_off"
        
        # Priority 1: Emergency hover if low and off-target
        if abs(x_error) > 20 and altitude < 50:
            if vertical_speed > 0.5:  # Descending
                thrust_action = "thrust_on"
        # Priority 2: Brake horizontal velocity at low altitude
        elif altitude < 200 and abs(horizontal_speed) > 3.0:
            thrust_action = "thrust_on"
        # Priority 3: Altitude-based control
        elif altitude < 150:
            if speed > 4.0 or vertical_speed > 2.5:
                thrust_action = "thrust_on"
        elif altitude < 300:
            if vertical_speed > 5.0:
                thrust_action = "thrust_on"
        else:
            if vertical_speed > 7.0:
                thrust_action = "thrust_on"
        
        return [thrust_action, rotate_action]
    
    async def play(self):
        await self.connect()
        await self.start_game()
        
        try:
            async for message in self.ws:
                data = json.loads(message)
                
                if data["type"] == "init":
                    print(f"✓ Game initialized")
                    
                elif data["type"] == "telemetry":
                    if data["lander"]["crashed"] or data["lander"]["landed"]:
                        continue
                    
                    actions = self.decide_action(data)
                    for action in actions:
                        await self.ws.send(json.dumps({
                            "type": "input",
                            "action": action
                        }))
                    
                elif data["type"] == "game_over":
                    score = data.get("score", 0)
                    landed = data.get("landed", False)
                    if landed:
                        print(f"✓ LANDED! Score: {score}")
                    else:
                        print(f"✗ CRASHED! Score: {score}")
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        finally:
            await self.ws.close()

if __name__ == "__main__":
    difficulty = sys.argv[1] if len(sys.argv) > 1 else "simple"
    bot = SimpleBot(difficulty=difficulty)
    asyncio.run(bot.play())

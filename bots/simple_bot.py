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
        """Simple rule-based decision making"""
        lander = telemetry["lander"]
        altitude = telemetry["altitude"]
        speed = telemetry["speed"]
        vertical_speed = telemetry.get("vertical_speed", lander["vy"])
        horizontal_speed = telemetry.get("horizontal_speed", lander["vx"])
        angle_degrees = telemetry.get("angle_degrees", abs(lander["rotation"]) * 57.3)
        is_over_landing_zone = telemetry.get("is_over_landing_zone", False)
        landing_zone_center_x = telemetry.get("landing_zone_center_x")
        
        actions = []
        
        # 1. Correct angle first (stay upright)
        if angle_degrees > 5:
            if lander["rotation"] > 0:
                actions.append("rotate_left")
            else:
                actions.append("rotate_right")
        else:
            actions.append("rotate_stop")
        
        # 2. Navigate to landing zone
        if landing_zone_center_x and not is_over_landing_zone:
            distance = lander["x"] - landing_zone_center_x
            if abs(distance) > 10:
                if distance > 0:
                    actions.append("rotate_left")
                else:
                    actions.append("rotate_right")
        
        # 3. Control descent
        target_vertical_speed = min(4.0, altitude / 20)  # Slower as we get closer
        
        if vertical_speed > target_vertical_speed:
            actions.append("thrust_on")
        else:
            actions.append("thrust_off")
        
        return actions
    
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

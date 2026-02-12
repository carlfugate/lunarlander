import asyncio
import time
import json
from game.physics import Lander
from game.terrain import Terrain
from game.replay import ReplayRecorder

class GameSession:
    def __init__(self, session_id, websocket, difficulty="simple"):
        self.session_id = session_id
        self.websocket = websocket
        self.difficulty = difficulty
        self.lander = Lander()
        self.terrain = Terrain(difficulty=difficulty)
        self.running = False
        self.start_time = None
        self.input_count = 0
        self.last_update = time.time()
        self.current_thrust = False
        self.current_rotate = None
        self.user_id = "anonymous"
        self.replay = None
        self.record_replay = True  # Enable replay recording
        self.spectators = []  # List of spectator websockets
        
    async def start(self):
        self.running = True
        self.start_time = time.time()
        
        # Initialize replay recorder
        if self.record_replay:
            self.replay = ReplayRecorder(self.session_id, self.user_id, self.difficulty)
            
        await self.game_loop()
        
    async def game_loop(self):
        target_fps = 60
        dt = 1.0 / target_fps
        
        while self.running:
            loop_start = time.time()
            
            # Update physics with current input state
            self.lander.update(dt, self.current_thrust, self.current_rotate)
            
            # Record frame for replay
            if self.replay:
                terrain_height = self.terrain.get_height_at(self.lander.x)
                self.replay.record_frame(self.lander.to_dict(), terrain_height)
            
            # Check collision
            terrain_y = self.terrain.get_height_at(self.lander.x)
            is_landing, multiplier = self.terrain.is_landing_zone(self.lander.x)
            
            # Debug: print terrain info every 2 seconds
            current_time = time.time()
            if int(current_time * 0.5) % 2 == 0 and int((current_time - 0.016) * 0.5) % 2 != 0:
                speed = (self.lander.vx**2 + self.lander.vy**2)**0.5
                print(f"[{current_time:.3f}] Alt: {800-self.lander.y:.0f}, Speed: {speed:.1f}, X: {self.lander.x:.0f}, Landing: {is_landing}")
            
            self.lander.check_collision(terrain_y, is_landing)
            
            # Check bounds
            if self.lander.x < 0 or self.lander.x > self.terrain.width:
                self.lander.crashed = True
            
            # Check game over
            if self.lander.crashed or self.lander.landed:
                await self.send_game_over()
                self.running = False
                break
                
            # Send telemetry
            await self.send_telemetry()
            
            # Sleep to maintain 60Hz
            elapsed = time.time() - loop_start
            sleep_time = max(0, dt - elapsed)
            await asyncio.sleep(sleep_time)
            
    async def send_telemetry(self):
        # Find nearest landing zone
        nearest_zone = None
        min_distance = float('inf')
        
        for zone in self.terrain.landing_zones:
            zone_center_x = (zone['x1'] + zone['x2']) / 2
            distance = abs(self.lander.x - zone_center_x)
            if distance < min_distance:
                min_distance = distance
                nearest_zone = {
                    'x1': zone['x1'],
                    'x2': zone['x2'],
                    'center_x': zone_center_x,
                    'y': zone['y'],
                    'width': zone['x2'] - zone['x1'],
                    'distance': distance,
                    'direction': 'left' if zone_center_x < self.lander.x else 'right'
                }
        
        # Calculate actual altitude above terrain
        terrain_height = self.terrain.get_height_at(self.lander.x)
        altitude_above_terrain = terrain_height - self.lander.y
        
        # Calculate total speed
        import math
        speed = math.sqrt(self.lander.vx**2 + self.lander.vy**2)
        
        message = {
            "type": "telemetry",
            "timestamp": time.time(),
            "lander": self.lander.to_dict(),
            "terrain_height": terrain_height,
            "altitude": altitude_above_terrain,
            "speed": speed,
            "nearest_landing_zone": nearest_zone,
            "all_landing_zones": self.terrain.landing_zones
        }
        
        # Send to player
        await self.websocket.send_text(json.dumps(message))
        
        # Send to all spectators
        for spectator_ws in self.spectators[:]:  # Copy list to avoid modification during iteration
            try:
                await spectator_ws.send_text(json.dumps(message))
            except:
                self.spectators.remove(spectator_ws)
        
    async def send_game_over(self):
        elapsed_time = time.time() - self.start_time
        
        # Finalize replay
        if self.replay:
            self.replay.finalize(
                self.lander.landed,
                self.lander.crashed,
                elapsed_time,
                self.lander.fuel,
                self.input_count
            )
            replay_id = f"{self.session_id}_{int(time.time())}"
        else:
            replay_id = None
        
        message = {
            "type": "game_over",
            "landed": self.lander.landed,
            "crashed": self.lander.crashed,
            "time": elapsed_time,
            "fuel_remaining": self.lander.fuel,
            "inputs": self.input_count,
            "replay_id": replay_id
        }
        
        # Send to player
        await self.websocket.send_text(json.dumps(message))
        
        # Send to all spectators
        for spectator_ws in self.spectators[:]:
            try:
                await spectator_ws.send_text(json.dumps(message))
            except:
                pass
        
    async def send_initial_state(self):
        message = {
            "type": "init",
            "terrain": self.terrain.to_dict(),
            "lander": self.lander.to_dict(),
            "constants": {
                "gravity": 1.62,
                "thrust_power": 5.0,
                "rotation_speed": 3.0,
                "fuel_consumption_rate": 10.0,
                "max_landing_speed": 5.0,
                "max_landing_angle": 0.3,  # radians (~17 degrees)
                "terrain_width": 1200,
                "terrain_height": 800
            }
        }
        
        # Send to player
        await self.websocket.send_text(json.dumps(message))
        
        # Send to all spectators
        for spectator_ws in self.spectators[:]:
            try:
                await spectator_ws.send_text(json.dumps(message))
            except:
                self.spectators.remove(spectator_ws)
        
    def handle_input(self, action):
        self.input_count += 1
        # Only log state changes, not every input
        if action == "thrust":
            if not self.current_thrust:
                print(f"[{time.time():.3f}] THRUST ON")
            self.current_thrust = True
        elif action == "thrust_off":
            if self.current_thrust:
                print(f"[{time.time():.3f}] THRUST OFF")
            self.current_thrust = False
        elif action == "rotate_left":
            if self.current_rotate != "left":
                print(f"[{time.time():.3f}] ROTATE LEFT")
            self.current_rotate = "left"
        elif action == "rotate_right":
            if self.current_rotate != "right":
                print(f"[{time.time():.3f}] ROTATE RIGHT")
            self.current_rotate = "right"
        elif action == "rotate_stop":
            if self.current_rotate is not None:
                print(f"[{time.time():.3f}] ROTATE STOP")
            self.current_rotate = None

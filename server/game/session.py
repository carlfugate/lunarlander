import asyncio
import time
import json
from game.physics import Lander
from game.terrain import Terrain
from game.replay import ReplayRecorder

class GameSession:
    def __init__(self, session_id, websocket, difficulty="simple", telemetry_mode="standard", update_rate=60):
        print(f"DEBUG - GameSession.__init__() called for {session_id}")
        self.session_id = session_id
        self.websocket = websocket
        self.difficulty = difficulty
        self.telemetry_mode = telemetry_mode  # "standard" or "advanced"
        self.update_rate = update_rate  # Hz: 60 for humans/bots, 2-10 for LLMs
        
        # Multiplayer support - players dictionary
        self.players = {}
        
        # Backward compatibility - create default player
        default_player_id = "default"
        self.players[default_player_id] = {
            'lander': Lander(),
            'thrust': False,
            'rotate': None,
            'websocket': websocket,
            'name': 'Player',
            'color': '#00ff00'
        }
        
        # Keep reference for backward compatibility
        self.lander = self.players[default_player_id]['lander']
        self.current_thrust = False
        self.current_rotate = None
        
        self.terrain = Terrain(difficulty=difficulty)
        self.running = False
        self.waiting = True  # New: waiting for game to start
        print(f"DEBUG - GameSession.__init__() completed for {session_id}, waiting={self.waiting}")
        self.start_time = None
        self.input_count = 0
        self.last_update = time.time()
        self.user_id = "anonymous"
        self.replay = None
        self.record_replay = True  # Enable replay recording
        self.spectators = []  # List of spectator websockets
        
        # Bot metadata (optional, for future leaderboard/registration)
        self.bot_name = None
        self.bot_version = None
        self.bot_author = None
        
    async def start(self):
        self.running = True
        # Don't set waiting = False here - let start_game() do it
        self.start_time = time.time()
        
        # Initialize replay recorder
        if self.record_replay:
            self.replay = ReplayRecorder(self.session_id, self.user_id, self.difficulty)
            self.replay.set_terrain(self.terrain.to_dict())
            
        await self.game_loop()
    
    def start_game(self):
        """Start the game (called by room creator)"""
        print(f"DEBUG - start_game() called for session {self.session_id}, changing waiting from {self.waiting} to False")
        self.waiting = False
        
    async def game_loop(self):
        print(f"DEBUG - game_loop started for session {self.session_id}, waiting={self.waiting}")
        
        # Wait for game to start
        while self.waiting and self.running:
            print(f"DEBUG - game_loop waiting for start, session {self.session_id}")
            await asyncio.sleep(0.1)
        
        if not self.running:
            print(f"DEBUG - game_loop exiting, session not running {self.session_id}")
            return
        
        print(f"DEBUG - game_loop starting physics simulation for session {self.session_id}")
        
        # Game has started - reset start time for accurate timing
        self.start_time = time.time()
            
        target_fps = 60
        dt = 1.0 / target_fps
        frame_count = 0
        
        while self.running:
            loop_start = time.time()
            
            # Skip physics simulation while waiting
            if self.waiting:
                await asyncio.sleep(0.1)
                continue
            
            # Update physics for all players
            for player_id, player in self.players.items():
                lander = player['lander']
                lander.update(dt, player['thrust'], player['rotate'])
                
                # Check collision
                terrain_y = self.terrain.get_height_at(lander.x)
                is_landing, multiplier = self.terrain.is_landing_zone(lander.x)
                lander.check_collision(terrain_y, is_landing)
                
                # Check bounds
                if lander.x < 0 or lander.x > self.terrain.width:
                    lander.crashed = True
            
            # Update backward compatibility references (use first player)
            if self.players:
                first_player = next(iter(self.players.values()))
                self.lander = first_player['lander']
                self.current_thrust = first_player['thrust']
                self.current_rotate = first_player['rotate']
            
            # Calculate altitude and speed for replay (backward compatibility)
            terrain_height = self.terrain.get_height_at(self.lander.x)
            altitude = terrain_height - self.lander.y
            import math
            speed = math.sqrt(self.lander.vx**2 + self.lander.vy**2)
            
            # Record frame for replay
            if self.replay:
                self.replay.record_frame(self.lander.to_dict(), terrain_height, altitude, speed, self.current_thrust)
            
            # Debug: print terrain info every 2 seconds
            current_time = time.time()
            if int(current_time * 0.5) % 2 == 0 and int((current_time - 0.016) * 0.5) % 2 != 0:
                speed = (self.lander.vx**2 + self.lander.vy**2)**0.5
                print(f"[{current_time:.3f}] Alt: {800-self.lander.y:.0f}, Speed: {speed:.1f}, X: {self.lander.x:.0f}, Landing: {self.terrain.is_landing_zone(self.lander.x)[0]}")
            
            # Check game over (any player crashed/landed ends game for now)
            game_over = any(player['lander'].crashed or player['lander'].landed for player in self.players.values())
            
            if game_over:
                # Send final telemetry with crashed/landed state
                await self.send_telemetry(send_to_spectators=True)
                await self.send_game_over()
                self.running = False
                break
                
            # Send telemetry at configured rate
            # Calculate how often to send based on update_rate
            frames_per_update = int(60 / self.update_rate)
            send_to_player = (frame_count % frames_per_update == 0)
            send_to_spectators = (frame_count % 2 == 0)
            
            if send_to_player:
                await self.send_telemetry(send_to_spectators)
            frame_count += 1
            
            # Sleep to maintain 60Hz
            elapsed = time.time() - loop_start
            sleep_time = max(0, dt - elapsed)
            await asyncio.sleep(sleep_time)
            
    async def send_telemetry(self, send_to_spectators=True):
        # Find nearest landing zone (using first player for backward compatibility)
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
        
        # Collect all players' states
        players_data = {}
        for player_id, player in self.players.items():
            lander = player['lander']
            players_data[player_id] = {
                'lander': lander.to_dict(),
                'name': player['name'],
                'color': player['color'],
                'thrusting': player['thrust']
            }
        
        # Standard telemetry (always included)
        message = {
            "type": "telemetry",
            "timestamp": time.time(),
            "terrain_height": terrain_height,
            "altitude": altitude_above_terrain,
            "speed": speed,
            "thrusting": self.current_thrust,
            "nearest_landing_zone": nearest_zone,
            "all_landing_zones": self.terrain.landing_zones,
            "spectator_count": len(self.spectators)
        }
        
        # Single-player vs multiplayer format
        if len(self.players) == 1 and 'default' in self.players:
            # Send single-player format (backward compatible)
            message['lander'] = self.players['default']['lander'].to_dict()
        else:
            # Send multiplayer format
            message['players'] = players_data
        
        # Advanced telemetry (only for AI clients)
        if self.telemetry_mode == "advanced":
            elapsed_time = time.time() - self.start_time
            angle_degrees = abs(self.lander.rotation) * 180 / math.pi
            is_safe_speed = speed < 5.0
            is_safe_angle = angle_degrees < 17.0
            
            # Check if over landing zone
            is_over_landing_zone = False
            landing_zone_center_x = None
            if nearest_zone:
                zone = nearest_zone
                is_over_landing_zone = zone['x1'] <= self.lander.x <= zone['x2']
                landing_zone_center_x = zone['center_x']
            
            # Estimate score if landed now
            estimated_score = 0
            if is_safe_speed and is_safe_angle and is_over_landing_zone:
                estimated_score = self.calculate_score(elapsed_time)
            
            # Predict time to ground (simple physics, no thrust)
            time_to_ground = None
            impact_speed = None
            if self.lander.vy > 0 and altitude_above_terrain > 0:
                a = 1.62  # lunar gravity
                v = self.lander.vy
                d = altitude_above_terrain
                discriminant = v*v + 2*a*d
                if discriminant >= 0:
                    time_to_ground = (-v + math.sqrt(discriminant)) / a
                    impact_speed = v + a * time_to_ground
            
            # Add advanced fields
            message.update({
                "is_over_landing_zone": is_over_landing_zone,
                "landing_zone_center_x": landing_zone_center_x,
                "is_safe_speed": is_safe_speed,
                "is_safe_angle": is_safe_angle,
                "angle_degrees": angle_degrees,
                "vertical_speed": self.lander.vy,
                "horizontal_speed": self.lander.vx,
                "elapsed_time": elapsed_time,
                "fuel_remaining_percent": self.lander.fuel / 1000.0,
                "estimated_score": estimated_score,
                "max_possible_score": int(1800 * (2.0 if self.difficulty == "hard" else 1.5 if self.difficulty == "medium" else 1.0)),
                "time_to_ground": time_to_ground,
                "impact_speed": impact_speed
            })
        
        # Send to all players
        for player_id, player in list(self.players.items()):
            try:
                await player['websocket'].send_text(json.dumps(message))
            except:
                # Remove player if websocket is closed
                self.remove_player(player_id)
        
        # Send to spectators (30Hz when send_to_spectators=True)
        if send_to_spectators:
            for spectator_ws in self.spectators[:]:  # Copy list to avoid modification during iteration
                try:
                    await spectator_ws.send_text(json.dumps(message))
                except:
                    self.spectators.remove(spectator_ws)
        
    async def send_game_over(self):
        elapsed_time = time.time() - self.start_time
        
        # Calculate score
        score = self.calculate_score(elapsed_time)
        
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
            "score": score,
            "replay_id": replay_id
        }
        
        # Send to all players
        for player_id, player in list(self.players.items()):
            try:
                await player['websocket'].send_text(json.dumps(message))
            except:
                # Remove player if websocket is closed
                self.remove_player(player_id)
        
        # Send to all spectators
        for spectator_ws in self.spectators[:]:
            try:
                await spectator_ws.send_text(json.dumps(message))
            except:
                pass
    
    def calculate_score(self, elapsed_time):
        """Calculate score based on landing success, fuel, time, and difficulty"""
        if self.lander.crashed:
            return 0
        
        if not self.lander.landed:
            return 0
        
        # Base score for successful landing
        score = 1000
        
        # Fuel bonus (up to 500 points)
        fuel_bonus = int((self.lander.fuel / 1000) * 500)
        score += fuel_bonus
        
        # Time bonus (faster = better, up to 300 points)
        # Assume 60s is slow, 20s is fast
        time_bonus = max(0, int(300 - (elapsed_time - 20) * 5))
        score += time_bonus
        
        # Difficulty multiplier
        multipliers = {"simple": 1.0, "medium": 1.5, "hard": 2.0}
        multiplier = multipliers.get(self.difficulty, 1.0)
        score = int(score * multiplier)
        
        return score
        
    async def send_initial_state(self):
        import traceback
        print(f"DEBUG - send_initial_state() called for session {self.session_id}, waiting={self.waiting}")
        print("DEBUG - Call stack:")
        for line in traceback.format_stack()[-3:-1]:
            print(f"  {line.strip()}")
        
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
        
        # Send to all players
        for player_id, player in list(self.players.items()):
            try:
                await player['websocket'].send_text(json.dumps(message))
            except:
                # Remove player if websocket is closed
                self.remove_player(player_id)
        
        # Send to all spectators
        for spectator_ws in self.spectators[:]:
            try:
                await spectator_ws.send_text(json.dumps(message))
            except:
                self.spectators.remove(spectator_ws)
    
    async def send_player_list(self):
        """Send current player list to all players"""
        players_list = []
        for player_id, player in self.players.items():
            players_list.append({
                "id": player_id,
                "name": player['name'],
                "color": player['color'],
                "is_creator": player_id == "default"
            })
        
        message = {
            "type": "player_list",
            "players": players_list
        }
        
        # Send to all players
        for player_id, player in list(self.players.items()):
            try:
                await player['websocket'].send_text(json.dumps(message))
            except:
                # Remove player if websocket is closed
                self.remove_player(player_id)
        
    def handle_input(self, action, player_id="default"):
        self.input_count += 1
        
        # Get player or use default
        if player_id not in self.players:
            player_id = "default"
        
        player = self.players[player_id]
        
        # Only log state changes, not every input
        if action == "thrust" or action == "thrust_on":
            if not player['thrust']:
                print(f"[{time.time():.3f}] THRUST ON (Player: {player_id})")
            player['thrust'] = True
        elif action == "thrust_off":
            if player['thrust']:
                print(f"[{time.time():.3f}] THRUST OFF (Player: {player_id})")
            player['thrust'] = False
        elif action == "rotate_left":
            if player['rotate'] != "left":
                print(f"[{time.time():.3f}] ROTATE LEFT (Player: {player_id})")
            player['rotate'] = "left"
        elif action == "rotate_right":
            if player['rotate'] != "right":
                print(f"[{time.time():.3f}] ROTATE RIGHT (Player: {player_id})")
            player['rotate'] = "right"
        elif action == "rotate_stop":
            if player['rotate'] is not None:
                print(f"[{time.time():.3f}] ROTATE STOP (Player: {player_id})")
            player['rotate'] = None
        
        # Update backward compatibility references if this is the default player
        if player_id == "default":
            self.current_thrust = player['thrust']
            self.current_rotate = player['rotate']
    
    def add_player(self, player_id, websocket, name, color):
        """Add a new player to the game session"""
        self.players[player_id] = {
            'lander': Lander(),
            'thrust': False,
            'rotate': None,
            'websocket': websocket,
            'name': name,
            'color': color
        }
        print(f"[{time.time():.3f}] Player {player_id} ({name}) joined")
    
    def remove_player(self, player_id):
        """Remove a player from the game session"""
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            del self.players[player_id]
            print(f"[{time.time():.3f}] Player {player_id} ({player_name}) left")
            
            # Send updated player list to remaining players
            if self.players:
                import asyncio
                asyncio.create_task(self.send_player_list())
            
            # If removing default player and others exist, promote first remaining player
            if player_id == "default" and self.players:
                first_player_id = next(iter(self.players.keys()))
                first_player = self.players[first_player_id]
                self.lander = first_player['lander']
                self.current_thrust = first_player['thrust']
                self.current_rotate = first_player['rotate']
                self.websocket = first_player['websocket']

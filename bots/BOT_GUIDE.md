# Building Your Own Lunar Lander Bot

Complete guide for creating AI bots to play Lunar Lander.

## Quick Start Template

```python
#!/usr/bin/env python3
import asyncio
import websockets
import json

class MyBot:
    def __init__(self):
        self.ws = None
        self.terrain_width = 1200  # Updated from init message
        
    async def connect(self):
        self.ws = await websockets.connect("ws://localhost:8000/ws")
        
    async def start_game(self):
        await self.ws.send(json.dumps({
            "type": "start",
            "difficulty": "simple",  # "simple", "medium", "hard"
            "telemetry_mode": "advanced",  # "standard" or "advanced"
            "update_rate": 60,  # Hz: 2-60 (use 60 for bots, 2-10 for LLMs)
            # Bot identification (optional, for future leaderboard/registration)
            "bot_name": "MyBot",
            "bot_version": "1.0.0",
            "bot_author": "Your Name"
        }))
        
    async def play(self):
        await self.connect()
        await self.start_game()
        
        async for message in self.ws:
            data = json.loads(message)
            
            if data["type"] == "init":
                # Extract game constants
                constants = data["constants"]
                self.terrain_width = constants["terrain_width"]  # 1200
                terrain_height = constants["terrain_height"]  # 800
                gravity = constants["gravity"]  # 1.62 m/s²
                thrust_power = constants["thrust_power"]  # 5.0 m/s²
                max_landing_speed = constants["max_landing_speed"]  # 5.0 m/s
                max_landing_angle = constants["max_landing_angle"]  # 0.3 rad (~17°)
                
            elif data["type"] == "telemetry":
                if data["lander"]["crashed"] or data["lander"]["landed"]:
                    continue
                    
                # Make decision
                actions = self.decide(data)
                
                # Send actions
                for action in actions:
                    await self.ws.send(json.dumps({
                        "type": "input",
                        "action": action
                    }))
                    
            elif data["type"] == "game_over":
                print(f"Score: {data['score']}")
                break
                
    def decide(self, telemetry):
        """Your bot logic here"""
        # Return list of actions
        return ["thrust_on", "rotate_stop"]

if __name__ == "__main__":
    bot = MyBot()
    asyncio.run(bot.play())
```

## Game Constants (Init Message)

Received once at game start:

```python
{
    "type": "init",
    "constants": {
        "gravity": 1.62,              # m/s² (lunar gravity)
        "thrust_power": 5.0,          # m/s² (acceleration when thrusting)
        "rotation_speed": 3.0,        # rad/s (rotation rate)
        "fuel_consumption_rate": 10.0, # units/s (fuel usage)
        "max_landing_speed": 5.0,     # m/s (safe landing speed)
        "max_landing_angle": 0.3,     # radians (~17°, safe landing angle)
        "terrain_width": 1200,        # pixels (game world width)
        "terrain_height": 800         # pixels (game world height)
    },
    "terrain": { ... },
    "lander": { ... }
}
```

## Standard Telemetry (60 Hz)

Basic telemetry for human players:

```python
{
    "type": "telemetry",
    "lander": {
        "x": 600.0,           # pixels (horizontal position)
        "y": 100.0,           # pixels (vertical position, 0=top)
        "vx": 2.5,            # m/s (horizontal velocity, right=+)
        "vy": 3.2,            # m/s (vertical velocity, down=+)
        "rotation": 0.1,      # radians (tilt, right=+)
        "fuel": 850,          # units remaining
        "crashed": false,
        "landed": false
    },
    "altitude": 450.0,        # meters above terrain
    "speed": 4.1,             # m/s (total velocity magnitude)
    "terrain_height": 550.0,  # pixels (terrain height at lander x)
    "thrusting": true,
    "nearest_landing_zone": {
        "x1": 500, "x2": 600,
        "center_x": 550,
        "y": 600,
        "width": 100,
        "distance": 50,       # pixels to center
        "direction": "left"   # or "right"
    }
}
```

## Advanced Telemetry (2-60 Hz)

Extended telemetry for AI bots (request with `telemetry_mode: "advanced"`):

```python
{
    # ... all standard fields, plus:
    
    # Safety checks
    "is_safe_speed": true,           # speed < 5.0 m/s
    "is_safe_angle": true,           # angle < 17°
    "angle_degrees": 5.7,            # absolute angle in degrees
    
    # Velocity components
    "vertical_speed": 3.2,           # m/s (down=+)
    "horizontal_speed": 2.5,         # m/s (right=+)
    
    # Landing zone targeting
    "is_over_landing_zone": false,  # currently over safe zone
    "landing_zone_center_x": 550,   # x-coordinate of zone center
    
    # Score prediction
    "estimated_score": 0,            # score if landed now (0 if unsafe)
    "max_possible_score": 1800,     # max score for this difficulty
    
    # Trajectory prediction (no thrust)
    "time_to_ground": 2.5,          # seconds until impact
    "impact_speed": 8.3,            # m/s at impact (if no thrust)
    
    # Game state
    "elapsed_time": 15.2,           # seconds since start
    "fuel_remaining_percent": 0.85  # 0.0 to 1.0
}
```

## Available Actions

Send actions as input messages:

```python
# Thrust control
{"type": "input", "action": "thrust_on"}
{"type": "input", "action": "thrust_off"}

# Rotation control
{"type": "input", "action": "rotate_left"}
{"type": "input", "action": "rotate_right"}
{"type": "input", "action": "rotate_stop"}
```

## Bot Identification (Optional)

Include bot metadata in the start message for future leaderboard/registration:

```python
{
    "type": "start",
    "difficulty": "simple",
    "telemetry_mode": "advanced",
    "update_rate": 60,
    # Optional bot identification
    "bot_name": "MyBot",           # Bot name (for leaderboard display)
    "bot_version": "1.0.0",        # Version string
    "bot_author": "Your Name"      # Author/team name
}
```

**Future Features:**
- Bot leaderboard with rankings
- Bot registration system
- Performance tracking across runs
- Tournament mode

**Current Status:** Metadata is accepted and stored but not yet used. Include it now to be ready for future features!

## Bot Strategy Tips

### 1. Wall Avoidance (Critical!)

```python
WALL_MARGIN = 50
if lander['x'] < WALL_MARGIN and horizontal_speed < 0:
    return ["thrust_on", "rotate_right"]
if lander['x'] > terrain_width - WALL_MARGIN and horizontal_speed > 0:
    return ["thrust_on", "rotate_left"]
```

### 2. Landing Zone Targeting

```python
x_error = landing_zone_center_x - lander['x']
if abs(x_error) > 20 and altitude < 100:
    # Navigate toward zone
    target_angle = max(-0.4, min(0.4, x_error * 0.005))
```

### 3. Horizontal Velocity Braking

```python
if abs(horizontal_speed) > 2.0 and altitude < 200:
    # Tilt opposite to velocity to brake
    target_angle = -horizontal_speed * 0.15
    target_angle = max(-0.5, min(0.5, target_angle))
```

### 4. Altitude-Based Thrust Control

```python
if altitude < 150:
    if speed > 4.0 or vertical_speed > 2.5:
        thrust_on = True
elif altitude < 300:
    if vertical_speed > 5.0:
        thrust_on = True
else:  # High altitude
    if vertical_speed > 7.0:
        thrust_on = True
```

### 5. Rotation Control

```python
angle_error = target_angle - lander['rotation']
if angle_error > 0.1:
    rotate_action = "rotate_right"
elif angle_error < -0.1:
    rotate_action = "rotate_left"
else:
    rotate_action = "rotate_stop"
```

## Coordinate System

```
(0, 0) ────────────────────────────── (1200, 0)
  │                                        │
  │         Lander (x, y)                  │
  │              ▼                         │
  │         Velocity (vx, vy)              │
  │              ↓                         │
  │                                        │
  │    Landing Zone                        │
  │    [x1────────x2]                      │
  │         ▲                              │
(0, 800) ──┴──────────────────────── (1200, 800)
        Terrain
```

- **X-axis**: 0 (left) to 1200 (right)
- **Y-axis**: 0 (top) to 800 (bottom)
- **Velocity**: vx (right=+), vy (down=+)
- **Rotation**: radians (right=+, left=-)
- **Altitude**: Calculated as `terrain_height - lander_y`

## Logging & Debugging

See `simple_bot.py` for logging implementation:

```python
def log_frame(self, telemetry, actions, reason=""):
    log_entry = {
        "frame": self.frame_count,
        "altitude": telemetry["altitude"],
        "speed": telemetry["speed"],
        "vx": telemetry.get("horizontal_speed", 0),
        "vy": telemetry.get("vertical_speed", 0),
        "angle": telemetry.get("angle_degrees", 0),
        "fuel": telemetry["lander"]["fuel"],
        "x": telemetry["lander"]["x"],
        "zone_x": telemetry.get("landing_zone_center_x", 0),
        "is_over_zone": telemetry.get("is_over_landing_zone", False),
        "actions": actions,
        "reason": reason
    }
    with open(self.log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

Analyze logs with `analyze_log.py`:
```bash
python3 bots/analyze_log.py bot_log_*.jsonl
```

## Performance Tips

1. **Update Rate**: Use 60 Hz for rule-based bots, 2-10 Hz for LLMs
2. **Priority System**: Handle emergencies first (walls, crashes)
3. **Predictive Control**: Use `time_to_ground` and `impact_speed`
4. **Fuel Management**: Monitor `fuel_remaining_percent`
5. **Testing**: Start with "simple" difficulty, then progress

## Example Bots

- **simple_bot.py**: Rule-based, 70-90% success, 60 Hz
- **ollama_bot.py**: LLM-powered, 40-60% success, 1-2 Hz (proof-of-concept)

## Resources

- Full telemetry documentation: `../TELEMETRY.md`
- Game architecture: `../ARCHITECTURE.md`
- Scoring system: `../SCORING.md`

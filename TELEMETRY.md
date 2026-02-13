# Telemetry Modes and Update Rates

The Lunar Lander server supports configurable telemetry modes and update rates to optimize for different client types.

## Update Rates

### Human Players (60 Hz - Default)
- **Update interval**: 16.67ms
- **Bandwidth**: ~30 KB/s (standard) or ~48 KB/s (advanced)
- **Use for**: Human players with real-time control

### Bot AI (60 Hz)
- **Update interval**: 16.67ms
- **Bandwidth**: ~48 KB/s (advanced mode recommended)
- **Use for**: Rule-based AI, neural networks, fast ML models
- **Decision time**: <1ms required

### LLM AI (2-10 Hz)
- **Update interval**: 100-500ms
- **Bandwidth**: ~1-5 KB/s (advanced mode recommended)
- **Use for**: Language model AI (GPT, Claude, etc.)
- **Decision time**: 200-1500ms typical
- **Recommended**: 5 Hz (200ms) for fast models, 2 Hz (500ms) for large models

## Telemetry Modes

## Standard Mode (Default)

**Use for**: Human players, spectators, replays

**Bandwidth**: ~500 bytes/frame @ 60Hz = ~30 KB/s

**Fields included**:
- `lander` - Full lander state (position, velocity, rotation, fuel, status)
- `terrain_height` - Ground level at current x position
- `altitude` - Height above terrain
- `speed` - Total velocity magnitude
- `thrusting` - Boolean thrust state
- `nearest_landing_zone` - Closest landing zone with distance/direction
- `all_landing_zones` - All landing zones (now just 1)
- `spectator_count` - Number of spectators

## Advanced Mode

**Use for**: AI clients that need scoring optimization

**Bandwidth**: ~800 bytes/frame @ 60Hz = ~48 KB/s (+60% vs standard)

**Additional fields**:

### Landing Zone Targeting
- `is_over_landing_zone` - Boolean: currently over target
- `landing_zone_center_x` - Optimal x coordinate to aim for

### Safety Metrics
- `is_safe_speed` - Boolean: speed < 5.0 m/s (safe to land)
- `is_safe_angle` - Boolean: angle < 17° (upright enough)
- `angle_degrees` - Angle in degrees (easier than radians)
- `vertical_speed` - vy component (critical for landing)
- `horizontal_speed` - vx component (for drift correction)

### Scoring Optimization
- `elapsed_time` - Seconds since game start
- `fuel_remaining_percent` - Fuel as 0.0-1.0 (for bonus calculation)
- `estimated_score` - Score if landed right now
- `max_possible_score` - Best achievable for this difficulty

### Trajectory Prediction
- `time_to_ground` - Seconds until impact (if no thrust)
- `impact_speed` - Predicted speed at impact (if no thrust)

## Usage

### JavaScript Client
```javascript
// Human player (60 Hz, standard telemetry)
wsClient.startGame('medium');

// Bot AI (60 Hz, advanced telemetry)
wsClient.startGame('medium', null, 'advanced', 60);

// LLM AI - Fast model (5 Hz, advanced telemetry)
wsClient.startGame('medium', null, 'advanced', 5);

// LLM AI - Large model (2 Hz, advanced telemetry)
wsClient.startGame('medium', null, 'advanced', 2);
```

### Python AI Client
```python
# Bot AI (60 Hz)
ws.send(json.dumps({
    "type": "start",
    "difficulty": "medium",
    "telemetry_mode": "advanced",
    "update_rate": 60
}))

# LLM AI (5 Hz for GPT-4o-mini/Claude Haiku)
ws.send(json.dumps({
    "type": "start",
    "difficulty": "medium",
    "telemetry_mode": "advanced",
    "update_rate": 5
}))

# LLM AI (2 Hz for GPT-4o/Claude Sonnet)
ws.send(json.dumps({
    "type": "start",
    "difficulty": "medium",
    "telemetry_mode": "advanced",
    "update_rate": 2
}))
```

## Performance Considerations

### Update Rate Impact

| Client Type | Update Rate | Bandwidth | Server CPU | Latency Tolerance |
|-------------|-------------|-----------|------------|-------------------|
| Human | 60 Hz | 30 KB/s | Baseline | <50ms |
| Bot AI | 60 Hz | 48 KB/s | +10% | <1ms |
| LLM (Fast) | 5 Hz | 4 KB/s | -80% | 200-500ms |
| LLM (Large) | 2 Hz | 1.6 KB/s | -95% | 500-1500ms |

### Telemetry Mode Impact

**Standard Mode**:
- Suitable for 100+ concurrent players
- Minimal server CPU overhead
- ~30 KB/s per connection @ 60Hz

**Advanced Mode**:
- Recommended for AI clients only
- Additional calculations per frame:
  - Angle conversion (radians → degrees)
  - Safety checks (2 comparisons)
  - Score estimation (function call)
  - Trajectory prediction (kinematic equation)
- ~48 KB/s per connection @ 60Hz
- ~10% additional CPU per session

### LLM Mode Benefits

**Reduced Load**:
- 5 Hz = 92% less bandwidth than 60 Hz
- 2 Hz = 97% less bandwidth than 60 Hz
- Allows 10-50x more concurrent LLM clients

**Playability**:
- Game physics still runs at 60 Hz (smooth)
- LLM receives updates at slower rate
- LLM has 100-500ms to make decisions
- Actions are applied immediately when received

**Recommendation**: 
- **Humans**: 60 Hz, standard mode
- **Bot AI**: 60 Hz, advanced mode
- **LLM (fast)**: 5 Hz, advanced mode (GPT-4o-mini, Claude Haiku)
- **LLM (large)**: 2 Hz, advanced mode (GPT-4o, Claude Sonnet)

## Example Telemetry

### Standard Mode
```json
{
  "type": "telemetry",
  "timestamp": 1707856234.567,
  "lander": {
    "x": 550.5,
    "y": 650.2,
    "vx": -1.2,
    "vy": 3.5,
    "rotation": 0.15,
    "fuel": 750,
    "crashed": false,
    "landed": false
  },
  "terrain_height": 700,
  "altitude": 49.8,
  "speed": 3.7,
  "thrusting": true,
  "nearest_landing_zone": {
    "x1": 500,
    "x2": 600,
    "center_x": 550,
    "y": 700,
    "width": 100,
    "distance": 0.5,
    "direction": "right"
  },
  "all_landing_zones": [...],
  "spectator_count": 2
}
```

### Advanced Mode (additional fields)
```json
{
  ...all standard fields...,
  "is_over_landing_zone": true,
  "landing_zone_center_x": 550,
  "is_safe_speed": true,
  "is_safe_angle": true,
  "angle_degrees": 8.6,
  "vertical_speed": 3.5,
  "horizontal_speed": -1.2,
  "elapsed_time": 15.3,
  "fuel_remaining_percent": 0.75,
  "estimated_score": 1650,
  "max_possible_score": 1800,
  "time_to_ground": 4.2,
  "impact_speed": 10.3
}
```

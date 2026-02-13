# Telemetry Modes

The Lunar Lander server supports two telemetry modes to balance performance and functionality.

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
// Standard mode (default)
wsClient.startGame('medium');

// Advanced mode (for AI)
wsClient.startGame('medium', null, 'advanced');
```

### Python AI Client
```python
# Connect and start with advanced telemetry
ws.send(json.dumps({
    "type": "start",
    "difficulty": "medium",
    "telemetry_mode": "advanced"
}))
```

## Performance Considerations

**Standard Mode**:
- Suitable for 100+ concurrent players
- Minimal server CPU overhead
- ~30 KB/s per connection

**Advanced Mode**:
- Recommended for AI clients only
- Additional calculations per frame:
  - Angle conversion (radians → degrees)
  - Safety checks (2 comparisons)
  - Score estimation (function call)
  - Trajectory prediction (kinematic equation)
- ~48 KB/s per connection
- ~10% additional CPU per session

**Recommendation**: Use standard mode for human players and spectators. Only request advanced mode when you need the AI optimization features.

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

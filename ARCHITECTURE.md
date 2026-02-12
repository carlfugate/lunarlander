# Architecture & Technical Documentation

## Project Structure

```
lunarlander/
├── server/
│   ├── game/
│   │   ├── physics.py       # Lander physics & collision detection
│   │   ├── terrain.py       # Procedural terrain generation
│   │   ├── session.py       # Game session management & scoring
│   │   └── replay.py        # Replay recording & optimization
│   ├── tests/
│   │   ├── test_physics.py  # Physics engine tests (12 tests)
│   │   ├── test_terrain.py  # Terrain generation tests (9 tests)
│   │   ├── test_scoring.py  # Scoring system tests (11 tests)
│   │   └── test_integration_scoring.py  # Integration tests
│   ├── main.py              # FastAPI WebSocket server
│   ├── firebase_config.py   # Firebase auth (optional)
│   └── requirements.txt
├── client/
│   ├── js/
│   │   ├── main-menu.js     # Menu & mode selection
│   │   ├── renderer.js      # Canvas rendering with HUD
│   │   ├── websocket.js     # WebSocket client with retry logic
│   │   ├── input.js         # Keyboard input handling
│   │   ├── replay.js        # Replay player
│   │   └── config.js        # Environment configuration
│   ├── css/
│   │   └── style.css        # Retro green terminal styling
│   ├── tests/
│   │   └── input.test.js    # Input handler tests (9 tests)
│   └── index.html
├── examples/
│   └── simple_ai.py         # Example AI client
├── docs/
│   └── images/              # Screenshots
├── nginx.conf               # Reverse proxy configuration
├── ngrok.yml                # ngrok tunnel configuration
└── README.md
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client (Browser)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ HTML5 Canvas │  │  WebSocket   │  │    Input     │      │
│  │  Renderer    │  │    Client    │  │   Handler    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket (ws://)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    nginx (Port 80)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Static Files: /css, /js, /index.html               │   │
│  │  Proxy: /ws, /spectate, /games, /replays → :8000    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server (Port 8000)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   WebSocket  │  │  Game Loop   │  │   Replay     │      │
│  │   Handlers   │  │   (60Hz)     │  │  Recording   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Physics    │  │   Terrain    │  │   Scoring    │      │
│  │   Engine     │  │  Generator   │  │   System     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Game Physics

### Constants
```python
GRAVITY = 1.62          # m/s² (lunar gravity)
THRUST_POWER = 8.0      # m/s² acceleration
ROTATION_SPEED = 3.0    # radians/s
INITIAL_FUEL = 1000.0   # units
FUEL_CONSUMPTION = 10.0 # units/s when thrusting
```

### Physics Loop (60Hz)
1. Apply rotation based on input
2. Apply thrust if active and fuel available
3. Apply gravity
4. Update position based on velocity
5. Check collision with terrain
6. Validate landing conditions
7. Broadcast telemetry to player and spectators

### Landing Validation
```python
# Safe landing requires:
speed < 5.0 m/s          # Total velocity
abs(rotation) < 0.3 rad  # ~17 degrees
is_landing_zone = True   # On flat green zone
```

## WebSocket API

### Player Connection

**Connect:**
```
ws://localhost:8000/ws
```

**Start Game:**
```json
{
  "type": "start",
  "difficulty": "simple" | "medium" | "hard"
}
```

**Receive Init:**
```json
{
  "type": "init",
  "terrain": {
    "points": [[x, y], ...],
    "landing_zones": [{x1, x2, y, multiplier}, ...],
    "width": 1200,
    "height": 800
  },
  "lander": {
    "x": 600, "y": 100,
    "vx": 0, "vy": 0,
    "rotation": 0,
    "fuel": 1000,
    "crashed": false,
    "landed": false
  },
  "constants": {
    "gravity": 1.62,
    "thrust_power": 8.0,
    "rotation_speed": 3.0,
    "fuel_consumption_rate": 10.0,
    "max_landing_speed": 5.0,
    "max_landing_angle": 0.3,
    "terrain_width": 1200,
    "terrain_height": 800
  }
}
```

**Receive Telemetry (60Hz):**
```json
{
  "type": "telemetry",
  "timestamp": 1770868000.0,
  "lander": {
    "x": 600, "y": 300,
    "vx": 0.5, "vy": 2.3,
    "rotation": 0.1,
    "fuel": 850,
    "crashed": false,
    "landed": false
  },
  "terrain_height": 700,
  "altitude": 400,
  "speed": 2.35,
  "thrusting": true,
  "spectator_count": 3,
  "nearest_landing_zone": {
    "x1": 450, "x2": 550,
    "center_x": 500,
    "y": 650,
    "width": 100,
    "distance": 100,
    "direction": "left"
  },
  "all_landing_zones": [...]
}
```

**Send Input:**
```json
{"type": "input", "action": "thrust_on"}
{"type": "input", "action": "thrust_off"}
{"type": "input", "action": "rotate_left"}
{"type": "input", "action": "rotate_right"}
{"type": "input", "action": "rotate_stop"}
```

**Receive Game Over:**
```json
{
  "type": "game_over",
  "landed": true,
  "crashed": false,
  "time": 143.0,
  "fuel_remaining": 568,
  "inputs": 216,
  "score": 2450,
  "replay_id": "session_id_timestamp"
}
```

### Spectator Connection

**Connect:**
```
ws://localhost:8000/spectate/{session_id}
```

**Receive Init + Telemetry:**
Same as player, but read-only (no input sending).

Spectators receive telemetry at 30Hz (50% bandwidth reduction).

## REST API

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "firebase_enabled": false
}
```

### GET /games
List all active game sessions.

**Response:**
```json
{
  "games": [
    {
      "session_id": "uuid",
      "user_id": "anonymous",
      "difficulty": "medium",
      "spectators": 3,
      "duration": 45.2
    }
  ]
}
```

### GET /replays
List all recorded replays.

**Response:**
```json
{
  "replays": [
    {
      "replay_id": "session_id_timestamp",
      "user_id": "anonymous",
      "difficulty": "hard",
      "duration": 38.5,
      "landed": true,
      "crashed": false,
      "timestamp": 1770868000.0
    }
  ]
}
```

### GET /replay/{replay_id}
Get specific replay data.

**Response:**
```json
{
  "metadata": {
    "session_id": "uuid",
    "user_id": "anonymous",
    "difficulty": "hard",
    "duration": 38.5,
    "landed": true,
    "crashed": false,
    "fuel_remaining": 234,
    "input_count": 156,
    "timestamp": 1770868000.0,
    "terrain": {...}
  },
  "frames": [
    {
      "lander": {...},
      "altitude": 400,
      "speed": 2.35,
      "thrusting": true
    },
    ...
  ]
}
```

## Scoring System

### Formula
```python
if crashed or not landed:
    score = 0
else:
    base = 1000
    fuel_bonus = (fuel_remaining / 1000) * 500
    time_bonus = max(0, 300 - (time - 20) * 5)
    
    multiplier = {
        "simple": 1.0,
        "medium": 1.5,
        "hard": 2.0
    }[difficulty]
    
    score = int((base + fuel_bonus + time_bonus) * multiplier)
```

### Score Ranges
- **Easy**: 1,300 - 1,800 points
- **Medium**: 1,950 - 2,700 points
- **Hard**: 2,600 - 3,600 points

## Terrain Generation

### Simple (Easy)
- Mostly flat with gentle slopes
- Y variation: ±20 pixels
- Point spacing: 50 pixels
- Landing zone width: ≥50 pixels

### Medium
- Rolling hills
- Y variation: ±30 pixels
- Point spacing: 40 pixels
- Landing zone width: ≥40 pixels

### Hard
- Steep mountains
- Y variation: ±50 pixels
- Point spacing: 30 pixels
- Landing zone width: ≥30 pixels

### Landing Zone Detection
Flat segments where `abs(y2 - y1) < 5` pixels and width meets difficulty requirement.

## Replay System

### Recording
- Captured at 30Hz (every other physics frame)
- Stores: lander state, altitude, speed, thrusting
- Quantization: 2 decimal places for floats
- Size: ~900 KB per 30-second game

### Optimization
- 30Hz vs 60Hz: 50% size reduction
- Quantization: 12% additional reduction
- Total: 62% smaller than naive approach

### Playback
- Client-side replay player
- 30fps playback (smooth enough)
- Full HUD and telemetry display

## Security Features

### Rate Limiting
- `/games`: 30 requests/min per IP
- `/replays`: 30 requests/min per IP
- `/replay/{id}`: 60 requests/min per IP
- Library: slowapi with in-memory storage

### Input Validation
- Message size limit: 1KB max
- JSON structure validation
- Action whitelist: `["thrust", "thrust_on", "thrust_off", "rotate_left", "rotate_right", "rotate_stop"]`
- Difficulty validation: `["simple", "medium", "hard"]`
- 10-second timeout on initial connection

### Connection Limits
- Max active sessions: 100
- Max spectators per game: 100
- Max total replays: 500 (FIFO eviction)

### Session Cleanup
- Auto-cleanup after 10 minutes idle
- Runs on every `/games` request
- Removes abandoned sessions

### Server-Authoritative Design
All game logic runs on server:
- Physics calculations
- Collision detection
- Fuel consumption
- Landing validation
- Score calculation

Clients only send input commands - cannot cheat!

## Performance

### Server
- Physics loop: 60Hz (16.67ms per frame)
- Player telemetry: 60Hz
- Spectator telemetry: 30Hz
- Replay recording: 30Hz

### Client
- Rendering: 60fps
- Canvas: 1200x800 pixels
- Responsive scaling to fit screen

### Network
- Player bandwidth: ~120 KB/s (960 Kbps)
- Spectator bandwidth: ~60 KB/s (480 Kbps)
- Replay size: ~900 KB per 30s game

### Scaling
- 100 spectators: ~6 Mbps bandwidth
- 1,000 spectators: ~60 Mbps bandwidth
- Bottleneck: Network bandwidth, not CPU

## Testing

### Unit Tests (46 tests)
- Physics engine: 12 tests
- Terrain generation: 9 tests
- Scoring system: 11 tests
- Input handling: 9 tests
- Replay optimization: 4 tests
- WebSocket client: 5 tests

### Integration Tests (4 tests)
- Difficulty selection
- WebSocket connection
- Telemetry reception
- Invalid input handling

### E2E Tests (11 tests)
- Full game flow
- Spectator mode
- Replay playback

### Run Tests
```bash
# Python tests
cd server
source ../venv/bin/activate
PYTHONPATH=. pytest tests/ -v

# JavaScript tests
cd client
npm test

# All tests
./run-tests.sh
```

## Deployment

### Local Development
```bash
# Terminal 1 - FastAPI
cd server && source ../venv/bin/activate
uvicorn main:app --port 8000

# Terminal 2 - Static files
cd client && python3 -m http.server 8081

# Access: http://localhost:8081
```

### Production (nginx + ngrok)
```bash
# Terminal 1 - FastAPI
cd server && source ../venv/bin/activate
uvicorn main:app --port 8000

# Terminal 2 - nginx
sudo nginx

# Terminal 3 - ngrok
ngrok start lunarlander

# Access: https://your-ngrok-url.ngrok.io
```

### nginx Configuration
See `nginx.conf` for full configuration.

Key features:
- Serves static files from `client/`
- Proxies API/WebSocket to FastAPI (port 8000)
- Accepts any hostname (localhost, ngrok, custom domain)
- Single-port deployment (port 80)

## Firebase Integration (Optional)

### Setup
1. Create Firebase project
2. Enable Authentication (Email/Password)
3. Enable Realtime Database
4. Download service account key → `server/firebase-credentials.json`
5. Add Firebase web config to `client/js/firebase-config.js`

### Features
- User authentication
- Leaderboards (planned)
- User profiles (planned)

## Development Roadmap

### Phase 1-7: Core Game ✅
- Project setup
- Physics engine
- WebSocket server
- Canvas renderer
- Input handling
- Spectator mode
- Replay system

### Phase 8: Polish & Features (85% complete)
- ✅ Scoring system
- ✅ Difficulty selection
- ✅ Security hardening
- ✅ Automated testing
- ⏳ Visual polish (particles, explosions)
- ⏳ Leaderboard system
- ⏳ Sound effects
- ⏳ Mobile touch controls

### Phase 9: Production (Planned)
- Redis for distributed rate limiting
- Database for persistent replays
- Horizontal scaling with load balancer
- CDN for static assets
- Monitoring and alerting

## Contributing

### Code Style
- Python: PEP 8
- JavaScript: Standard JS
- Comments for complex logic
- Type hints in Python

### Adding Features
1. Add tests first (TDD)
2. Implement feature
3. Update documentation
4. Submit PR

### Project Goals
- Educational: Learn game dev + WebSockets
- Competitive: AI vs human leaderboards
- Extensible: Easy to add features
- Performant: 60Hz physics, smooth rendering

## License

MIT License - See LICENSE file for details.

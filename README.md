# Lunar Lander - AI/Human Game

A browser-based Lunar Lander game with WebSocket API for AI players, featuring real-time telemetry streaming, live spectator mode, and replay recording.

## Features

### Core Gameplay
- **Browser-based HTML5 Canvas** rendering at 60fps
- **Server-authoritative physics** - Classic Atari Lunar Lander style
- **Dual play modes**: Human (keyboard) and AI (WebSocket API)
- **Real-time telemetry** at 60Hz for AI decision-making
- **Three difficulty levels**: Simple, Intermediate, Advanced (terrain generation)

### Game Modes
- **Play Mode**: Human players control with keyboard
- **Spectator Mode**: Watch live games in real-time with full telemetry
- **Replay Mode**: Watch recorded games with accurate playback

### Technical Features
- **WebSocket communication** for real-time gameplay
- **Replay recording** - All games automatically recorded with full state
- **Live spectating** - Multiple spectators per game with real-time updates
- **Color-coded HUD** - Green/red indicators for safe landing parameters
- **Comprehensive telemetry** - Position, velocity, fuel, landing zones, altitude, speed
- **Server-calculated metrics** - Accurate altitude and speed from server physics

## Quick Start

### 1. Server Setup

```bash
cd server
python3 -m venv ../venv
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Client Setup

```bash
cd client
python3 -m http.server 8080
```

Open browser to **http://localhost:8080**

## How to Play

### Human Controls
- **Arrow Up**: Thrust
- **Arrow Left/Right**: Rotate
- **R**: Restart after game over
- **ESC**: Return to menu

### Landing Requirements
- **Speed**: < 5.0 m/s total velocity
- **Angle**: < 17° from vertical
- **Location**: Must land on green landing zones

Watch the HUD - Speed and Angle indicators turn **GREEN** when safe to land!

## AI Client

### Running the Example AI

```bash
cd examples
python3 simple_ai.py
```

The AI will autonomously navigate and attempt to land.

### WebSocket API

**Connect to game:**
```
ws://localhost:8000/ws
```

**Start game:**
```json
{"type": "start", "difficulty": "simple"}
```

**Receive telemetry (60Hz):**
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
  "altitude": 400,
  "speed": 2.35,
  "terrain_height": 700,
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

**Send input:**
```json
{"type": "input", "action": "thrust"}
{"type": "input", "action": "thrust_off"}
{"type": "input", "action": "rotate_left"}
{"type": "input", "action": "rotate_right"}
{"type": "input", "action": "rotate_stop"}
```

**Game over:**
```json
{
  "type": "game_over",
  "landed": true,
  "crashed": false,
  "time": 143.0,
  "fuel_remaining": 568,
  "inputs": 216,
  "replay_id": "session_id_timestamp"
}
```

## Spectator Mode

### List Active Games
```bash
curl http://localhost:8000/games
```

### Spectate via WebSocket
```
ws://localhost:8000/spectate/{session_id}
```

Spectators receive the same telemetry as players in real-time.

### Browser UI
1. Click "Spectate Live Game" from menu
2. Select a game from the list
3. Watch in real-time with full HUD

## Replay System

### List Replays
```bash
curl http://localhost:8000/replays
```

### Get Replay Data
```bash
curl http://localhost:8000/replay/{replay_id}
```

All games are automatically recorded at 60Hz with full game state.

## Project Structure

```
lunarlander/
├── server/
│   ├── game/
│   │   ├── physics.py       # Lander physics & collision
│   │   ├── terrain.py       # Procedural terrain generation
│   │   ├── session.py       # Game session management
│   │   └── replay.py        # Replay recording
│   ├── main.py              # FastAPI WebSocket server
│   ├── firebase_config.py   # Firebase auth (optional)
│   └── requirements.txt
├── client/
│   ├── js/
│   │   ├── main-menu.js     # Menu & mode selection
│   │   ├── renderer.js      # Canvas rendering
│   │   ├── websocket.js     # WebSocket client
│   │   ├── input.js         # Keyboard input
│   │   └── replay.js        # Replay player
│   ├── css/
│   │   └── style.css
│   └── index.html
├── examples/
│   └── simple_ai.py         # Example AI client
└── README.md
```

## Game Physics

- **Gravity**: 1.62 m/s² (lunar gravity)
- **Thrust Power**: 5.0 m/s² acceleration
- **Rotation Speed**: 3.0 rad/s
- **Initial Fuel**: 1000 units
- **Fuel Consumption**: 10 units/s when thrusting

## API Endpoints

### REST API
- `GET /health` - Server health check
- `GET /games` - List active game sessions
- `GET /replays` - List all recorded replays
- `GET /replay/{replay_id}` - Get specific replay data

### WebSocket
- `ws://localhost:8000/ws` - Play game
- `ws://localhost:8000/spectate/{session_id}` - Spectate game

## Development Status

### ✅ Completed (Tasks 1-6, 9-10)
- Project setup and structure
- Core physics engine
- WebSocket server with 60Hz game loop
- HTML5 Canvas renderer
- Client WebSocket integration
- Keyboard input handling
- Replay recording system
- Live spectator mode
- Menu system with mode selection

### 🚧 In Progress
- Replay playback in browser (needs terrain storage)

### 📋 Planned (Tasks 7-8, 12-13)
- Scoring system (time/fuel/inputs based)
- Firebase leaderboards (human vs AI categories)
- Difficulty selection UI
- Firebase authentication integration
- Error handling and reconnection logic
- User registration/login UI

## Firebase Setup (Optional)

To enable authentication and leaderboards:

1. Create Firebase project at https://console.firebase.google.com
2. Enable Authentication (Email/Password)
3. Enable Realtime Database
4. Download service account key → `server/firebase-credentials.json`
5. Add Firebase web config to `client/js/firebase-config.js`

## Contributing

The game is designed to be extensible:
- Add new AI strategies in `examples/`
- Modify physics constants in `server/game/physics.py`
- Add new terrain generators in `server/game/terrain.py`
- Customize rendering in `client/js/renderer.js`

## License

MIT License - Feel free to use and modify!

## Credits

Inspired by the classic 1979 Atari Lunar Lander arcade game.

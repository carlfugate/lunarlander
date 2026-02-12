# Replay and Spectator Features

## Task 9: Replay Recording System ✅

### Features Implemented:
- **Automatic replay recording** for all games
- **Frame-by-frame capture** at 60Hz
- **Metadata tracking**: user, difficulty, duration, result
- **Compression support** using gzip
- **In-memory storage** (can be extended to database/Firebase)

### API Endpoints:

**List all replays:**
```
GET /replays
```
Returns list of all recorded replays with metadata.

**Get specific replay:**
```
GET /replay/{replay_id}
```
Returns full replay data including all frames.

### Replay Data Structure:
```json
{
  "metadata": {
    "session_id": "...",
    "user_id": "...",
    "difficulty": "simple",
    "start_time": 1770868000.0,
    "end_time": 1770868143.0,
    "duration": 143.0,
    "landed": true,
    "crashed": false,
    "fuel_remaining": 568,
    "inputs": 216,
    "frame_count": 8580
  },
  "frames": [
    {
      "lander": {
        "x": 600, "y": 100,
        "vx": 0, "vy": 0,
        "rotation": 0,
        "fuel": 1000,
        "crashed": false,
        "landed": false
      },
      "terrain_height": 700,
      "timestamp": 1770868000.016
    },
    ...
  ]
}
```

## Task 10: Live Spectator Mode ✅

### Features Implemented:
- **Real-time spectating** of active games
- **Multiple spectators** per game
- **Automatic broadcast** of telemetry to all spectators
- **Active games list** endpoint

### API Endpoints:

**List active games:**
```
GET /games
```
Returns list of all currently running games.

**Spectate a game:**
```
WebSocket /spectate/{session_id}
```
Connect as spectator to watch a live game.

### Usage:

**1. List active games:**
```bash
curl http://localhost:8000/games
```

**2. Connect as spectator:**
```javascript
const ws = new WebSocket('ws://localhost:8000/spectate/SESSION_ID');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Receive same telemetry as player
    if (data.type === 'telemetry') {
        // Update spectator view
    }
};
```

**3. Spectators receive:**
- Initial game state (terrain, starting position)
- Real-time telemetry at 60Hz
- Game over notification

### Testing:

**Test replay recording:**
1. Play a game (human or AI)
2. After game ends, check: `curl http://localhost:8000/replays`
3. Get replay: `curl http://localhost:8000/replay/REPLAY_ID`

**Test spectator mode:**
1. Start a game in one terminal/browser
2. Get session ID from server logs or `/games` endpoint
3. Connect spectator: `ws://localhost:8000/spectate/SESSION_ID`
4. Spectator sees live game updates

## Next Steps:

To implement replay playback in the client:
1. Fetch replay data from `/replay/{id}`
2. Step through frames at 60fps
3. Render each frame's lander state
4. Add playback controls (play/pause/speed)

To add spectator UI:
1. List active games from `/games`
2. Allow user to select game to watch
3. Connect to `/spectate/{session_id}`
4. Render game in read-only mode

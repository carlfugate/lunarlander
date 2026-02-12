# Quick Reference Guide

## Starting the Game

### Terminal 1 - Server
```bash
cd ~/Documents/Github/lunarlander/server
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Terminal 2 - Client
```bash
cd ~/Documents/Github/lunarlander/client
python3 -m http.server 8080
```

### Terminal 3 - AI Player (Optional)
```bash
cd ~/Documents/Github/lunarlander/examples
python3 simple_ai.py
```

## Browser
Open: **http://localhost:8080**

## Game Modes

### 1. Play Mode
- Click "Play Game"
- Use Arrow keys to control
- Land on green zones with Speed < 5.0 and Angle < 17°

### 2. Spectator Mode
- Click "Spectate Live Game"
- Select active game from list
- Watch in real-time

### 3. Replay Mode
- Click "Watch Replay"
- Select from recorded games
- (Full playback coming soon)

## Keyboard Controls

| Key | Action |
|-----|--------|
| ↑ | Thrust |
| ← | Rotate Left |
| → | Rotate Right |
| R | Restart (after game over) |
| ESC | Return to Menu |

## HUD Indicators

| Indicator | Green | Red |
|-----------|-------|-----|
| Speed | < 5.0 m/s | ≥ 5.0 m/s |
| Angle | < 17° | ≥ 17° |
| Fuel | > 100 | ≤ 100 |

## API Quick Reference

### List Active Games
```bash
curl http://localhost:8000/games
```

### List Replays
```bash
curl http://localhost:8000/replays
```

### Get Replay
```bash
curl http://localhost:8000/replay/{replay_id}
```

## AI Development

### Telemetry Data (60Hz)
```javascript
{
  lander: { x, y, vx, vy, rotation, fuel },
  altitude: 400,  // Above terrain
  speed: 2.35,    // Total velocity
  nearest_landing_zone: {
    x1, x2, center_x, y, width, distance, direction
  }
}
```

### Input Commands
```javascript
{type: "input", action: "thrust"}
{type: "input", action: "thrust_off"}
{type: "input", action: "rotate_left"}
{type: "input", action: "rotate_right"}
{type: "input", action: "rotate_stop"}
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

### Black Screen in Spectator Mode
- Restart server (fixed in latest version)
- Spectators now receive game state immediately

### AI Not Landing
- Check altitude calculation (uses terrain height, not screen top)
- Ensure horizontal velocity control (brake when moving sideways)
- Navigate to landing zone before descending below 50m

## File Locations

### Server Code
- `server/game/physics.py` - Physics constants and lander logic
- `server/game/terrain.py` - Terrain generation
- `server/game/session.py` - Game loop and telemetry
- `server/main.py` - WebSocket endpoints

### Client Code
- `client/js/main-menu.js` - Menu and mode selection
- `client/js/renderer.js` - Canvas rendering and HUD
- `client/js/websocket.js` - WebSocket client
- `client/js/input.js` - Keyboard controls

### AI Example
- `examples/simple_ai.py` - Working AI with landing logic

## Next Steps

To continue development:
1. **Task 7**: Add scoring system
2. **Task 8**: Implement Firebase leaderboards
3. **Task 12**: Add difficulty selection UI
4. **Task 13**: Polish and error handling

## Git Repository

```bash
cd ~/Documents/Github/lunarlander
git log --oneline  # View commits
git status         # Check status
```

Current commit: Initial implementation with Play/Spectate/Replay modes

# 🚀 Lunar Lander

![CI](https://github.com/carlfugate/lunarlander/workflows/CI/badge.svg)

A modern browser-based remake of the classic 1979 Atari Lunar Lander arcade game, featuring real-time multiplayer spectating, AI support, and competitive scoring.

## Screenshots

### Main Menu
![Start Screen](docs/images/start.png)
*Main menu showing single-player, multiplayer, spectate, and replay options*

### Multiplayer Lobby
![Multiplayer Lobby](docs/images/multiplayer.png)
*Waiting lobby where players join before the game starts*

### Live Gameplay
![Gameplay](docs/images/gameplay.png)
*Active game showing lander, terrain, HUD with fuel/speed/altitude, and landing zones*

### Spectate Mode
![Spectate Mode](docs/images/spectate.png)
*Real-time spectating of live games with full telemetry display*

## 🎮 Features

### Three Difficulty Levels
- **Easy**: Gentle terrain, more fuel - Perfect for learning
- **Medium**: Moderate terrain, standard fuel - Balanced challenge  
- **Hard**: Rough terrain, limited fuel - Expert mode

### Competitive Scoring
- **Base Score**: 1,000 points for successful landing
- **Fuel Bonus**: Up to 500 points (conserve fuel!)
- **Time Bonus**: Up to 300 points (land quickly!)
- **Difficulty Multiplier**: 1x Easy, 1.5x Medium, 2x Hard
- **Maximum Score**: 3,600 points (perfect landing on Hard)

### Game Modes
- **🎮 Play**: Single-player mode with three difficulty levels
- **👥 Multiplayer**: Create or join rooms to play with friends
- **👁️ Spectate**: Watch live games in real-time
- **📹 Replay**: Watch recorded games

### Multiplayer Features
- **Room Creation**: Create custom-named rooms for friends
- **Waiting Lobby**: See all players before starting
- **Creator Control**: Room creator starts the game
- **Colored Landers**: Each player has a unique color
- **Player Names**: Names displayed above landers
- **Individual Tracking**: Separate scores, fuel, and finish times
- **Game Continues**: Play until ALL players finish
- **Ranked Results**: Final leaderboard with all players
- **Spectate Support**: Watch multiplayer games live

### Mobile Support
- **Touch Controls**: Optimized for mobile devices
- **Landscape Mode**: Best experience in horizontal orientation
- **Responsive Design**: Adapts to screen size
- **Swappable Controls**: Choose left or right-handed layout
- **Full Feature Parity**: All gameplay features available on mobile

### Live Spectating
- Watch other players in real-time
- See spectator count in-game
- Full telemetry and HUD display
- Multiple spectators per game

### AI Support
- WebSocket API for AI clients
- 60Hz real-time telemetry
- Example AI included
- Perfect for competitions

### CLI Terminal Client
- Interactive terminal-based game client
- Full gameplay with ASCII graphics
- Real-time telemetry display
- Perfect for headless environments

**Installation:**
```bash
cd cli
pip install -r requirements.txt
```

**Usage:**
```bash
python terminal_client.py
```

See [docs/CLI_CLIENT.md](docs/CLI_CLIENT.md) for full documentation.

## 🚀 Quick Start

### Development Workflow

**Before making changes:**
```bash
./cli/run_all_tests.sh  # Ensure tests pass
```

**After making changes:**
```bash
./cli/run_all_tests.sh  # Tests run automatically on commit
git add .
git commit -m "Your message"  # Pre-commit hook runs tests
```

**Pre-commit hook automatically:**
- Runs unit tests (must pass)
- Checks coverage (75% minimum)
- Runs E2E tests (if server running)
- Reminds you to do manual testing

See [cli/TESTING_CHECKLIST.md](cli/TESTING_CHECKLIST.md) for detailed workflow.

### Play Locally

**1. Start the server:**
```bash
cd server
source ../venv/bin/activate  # venv is in project root
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**2. Build the client (first time or after changes):**
```bash
cd client
npm install
npm run build
```

**3. Start nginx:**
```bash
# macOS
brew services start nginx

# Linux
sudo systemctl start nginx
```

**4. Open your browser:**
```
http://localhost
```

### Deploy to Internet (ngrok)

```bash
ngrok start lunarlander
```

Access via the ngrok URL - game works identically!

## 🎯 How to Play

### Controls

**Desktop:**
- **↑ Arrow Up**: Thrust (main engine)
- **← → Arrow Left/Right**: Rotate lander
- **P**: Pause/Resume (single-player only)
- **R**: Restart after game over (single-player only)
- **ESC**: Return to menu

**Multiplayer Notes:**
- No pause or restart in multiplayer
- Game continues until all players finish
- ESC returns to menu after game over

**Mobile (< 768px):**
- **▲ Button**: Thrust (hold to thrust)
- **◀ ▶ Buttons**: Rotate left/right
- **↻ Button**: Restart (top-left)
- **☰ Button**: Menu (top-left)
- **⇄ Swap**: Switch control sides (preference saved)

**Mobile Layout:**
- Default: Thrust on left, Rotate on right
- Optimized for landscape orientation
- Touch-friendly button sizes

### Landing Requirements
✅ **Speed**: < 5.0 m/s total velocity  
✅ **Angle**: < 17° from vertical  
✅ **Location**: Green landing zones only

**Watch the HUD!** Speed and Angle indicators turn **GREEN** when safe to land.

### Strategy Tips
1. **Conserve fuel** - Each 1% fuel = 5 points
2. **Land quickly** - Every second after 20s costs 5 points
3. **Play on Hard** - 2x multiplier doubles your score
4. **Balance speed vs fuel** - Using thrust costs fuel but saves time

## 🤖 AI Client

### Run the Example AI
```bash
cd examples
python3 simple_ai.py
```

The AI will autonomously navigate and attempt to land.

### Build Your Own AI
Connect to `ws://localhost:8000/ws` and receive 60Hz telemetry including:
- Lander position, velocity, rotation, fuel
- Terrain height and landing zones
- Calculated altitude and speed
- Nearest landing zone with distance/direction

See [ARCHITECTURE.md](ARCHITECTURE.md) for full API documentation.

## 🏆 Scoring Examples

### Perfect Landing (Easy)
- Land in 20s with full fuel
- **Score: 1,800 points**

### Perfect Landing (Hard)
- Land in 20s with full fuel  
- **Score: 3,600 points** 🎯

### Realistic Landing (Medium)
- Land in 35s with 30% fuel
- **Score: 2,062 points**

### Crash
- **Score: 0 points** 💥

## 🔒 Security Features

Built for hacker conferences with security in mind:

- ✅ **Server-authoritative physics** - No client-side cheating
- ✅ **Rate limiting** - 30-60 requests/min per IP
- ✅ **Input validation** - Whitelist of valid actions
- ✅ **Connection limits** - 100 games, 100 spectators/game
- ✅ **Session cleanup** - Auto-remove after 10min idle
- ✅ **XSS protection** - No innerHTML usage

See [SECURITY.md](SECURITY.md) for full details.

## 📊 Stats

- **Lines of Code**: ~3,500 (Python: 1,800, JavaScript: 1,700)
- **Automated Tests**: 57 passing (unit + integration + E2E)
- **Test Coverage**: Core features covered
- **Performance**: 60Hz physics, 60fps rendering, 30Hz spectator updates

## 🛠️ Technology Stack

**Backend:**
- Python 3.14 + FastAPI
- WebSocket for real-time communication
- Server-authoritative physics at 60Hz

**Frontend:**
- HTML5 Canvas rendering
- Vanilla JavaScript (no frameworks)
- WebSocket client

**Deployment:**
- nginx reverse proxy
- ngrok for internet access
- Single-port deployment (port 80)

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details, API docs, project structure
- [SECURITY.md](SECURITY.md) - Security features and testing
- [SCORING.md](SCORING.md) - Detailed scoring system
- [TESTING.md](TESTING.md) - Testing strategy and coverage
- [NGROK.md](NGROK.md) - Deployment guide

## 🎯 Project Status

**Current Version**: 1.0 (Conference Ready)  
**Completion**: 85%

### ✅ Completed
- Core gameplay with physics
- Scoring system
- Difficulty selection
- Live spectating
- Replay system
- Security hardening
- 57 automated tests
- nginx + ngrok deployment

### 🚧 Planned
- Visual polish (particles, explosions)
- Leaderboard system
- Sound effects
- Mobile touch controls

## 🤝 Contributing

Contributions welcome! The game is designed to be extensible:
- Add new AI strategies in `examples/`
- Modify physics in `server/game/physics.py`
- Add terrain generators in `server/game/terrain.py`
- Customize rendering in `client/js/renderer.js`

## 📝 License

MIT License - Feel free to use and modify!

## 🎮 Credits

Inspired by the classic 1979 Atari Lunar Lander arcade game.

Built with ❤️ for hacker conferences and AI competitions.

---

**Ready to play?** Start the server and visit http://localhost 🚀


## 🛠️ Quick Commands

**Development:**
```bash
cd client
npm run dev              # Start dev server
npm run validate         # Run CSS linting + tests
npm test                 # Run unit tests (watch mode)
npm run test:e2e         # Run E2E tests
```

**Debugging:**
- Add `?debug=true` to URL to enable debug logs
- Press **`** (backtick) to toggle dev tools panel
- Run `logger.enable()` in console to enable debug mode
- Run `logger.perf.memory()` to check memory usage
- Run `logger.storage()` to inspect localStorage

**Testing:**
```bash
npm run lint:css         # Check CSS syntax
npm run validate         # Run all checks before commit
```

**Git Workflow:**
- Small fixes/docs → commit directly to master
- Major changes → create feature branch first
- See [Git Workflow](docs/GIT_WORKFLOW.md) for details


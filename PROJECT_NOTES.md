# Lunar Lander - AI/Human Game Project

## Project Overview

A browser-based implementation of the classic Lunar Lander game designed for both human players and AI agents. The project features server-authoritative physics, real-time WebSocket communication, live spectator mode, and automatic replay recording.

## Project Goals

### Primary Objectives
1. **Dual-Mode Gameplay**: Create a game playable by both humans (keyboard) and AI agents (WebSocket API)
2. **Real-Time Telemetry**: Provide comprehensive game state data at 60Hz for AI decision-making
3. **Spectator System**: Enable live viewing of games in progress
4. **Replay Recording**: Automatically capture and store all games for later analysis
5. **Fair Competition**: Server-authoritative physics ensures no client-side cheating

### Secondary Objectives
- Leaderboard system (human vs AI categories)
- Multiple difficulty levels
- Scoring system based on time, fuel efficiency, and input count
- Firebase integration for authentication and persistence
- Comprehensive API documentation for AI developers

## Technical Approach

### Architecture Decisions

#### 1. Server-Authoritative Physics
**Decision**: Run all physics calculations on the server, clients only render state.

**Rationale**:
- Single source of truth prevents desync issues
- Eliminates client-side cheating
- Simplifies replay system (just record server state)
- Fair for AI vs human competition

**Trade-offs**:
- ~16ms input latency (acceptable for this game type)
- Requires efficient server implementation
- More server CPU usage

#### 2. WebSocket Communication at 60Hz
**Decision**: Use WebSocket for bidirectional real-time communication with 60Hz update rate.

**Rationale**:
- Low latency for responsive gameplay
- Persistent connection reduces overhead
- 60Hz provides smooth visuals and sufficient data for AI
- Bidirectional allows server to push updates

**Trade-offs**:
- More complex than REST API
- Requires connection management
- Higher bandwidth than polling

#### 3. Monorepo Structure
**Decision**: Single repository with server (Python) and client (JavaScript) code.

**Rationale**:
- Shared constants between server and client
- Easier to keep physics and rendering synchronized
- Simpler deployment and version control
- Can still deploy components independently

**Trade-offs**:
- Mixed language codebase
- Requires coordination between frontend/backend changes

#### 4. Python FastAPI + Vanilla JavaScript
**Decision**: FastAPI for server, no frontend framework for client.

**Rationale**:
- FastAPI: Excellent async/WebSocket support, automatic API docs, type hints
- Vanilla JS: Minimal dependencies, fast load time, easier to understand
- Python: Great for AI developers (familiar ecosystem)

**Trade-offs**:
- No React/Vue reactivity (not needed for canvas game)
- Manual DOM manipulation for menus

### Physics Implementation

#### Classic Atari Lunar Lander Model
- **Gravity**: 1.62 m/s² (actual lunar gravity)
- **Thrust**: 5.0 m/s² (stronger than gravity for control)
- **Rotation**: 3.0 rad/s (responsive but not instant)
- **Fuel**: Limited resource (1000 units, 10 units/s consumption)

#### Collision Detection
- **Landing Success**: Speed < 5.0 m/s, Angle < 17°, On landing zone
- **Crash**: Any other ground contact
- **Bounds**: Lander must stay within terrain width

#### Design Choices
- **Forgiving speed limit**: 5.0 m/s (vs realistic 2.0 m/s) for better gameplay
- **Rotation normalization**: Prevents angle wrapping issues
- **Hysteresis in AI**: Prevents rapid thrust toggling

### Communication Protocol

#### Message Types

**Client → Server (Input)**
```json
{"type": "input", "action": "thrust|thrust_off|rotate_left|rotate_right|rotate_stop"}
```

**Server → Client (Telemetry - 60Hz)**
```json
{
  "type": "telemetry",
  "timestamp": 1770868000.0,
  "lander": {"x": 600, "y": 300, "vx": 0.5, "vy": 2.3, "rotation": 0.1, "fuel": 850},
  "altitude": 400,
  "speed": 2.35,
  "terrain_height": 700,
  "nearest_landing_zone": {"x1": 450, "x2": 550, "center_x": 500, "y": 650, "width": 100, "distance": 100, "direction": "left"},
  "all_landing_zones": [...]
}
```

**Server → Client (Game Over)**
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

#### Design Rationale
- **Calculated values in telemetry**: Server provides altitude and speed to reduce AI computation
- **All landing zones**: AI can choose optimal target
- **Nearest zone highlighted**: Simplifies basic AI logic
- **Timestamp included**: Enables latency measurement and debugging

### Spectator Mode Implementation

#### Approach
1. Spectators connect via separate WebSocket endpoint (`/spectate/{session_id}`)
2. Server maintains list of spectator connections per game session
3. Telemetry broadcast to both player and all spectators
4. Spectators receive current game state immediately on join (mid-game support)

#### Design Choices
- **Read-only**: Spectators cannot send input
- **Same data as player**: No information advantage/disadvantage
- **Multiple spectators**: No limit on concurrent viewers
- **Mid-game join**: Spectators can join games in progress

### Replay System Implementation

#### Recording Strategy
- **Frame-by-frame capture**: Record lander state every frame (60Hz)
- **Automatic recording**: All games recorded by default
- **Metadata tracking**: User, difficulty, duration, result, fuel, inputs
- **In-memory storage**: Fast access, can be extended to database/Firebase

#### Data Structure
```json
{
  "metadata": {
    "session_id": "...",
    "user_id": "...",
    "difficulty": "simple",
    "duration": 143.0,
    "landed": true,
    "fuel_remaining": 568,
    "inputs": 216,
    "frame_count": 8580
  },
  "frames": [
    {"lander": {...}, "terrain_height": 700, "timestamp": 1770868000.016},
    ...
  ]
}
```

#### Design Choices
- **Compression support**: gzip for efficient storage
- **Terrain not in frames**: Would need to be added for full replay playback
- **REST API access**: Easy to retrieve and analyze replays
- **Replay ID in game_over**: Links game result to replay

### AI Development Considerations

#### Telemetry Design
The telemetry was designed to provide everything an AI needs without requiring complex calculations:

1. **Altitude above terrain**: Pre-calculated (not altitude from screen top)
2. **Total speed**: Pre-calculated magnitude of velocity vector
3. **Nearest landing zone**: Identified with distance and direction
4. **All landing zones**: Allows strategic target selection
5. **Game constants**: Provided in init message for physics modeling

#### Example AI Strategy (simple_ai.py)
1. **Altitude-based thrust control**: Different thresholds for high/medium/low altitude
2. **Horizontal velocity management**: Brake when moving too fast sideways
3. **Emergency navigation**: Hover and navigate if low but not over landing zone
4. **Hysteresis**: Prevent rapid thrust toggling with dead zones
5. **Rotation control**: Tilt to navigate or brake, stay upright for landing

#### AI Challenges
- **Horizontal velocity**: Easy to build up speed, hard to brake
- **Fuel management**: Must balance speed control with fuel conservation
- **Landing zone navigation**: Must reach target before descending too low
- **Timing**: Must start braking early enough to slow down

## Development Process

### Phase 1: Core Infrastructure (Tasks 1-3)
1. **Project setup**: Monorepo, Python venv, FastAPI, basic HTML
2. **Physics engine**: Lander class, terrain generation, collision detection
3. **WebSocket server**: 60Hz game loop, session management, telemetry streaming

**Key Decisions**:
- Chose FastAPI for async/WebSocket support
- Implemented physics tests early to validate behavior
- Used asyncio for concurrent game loop and message handling

### Phase 2: Client Implementation (Tasks 4-6)
4. **Firebase placeholder**: Auth structure ready for credentials
5. **Canvas renderer**: 60fps rendering, camera system, HUD with color indicators
6. **Client integration**: WebSocket client, keyboard input, full gameplay loop

**Key Decisions**:
- Vanilla JavaScript (no framework) for simplicity
- Color-coded HUD for instant visual feedback
- requestAnimationFrame for smooth rendering

**Challenges Solved**:
- Input state tracking (class variables vs instance variables bug)
- WebSocket message handling (parallel tasks for game loop and input)
- Rotation wrapping (normalization to -π to π)
- Lander rendering position (bottom at y, not center)

### Phase 3: AI Development (Task 11 partial)
- **AI client example**: Working autonomous landing
- **Telemetry enhancement**: Added calculated altitude and speed
- **AI strategy refinement**: Altitude-based control, horizontal braking, emergency navigation

**Challenges Solved**:
- Altitude calculation (terrain height vs screen top)
- Rapid thrust toggling (hysteresis)
- Horizontal velocity control (tilt to brake)
- Landing zone navigation (hover if off-target at low altitude)

### Phase 4: Spectator & Replay (Tasks 9-10)
9. **Replay recording**: Frame capture, metadata, compression, REST API
10. **Spectator mode**: Live viewing, multiple spectators, mid-game join

**Key Decisions**:
- Broadcast telemetry to spectators (same data as player)
- Send current state on spectator join (mid-game support)
- In-memory replay storage (fast, can extend to database)

**Challenges Solved**:
- Spectator black screen (needed to send init state immediately)
- Broadcast to multiple connections (iterate spectator list)
- Replay storage (finalize on game end, save before session cleanup)

### Phase 5: UI/UX Polish
- **Menu system**: Play/Spectate/Replay mode selection
- **Active games list**: Show running games with metadata
- **Replay list**: Show recorded games with results
- **Mode indicator**: Visual feedback for current mode
- **ESC to menu**: Easy navigation

## Technical Challenges & Solutions

### Challenge 1: Input State Not Updating
**Problem**: Thrust and rotation commands received but not applied to lander.

**Root Cause**: `current_thrust` and `current_rotate` were class variables instead of instance variables, shared across all sessions.

**Solution**: Moved to `__init__` as instance variables.

**Learning**: Python class variables are shared, instance variables are per-object.

### Challenge 2: WebSocket Timeout
**Problem**: WebSocket connections closing with "keepalive ping timeout".

**Root Cause**: Game loop and message handling competing for WebSocket, timeout too short (0.1s).

**Solution**: Created parallel async tasks for game loop and message handling.

**Learning**: Use `asyncio.create_task()` for concurrent operations, don't block WebSocket receive.

### Challenge 3: Rotation Angle Wrapping
**Problem**: Lander rotation reaching 1799° causing incorrect collision detection.

**Root Cause**: Rotation accumulating without bounds.

**Solution**: Normalize rotation to -π to π range every frame.

**Learning**: Always normalize angular values in physics simulations.

### Challenge 4: AI Rapid Thrust Toggling
**Problem**: AI toggling thrust on/off every frame around speed threshold.

**Root Cause**: Speed oscillating around 3.0 m/s threshold (3.0 vs 3.1).

**Solution**: Implemented hysteresis (turn on at 3.5, turn off at 2.5).

**Learning**: Use dead zones for threshold-based control systems.

### Challenge 5: AI Crashing Off Landing Zone
**Problem**: AI hovering at low altitude but 75 pixels away from landing zone, then crashing.

**Root Cause**: AI only controlled vertical descent, not horizontal navigation at low altitude.

**Solution**: Added emergency navigation logic (hover and navigate if low and off-target).

**Learning**: Multi-objective control requires priority system.

### Challenge 6: Spectator Black Screen
**Problem**: Spectators connecting to game but seeing black screen.

**Root Cause**: Spectators joining mid-game didn't receive initial terrain/lander state.

**Solution**: Send current game state immediately when spectator connects.

**Learning**: Late joiners need current state, not just future updates.

## Performance Characteristics

### Server
- **Game loop**: 60Hz (16.67ms per frame)
- **Physics update**: < 1ms per frame
- **Telemetry broadcast**: < 1ms per frame per connection
- **Concurrent games**: Limited by CPU (each game is async task)

### Client
- **Rendering**: 60fps via requestAnimationFrame
- **WebSocket latency**: ~16ms (one frame delay)
- **Memory**: Minimal (no replay storage in client)

### Network
- **Telemetry size**: ~500 bytes per message
- **Bandwidth per game**: ~30 KB/s (60 messages/s × 500 bytes)
- **Spectator overhead**: +30 KB/s per spectator

## Future Enhancements

### Immediate (Tasks 7-8, 12-13)
1. **Scoring system**: Calculate score based on time, fuel, inputs, difficulty
2. **Firebase leaderboards**: Persistent storage, human vs AI categories
3. **Difficulty selection UI**: Choose terrain difficulty before game
4. **Error handling**: Reconnection logic, better error messages
5. **Authentication UI**: Login/register with Firebase

### Medium Term
1. **Replay playback**: Store terrain in replay, implement playback controls
2. **AI tournament mode**: Multiple AIs compete on same terrain
3. **Terrain editor**: Custom terrain creation and sharing
4. **Advanced AI metrics**: Path efficiency, fuel efficiency scoring
5. **Mobile support**: Touch controls for human players

### Long Term
1. **Multiplayer racing**: Multiple landers on same terrain
2. **Procedural challenges**: Daily/weekly challenge terrains
3. **AI training mode**: Provide training API for reinforcement learning
4. **3D rendering**: Three.js for visual enhancement
5. **Sound effects**: Engine sounds, crash/landing audio

## Lessons Learned

### What Worked Well
1. **Server-authoritative physics**: Eliminated sync issues, simplified replay
2. **60Hz telemetry**: Sufficient for both smooth visuals and AI decision-making
3. **Monorepo**: Easy to keep server/client in sync
4. **Early testing**: Physics tests caught issues before integration
5. **Incremental development**: Each task built on previous work

### What Could Be Improved
1. **Terrain in replay**: Should have stored terrain data from the start
2. **Type safety**: TypeScript for client would catch errors earlier
3. **Configuration**: Game constants should be in config file
4. **Database**: In-memory storage limits scalability
5. **Testing**: Need integration tests for WebSocket communication

### Key Takeaways
1. **Real-time systems need careful async design**: Parallel tasks, not blocking
2. **Physics simulation requires normalization**: Angles, velocities need bounds
3. **Control systems need hysteresis**: Prevent oscillation around thresholds
4. **Late joiners need current state**: Not just future updates
5. **AI development is iterative**: Start simple, add complexity as needed

## Project Statistics

- **Development Time**: ~6 hours
- **Lines of Code**: ~2,137 (24 files)
- **Languages**: Python (server), JavaScript (client)
- **Dependencies**: 6 Python packages, 0 JavaScript packages
- **API Endpoints**: 4 REST, 2 WebSocket
- **Game Modes**: 3 (Play, Spectate, Replay)
- **Physics Update Rate**: 60Hz
- **Telemetry Rate**: 60Hz
- **Render Rate**: 60fps

## Conclusion

This project successfully demonstrates a modern approach to classic game development with AI integration. The server-authoritative architecture ensures fairness, the WebSocket API provides rich telemetry for AI development, and the spectator/replay systems enable analysis and entertainment.

The modular design allows for easy extension - new AI strategies, terrain generators, scoring systems, and game modes can be added without major refactoring. The comprehensive telemetry and replay system provide excellent tools for AI development and debugging.

The project serves as both a playable game and a platform for AI experimentation, achieving its dual goals of entertainment and education.

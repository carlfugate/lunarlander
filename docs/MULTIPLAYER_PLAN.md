# Multiplayer Implementation Plan

## Overview
Add multiplayer functionality to Lunar Lander, allowing 2-8 players to compete simultaneously on the same terrain.

## Architecture Decisions

### Shared Terrain
- **Decision:** All players in a room share the same terrain
- **Why:** Reuses existing generation, fair competition, simpler synchronization
- **Implementation:** Generate once per room, broadcast to all players on join

### Synchronization Approach
- **Server-Authoritative:** Physics simulation runs on server (already implemented)
- **Client Prediction:** Clients predict their own lander movement for responsiveness
- **Server Reconciliation:** Server sends authoritative state, clients adjust if needed
- **Broadcast Rate:** 60Hz game state updates (existing rate)

### Room-Based Sessions
- **Capacity:** 2-8 players per room
- **Lifecycle:** Lobby → Ready → Playing → Results → Lobby
- **Spectators:** Existing spectate mode works for multiplayer rooms

## Implementation Phases

### Phase 1: Core Multiplayer Foundation (Week 1-2)
**Goal:** Multiple players can connect to same game session

**Server Changes:**
- Extend `GameSession` class to support multiple players
  - `players: Dict[player_id, PlayerState]` instead of single lander
  - Track each player's lander, fuel, status independently
- Add `Room` class for session management
  - Room ID, player list, ready states, game state
- Modify WebSocket handlers
  - `join_room(room_id)` message type
  - Broadcast player join/leave to room
  - Send all player states in telemetry

**Client Changes:**
- Modify renderer to draw multiple landers
  - Different colors per player
  - Player name labels above landers
- Update state management for multi-player data
- Add player list UI component

**Deliverable:** 2+ players can see each other flying simultaneously

---

### Phase 2: Lobby System (Week 3)
**Goal:** Players can create/join rooms and ready up

**Server Changes:**
- Add room management endpoints
  - `GET /rooms` - List available rooms
  - `POST /rooms` - Create new room
  - Room metadata: name, player count, difficulty, status
- Add ready state tracking
  - All players must ready before game starts
- Auto-start when all ready

**Client Changes:**
- Create lobby UI screen
  - Room browser (list of available rooms)
  - Create room dialog (name, difficulty, max players)
  - Join room button
- Room waiting screen
  - Player list with ready indicators
  - Ready/Unready button
  - Start countdown when all ready

**Deliverable:** Full lobby experience with room creation/joining

---

### Phase 3: Simultaneous Gameplay (Week 4-5)
**Goal:** Smooth multiplayer gameplay with prediction

**Server Changes:**
- Independent physics simulation per player
  - Each player has own lander state
  - Collision detection per player
  - Track landed/crashed status individually
- Broadcast optimizations
  - Delta compression (only send changed values)
  - Player culling (only send nearby players if needed)
- Handle player disconnects gracefully
  - Mark as disconnected, keep ghost lander
  - Remove after 30s timeout

**Client Changes:**
- Client-side prediction
  - Predict own lander movement locally
  - Apply inputs immediately for responsiveness
  - Reconcile with server state on mismatch
- Interpolation for other players
  - Smooth movement between server updates
  - Handle latency gracefully
- Enhanced HUD
  - Mini-map showing all players
  - Player rankings (by altitude/fuel/status)

**Deliverable:** Smooth multiplayer gameplay with good netcode

---

### Phase 4: Scoring & Leaderboards (Week 6)
**Goal:** Competitive scoring and rankings

**Server Changes:**
- Scoring system
  - Landing accuracy (distance from zone center)
  - Fuel efficiency (remaining fuel)
  - Time bonus (faster landing)
  - Crash penalty
- Results calculation
  - Rank players by score
  - Store match results
- Simple leaderboard
  - In-memory top 100 scores
  - Optional: Persist to database later

**Client Changes:**
- Results screen
  - Player rankings with scores
  - Breakdown of score components
  - "Play Again" / "Leave Room" buttons
- Leaderboard UI
  - Top players list
  - Personal best display

**Deliverable:** Complete competitive multiplayer experience

---

## Technical Details

### Message Protocol Extensions

**New Client → Server Messages:**
```javascript
{ type: "create_room", name: "Room Name", difficulty: "medium", max_players: 4 }
{ type: "join_room", room_id: "abc123" }
{ type: "leave_room" }
{ type: "ready", ready: true }
```

**New Server → Client Messages:**
```javascript
{ type: "room_list", rooms: [...] }
{ type: "room_joined", room_id: "abc123", players: [...] }
{ type: "player_joined", player_id: "xyz", name: "Player" }
{ type: "player_left", player_id: "xyz" }
{ type: "player_ready", player_id: "xyz", ready: true }
{ type: "game_starting", countdown: 3 }
{ type: "game_results", rankings: [...] }
```

**Modified Telemetry Message:**
```javascript
{
  type: "telemetry",
  players: {
    "player1": { x, y, vx, vy, rotation, fuel, crashed, landed },
    "player2": { ... }
  },
  terrain: { ... }
}
```

### Data Structures

**Room:**
```python
class Room:
    room_id: str
    name: str
    difficulty: str
    max_players: int
    players: Dict[str, Player]
    status: str  # "lobby", "playing", "results"
    terrain: Terrain
    game_session: GameSession
```

**Player:**
```python
class Player:
    player_id: str
    name: str
    websocket: WebSocket
    ready: bool
    lander: LanderState
    score: int
```

### Rendering Multiple Landers

**Color Palette:**
- Player 1: White (current)
- Player 2: Cyan
- Player 3: Yellow
- Player 4: Magenta
- Player 5: Green
- Player 6: Orange
- Player 7: Purple
- Player 8: Red

**Label Rendering:**
```javascript
// Above each lander
ctx.fillStyle = playerColor;
ctx.fillText(playerName, x, y - 40);
```

## Testing Strategy

### Phase 1 Testing
- 2 players connect and see each other
- Player disconnect handling
- Multiple rooms simultaneously

### Phase 2 Testing
- Create/join/leave rooms
- Ready state synchronization
- Auto-start when all ready

### Phase 3 Testing
- Latency simulation (50ms, 100ms, 200ms)
- Packet loss handling
- Prediction accuracy
- 8 players simultaneously

### Phase 4 Testing
- Score calculation correctness
- Leaderboard updates
- Results screen display

## Rollout Plan

1. **Phase 1:** Merge to master after testing with 2-4 players
2. **Phase 2:** Merge lobby system, enable room creation
3. **Phase 3:** Merge gameplay improvements incrementally
4. **Phase 4:** Merge scoring as final piece

Each phase is independently shippable and adds value.

## Future Enhancements (Post-MVP)

- Private rooms with passwords
- Team mode (2v2, 3v3)
- Custom terrain editor
- Tournament brackets
- Voice chat integration
- Replay sharing for multiplayer matches
- Persistent user accounts
- ELO ranking system
- Achievements/badges

## Success Metrics

- **Phase 1:** 2+ players can play simultaneously without crashes
- **Phase 2:** Players can create/join rooms in <5 seconds
- **Phase 3:** <100ms input latency, smooth 60fps gameplay
- **Phase 4:** Complete match with scoring in <5 minutes

## Timeline Estimate

- **Phase 1:** 2 weeks
- **Phase 2:** 1 week
- **Phase 3:** 2 weeks
- **Phase 4:** 1 week

**Total:** 6 weeks for full multiplayer implementation

---

**Status:** Planning Complete ✅  
**Next Step:** Begin Phase 1 implementation

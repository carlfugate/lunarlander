from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
import uuid
import time
import asyncio
from game.session import GameSession
try:
    from firebase_config import verify_token
    FIREBASE_ENABLED = True
except:
    FIREBASE_ENABLED = False
    print("⚠ Firebase not configured - authentication disabled")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions and replays
sessions = {}
replays = {}  # In-memory replay storage (would use database in production)

# Security limits
MAX_SESSIONS = 100
MAX_SPECTATORS_PER_GAME = 100
MAX_REPLAYS = 500
SESSION_TIMEOUT = 600  # 10 minutes

def cleanup_stale_sessions():
    """Remove sessions that have been idle for too long"""
    current_time = time.time()
    stale_sessions = []
    
    for session_id, session in sessions.items():
        if not session.running and session.start_time:
            idle_time = current_time - session.start_time
            if idle_time > SESSION_TIMEOUT:
                stale_sessions.append(session_id)
    
    for session_id in stale_sessions:
        print(f"Removing stale session: {session_id}")
        del sessions[session_id]
    
    return len(stale_sessions)

@app.get("/health")
async def health():
    return {"status": "ok", "firebase_enabled": FIREBASE_ENABLED}

@app.get("/games")
@limiter.limit("30/minute")
async def list_active_games(request: Request):
    """List all active game sessions"""
    # Cleanup stale sessions
    cleanup_stale_sessions()
    
    games = []
    for session_id, session in sessions.items():
        games.append({
            "session_id": session_id,
            "user_id": session.user_id,
            "difficulty": session.difficulty,
            "spectators": len(session.spectators),
            "duration": time.time() - session.start_time if session.start_time else 0
        })
    return {"games": games}

@app.get("/rooms")
@limiter.limit("30/minute")
async def list_active_rooms(request: Request):
    """List all active rooms with at least 1 player"""
    cleanup_stale_sessions()
    
    rooms = []
    for session_id, session in sessions.items():
        player_count = len(session.players)
        if player_count > 0:
            status = "waiting" if session.waiting else "playing"
            rooms.append({
                "id": session_id,
                "name": f"Room {session_id[:8]}",
                "player_count": player_count,
                "max_players": 8,
                "difficulty": session.difficulty,
                "status": status
            })
    return rooms

@app.websocket("/spectate/{session_id}")
async def spectate_game(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        if session_id not in sessions:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Game session not found"
            }))
            await websocket.close()
            return
            
        session = sessions[session_id]
        
        # Check spectator limit
        if len(session.spectators) >= MAX_SPECTATORS_PER_GAME:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Spectator limit reached"
            }))
            await websocket.close()
            return
        
        session.spectators.append(websocket)
        print(f"Spectator joined session {session_id} (total: {len(session.spectators)})")
        
        # Send current game state to spectator immediately
        init_message = {
            "type": "init",
            "terrain": session.terrain.to_dict(),
            "lander": session.lander.to_dict(),
            "spectator_count": len(session.spectators),
            "constants": {
                "gravity": 1.62,
                "thrust_power": 5.0,
                "rotation_speed": 3.0,
                "fuel_consumption_rate": 10.0,
                "max_landing_speed": 5.0,
                "max_landing_angle": 0.3,
                "terrain_width": 1200,
                "terrain_height": 800
            }
        }
        await websocket.send_text(json.dumps(init_message))
        
        # Keep connection alive
        while session.running:
            try:
                # Handle spectator messages (like ping)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                continue
            except:
                break
                
    except Exception as e:
        print(f"Spectator error: {e}")
    finally:
        if session_id in sessions and websocket in sessions[session_id].spectators:
            sessions[session_id].spectators.remove(websocket)
            print(f"Spectator left session {session_id} (remaining: {len(sessions[session_id].spectators)})")

@app.get("/replays")
@limiter.limit("30/minute")
async def list_replays(request: Request):
    """List all available replays"""
    replay_list = []
    for replay_id, replay_data in replays.items():
        metadata = replay_data['metadata']
        replay_list.append({
            "replay_id": replay_id,
            "user_id": metadata.get('user_id'),
            "difficulty": metadata.get('difficulty'),
            "duration": metadata.get('duration'),
            "landed": metadata.get('landed'),
            "crashed": metadata.get('crashed'),
            "timestamp": metadata.get('start_time')
        })
    # Sort by timestamp, newest first
    replay_list.sort(key=lambda x: x['timestamp'], reverse=True)
    return {"replays": replay_list}

@app.get("/replay/{replay_id}")
@limiter.limit("60/minute")
async def get_replay(replay_id: str, request: Request):
    """Get a specific replay"""
    if replay_id not in replays:
        return {"error": "Replay not found"}, 404
    return replays[replay_id]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Check session limit
    if len(sessions) >= MAX_SESSIONS:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Server at capacity. Please try again later."
        }))
        await websocket.close()
        return
    
    session_id = str(uuid.uuid4())
    session = None
    user_id = "anonymous"
    
    try:
        # Wait for start message (with optional auth)
        data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        
        # Validate message size
        if len(data) > 1024:  # 1KB limit
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Message too large"
            }))
            await websocket.close()
            return
        
        message = json.loads(data)
        
        # Validate message structure
        if not isinstance(message, dict) or "type" not in message:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid message format"
            }))
            await websocket.close()
            return
        
        # Optional authentication
        if FIREBASE_ENABLED and message.get("token"):
            auth_result = verify_token(message["token"])
            if not auth_result["success"]:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Authentication failed"
                }))
                await websocket.close()
                return
            user_id = auth_result["uid"]
        
        if message.get("type") == "start":
            difficulty = message.get("difficulty", "simple")
            telemetry_mode = message.get("telemetry_mode", "standard")
            update_rate = message.get("update_rate", 60)
            player_name = message.get("player_name", "Player")
            
            # Bot metadata (optional)
            bot_name = message.get("bot_name", None)
            bot_version = message.get("bot_version", None)
            bot_author = message.get("bot_author", None)
            
            # Validate difficulty
            if difficulty not in ["simple", "medium", "hard"]:
                difficulty = "simple"
            
            # Validate telemetry mode
            if telemetry_mode not in ["standard", "advanced"]:
                telemetry_mode = "standard"
            
            # Validate update rate (2-60 Hz)
            update_rate = max(2, min(60, int(update_rate)))
            
            session = GameSession(session_id, websocket, difficulty, telemetry_mode, update_rate)
            session.user_id = user_id
            session.bot_name = bot_name
            session.bot_version = bot_version
            session.bot_author = bot_author
            
            # Update default player name and ensure player is added
            session.players["default"]["name"] = player_name
            session.players["default"]["websocket"] = websocket
            
            sessions[session_id] = session
            
            # Send room_id back to client
            await websocket.send_text(json.dumps({
                "type": "room_created",
                "room_id": session_id
            }))
            
            # Send initial state
            await session.send_initial_state()
            
            # Start game loop in background
            game_task = asyncio.create_task(session.start())
            
            # Handle incoming messages in parallel
            async def handle_messages():
                while session.running:
                    try:
                        data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                        
                        # Validate message size
                        if len(data) > 1024:
                            print(f"Message too large from {session_id}")
                            break
                        
                        msg = json.loads(data)
                        
                        # Validate message structure
                        if not isinstance(msg, dict):
                            continue
                        
                        if msg.get("type") == "input":
                            action = msg.get("action")
                            # Validate action
                            if action in ["thrust", "thrust_on", "thrust_off", "rotate_left", "rotate_right", "rotate_stop"]:
                                session.handle_input(action, "default")
                            else:
                                print(f"Invalid action from {session_id}: {action}")
                        elif msg.get("type") == "start_game":
                            # Only room creator (default player) can start the game
                            if session.waiting:
                                session.start_game()
                                # Broadcast game_started to all players
                                start_message = {"type": "game_started"}
                                for pid, player in session.players.items():
                                    try:
                                        await player['websocket'].send_text(json.dumps(start_message))
                                    except:
                                        pass
                        elif msg.get("type") == "ping":
                            # Respond to ping with pong
                            await websocket.send_text(json.dumps({"type": "pong"}))
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {session_id}")
                        break
                    except Exception as e:
                        print(f"Message handling error: {e}")
                        break
            
            message_task = asyncio.create_task(handle_messages())
            
            # Wait for game to end
            await game_task
            message_task.cancel()
            
        elif message.get("type") == "join_room":
            room_id = message.get("room_id")
            player_name = message.get("player_name", "Player")
            
            if not room_id or room_id not in sessions:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Room not found"
                }))
                await websocket.close()
                return
            
            session = sessions[room_id]
            session_id = room_id
            
            # Color palette
            colors = ['#fff', '#0ff', '#ff0', '#f0f', '#0f0', '#f80', '#80f', '#f00']
            player_color = colors[len(session.players) % len(colors)]
            
            # Add player to session
            player_id = str(uuid.uuid4())
            session.add_player(player_id, websocket, player_name, player_color)
            
            # Broadcast player_joined to all players
            join_message = {
                "type": "player_joined",
                "player_id": player_id,
                "player_name": player_name,
                "player_color": player_color
            }
            
            for pid, player in session.players.items():
                try:
                    await player['websocket'].send_text(json.dumps(join_message))
                except:
                    pass
            
            # Send initial state to new player
            await session.send_initial_state()
            
            # No game loop needed - joining existing session
            game_task = None
            
            # Handle incoming messages in parallel
            async def handle_messages():
                current_player_id = "default"  # Default for room creators
                
                # Find current player ID for joiners
                for pid, player in session.players.items():
                    if player['websocket'] == websocket:
                        current_player_id = pid
                        break
                
                while session.running:
                    try:
                        data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                        
                        # Validate message size
                        if len(data) > 1024:
                            print(f"Message too large from {session_id}")
                            break
                        
                        msg = json.loads(data)
                        
                        # Validate message structure
                        if not isinstance(msg, dict):
                            continue
                        
                        if msg.get("type") == "input":
                            action = msg.get("action")
                            # Validate action
                            if action in ["thrust", "thrust_on", "thrust_off", "rotate_left", "rotate_right", "rotate_stop"]:
                                session.handle_input(action, current_player_id)
                            else:
                                print(f"Invalid action from {session_id}: {action}")
                        elif msg.get("type") == "start_game":
                            # Only room creator (default player) can start the game
                            if session.waiting and current_player_id == "default":
                                session.start_game()
                                # Broadcast game_started to all players
                                start_message = {"type": "game_started"}
                                for pid, player in session.players.items():
                                    try:
                                        await player['websocket'].send_text(json.dumps(start_message))
                                    except:
                                        pass
                        elif msg.get("type") == "ping":
                            # Respond to ping with pong
                            await websocket.send_text(json.dumps({"type": "pong"}))
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {session_id}")
                        break
                    except Exception as e:
                        print(f"Message handling error: {e}")
                        break
            
            if game_task:
                message_task = asyncio.create_task(handle_messages())
                
                # Wait for game to end
                await game_task
                message_task.cancel()
            else:
                # Just handle messages for joiners
                await handle_messages()
            
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if session_id in sessions:
            session = sessions[session_id]
            
            # Debug: Show all players before removal
            print(f"DEBUG - Players in session {session_id} before removal:")
            for pid, player in session.players.items():
                print(f"  Player {pid}: {player['name']} (websocket: {id(player['websocket'])})")
            print(f"  Disconnecting websocket: {id(websocket)}")
            
            # Find and remove disconnected player
            for pid, player in list(session.players.items()):
                if player['websocket'] == websocket:
                    disconnected_player_name = player['name']
                    print(f"DEBUG - Removing player {pid} ({disconnected_player_name})")
                    session.remove_player(pid)
                    print(f"DEBUG - Players remaining after removal: {len(session.players)}")
                    
                    # Broadcast player_left to remaining players
                    if session.players:
                        left_message = {
                            "type": "player_left",
                            "player_id": pid,
                            "player_name": disconnected_player_name
                        }
                        
                        for remaining_pid, remaining_player in session.players.items():
                            try:
                                await remaining_player['websocket'].send_text(json.dumps(left_message))
                            except:
                                pass
                    break
            else:
                print(f"DEBUG - No matching player found for websocket {id(websocket)} in session {session_id}")
            
            # Only delete session if no players left
            if session_id in sessions and not sessions[session_id].players:
                # Save replay before deleting session
                if session.replay:
                    replay_id = f"{session_id}_{int(time.time())}"
                    
                    # Enforce replay limit
                    if len(replays) >= MAX_REPLAYS:
                        # Remove oldest replay
                        oldest_id = min(replays.keys(), key=lambda k: replays[k]['metadata'].get('timestamp', 0))
                        del replays[oldest_id]
                        print(f"Removed oldest replay: {oldest_id}")
                    
                    replays[replay_id] = session.replay.to_dict()
                    print(f"Saved replay: {replay_id}")
                    print(f"Total replays in memory: {len(replays)}")
                else:
                    print(f"No replay to save for session {session_id}")
                del sessions[session_id]

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
import os
from game.session import GameSession
from metrics.live_stats import LiveStatsTracker
from metrics.analytics import AnalyticsEngine
from metrics.config import AnalyticsConfig

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

# Initialize live stats tracker
live_stats = LiveStatsTracker()

# Initialize analytics engine with conference config
analytics_config = AnalyticsConfig(
    default_window_hours=int(os.getenv('ANALYTICS_WINDOW_HOURS', 8)),
    cache_ttl_seconds=int(os.getenv('ANALYTICS_CACHE_TTL', 60)),
    infinite_mode=os.getenv('ANALYTICS_INFINITE_MODE', 'false').lower() == 'true'
)
analytics = AnalyticsEngine(config=analytics_config)

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
        # Remove finished games that are idle
        if not session.running and session.start_time:
            idle_time = current_time - session.start_time
            if idle_time > SESSION_TIMEOUT:
                stale_sessions.append(session_id)
        # Remove waiting rooms with no players
        elif session.waiting and len(session.players) == 0:
            stale_sessions.append(session_id)
    
    for session_id in stale_sessions:
        session = sessions[session_id]
        print(f"{session.get_session_info()} Removing stale session")
        del sessions[session_id]
    
    return len(stale_sessions)

@app.get("/health")
async def health():
    return {"status": "ok", "firebase_enabled": FIREBASE_ENABLED}

@app.post("/cleanup")
async def manual_cleanup():
    """Manually trigger session cleanup"""
    removed = cleanup_stale_sessions()
    return {"status": "ok", "sessions_removed": removed}

@app.get("/games")
@limiter.limit("30/minute")
async def list_active_games(request: Request):
    """List all active game sessions"""
    from fastapi.responses import JSONResponse
    cleanup_stale_sessions()
    
    games = []
    for session_id, session in sessions.items():
        player_count = len(session.players)
        games.append({
            "session_id": session_id,
            "user_id": session.user_id,
            "difficulty": session.difficulty,
            "spectators": len(session.spectators),
            "duration": time.time() - session.start_time if session.start_time else 0,
            "is_multiplayer": player_count > 1,
            "player_count": player_count
        })
    return JSONResponse(content={"games": games}, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/rooms")
@limiter.limit("30/minute")
async def list_active_rooms(request: Request):
    """List all active rooms with at least 1 player"""
    from fastapi.responses import JSONResponse
    cleanup_stale_sessions()
    
    rooms = []
    for session_id, session in sessions.items():
        player_count = len(session.players)
        if player_count > 0:
            status = "waiting" if session.waiting else "playing"
            rooms.append({
                "id": session_id,
                "name": session.room_name or session_id[:8],
                "player_count": player_count,
                "max_players": 8,
                "difficulty": session.difficulty,
                "status": status
            })
    return JSONResponse(content=rooms, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

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
        print(f"{session.get_session_info()} Spectator joined (total: {len(session.spectators)})")
        
        # Send current game state to spectator immediately
        init_message = {
            "type": "init",
            "terrain": session.terrain.to_dict(),
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
        
        # Check if multiplayer game and send appropriate data format
        if len(session.players) > 1:
            init_message['players'] = {pid: p['lander'].to_dict() for pid, p in session.players.items()}
        else:
            init_message['lander'] = session.lander.to_dict()
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
        print(f"{session.get_session_info()} Spectator error: {e}")
    finally:
        if session_id in sessions and websocket in sessions[session_id].spectators:
            session = sessions[session_id]
            session.spectators.remove(websocket)
            print(f"{session.get_session_info()} Spectator left (remaining: {len(session.spectators)})")

@app.get("/replays")
@limiter.limit("30/minute")
async def list_replays(request: Request):
    """List all available replays"""
    from fastapi.responses import JSONResponse
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
    replay_list.sort(key=lambda x: x['timestamp'], reverse=True)
    return JSONResponse(content={"replays": replay_list}, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/replay/{replay_id}")
@limiter.limit("60/minute")
async def get_replay(replay_id: str, request: Request):
    """Get a specific replay"""
    if replay_id not in replays:
        return {"error": "Replay not found"}, 404
    return replays[replay_id]

@app.get("/api/stats/live")
@limiter.limit("120/minute")
async def get_live_stats(request: Request):
    """Get real-time statistics"""
    return live_stats.get_stats()

@app.get("/api/stats/aggregate")
@limiter.limit("60/minute")
async def get_aggregate_stats(request: Request, hours: int = None):
    """
    Get aggregate statistics
    
    Args:
        hours: Time window in hours (default: 8 for conference day)
               Use 0 for infinite mode
    """
    if hours == 0:
        # Infinite mode
        analytics.config.infinite_mode = True
        stats = analytics.get_aggregate_stats()
        analytics.config.infinite_mode = False
    else:
        stats = analytics.get_aggregate_stats(hours)
    
    return stats

@app.get("/api/stats/trending")
@limiter.limit("120/minute")
async def get_trending_stats(request: Request):
    """Get trending statistics (last hour vs previous)"""
    return analytics.get_trending_stats()

@app.get("/api/stats/recent")
@limiter.limit("120/minute")
async def get_recent_activity(request: Request, minutes: int = 5):
    """
    Get recent activity
    
    Args:
        minutes: Time window in minutes (default: 5)
    """
    return analytics.get_recent_activity(minutes)

@app.get("/api/stats/fun-facts")
@limiter.limit("60/minute")
async def get_fun_facts(request: Request, hours: int = None):
    """
    Get fun facts for presentation
    
    Args:
        hours: Time window in hours (default: 8)
    """
    return analytics.get_fun_facts(hours)

@app.get("/api/stats/config")
async def get_analytics_config():
    """Get current analytics configuration"""
    return {
        'default_window_hours': analytics.config.default_window_hours,
        'cache_ttl_seconds': analytics.config.cache_ttl_seconds,
        'infinite_mode': analytics.config.infinite_mode,
        'recent_events_window': analytics.config.recent_events_window
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Track session start
    live_stats.session_started()
    
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
            fuel_mode = message.get("fuel_mode", "standard")
            
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
            
            # Validate fuel mode
            if fuel_mode not in ["standard", "unlimited", "limited", "challenge"]:
                fuel_mode = "standard"
            
            # Validate update rate (2-60 Hz)
            update_rate = max(2, min(60, int(update_rate)))
            
            session = GameSession(session_id, websocket, difficulty, telemetry_mode, update_rate, fuel_mode=fuel_mode)
            session.user_id = user_id
            session.bot_name = bot_name
            session.bot_version = bot_version
            session.bot_author = bot_author
            
            # Update default player name and ensure player is added
            session.players["default"]["name"] = player_name
            session.players["default"]["websocket"] = websocket
            
            sessions[session_id] = session
            session.waiting = False  # Single-player games start immediately
            
            # Send room_id back to client
            await websocket.send_text(json.dumps({
                "type": "room_created",
                "room_id": session_id
            }))
            
            # Send current player list
            await session.send_player_list()
            
            # Send initial state
            try:
                await session.send_initial_state()
            except Exception as e:
                print(f"Error in send_initial_state: {e}")
                import traceback
                traceback.print_exc()
                raise
            
            # Start game loop in background (will wait until game starts)
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
                                # Send initial state now that game is starting
                                await session.send_initial_state()
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
            
        elif message.get("type") == "create_room":
            difficulty = message.get("difficulty", "simple")
            player_name = message.get("player_name", "Player")
            room_name = message.get('room_name', None)
            
            # Check for duplicate room name
            if room_name:
                duplicate = any(
                    session.room_name == room_name and session.waiting 
                    for session in sessions.values()
                )
                if duplicate:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Room name '{room_name}' already exists. Please choose a different name."
                    }))
                    return  # Exit the websocket handler
            
            # Validate difficulty
            if difficulty not in ["simple", "medium", "hard"]:
                difficulty = "simple"
            
            session = GameSession(session_id, websocket, difficulty, "standard", 60, room_name=room_name)
            session.user_id = user_id
            
            # Update default player name and ensure player is added
            session.players["default"]["name"] = player_name
            session.players["default"]["websocket"] = websocket
            
            sessions[session_id] = session
            # Keep session.waiting = True for multiplayer rooms
            
            
            # Send room_id back to client
            await websocket.send_text(json.dumps({
                "type": "room_created",
                "room_id": session_id
            }))
            
            # Send current player list
            await session.send_player_list()
            
            # DO NOT send initial state for multiplayer rooms - only send after start_game
            
            # Start game loop in background (will wait until game starts)
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
                                # Send initial state now that game is starting
                                await session.send_initial_state()
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
            
            # Send current player list to all players
            await session.send_player_list()
            
            # Send room_joined confirmation to joining player
            await websocket.send_text(json.dumps({
                'type': 'room_joined',
                'room_id': room_id,
                'room_name': session.room_name
            }))
            
            # Only send initial state if game has already started
            if not session.waiting:
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
                                # Send initial state now that game is starting
                                await session.send_initial_state()
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
        # Track session end
        live_stats.session_ended()
        
        if session_id in sessions:
            session = sessions[session_id]
            
            # Debug: Show all players before removal
            for pid, player in session.players.items():
                print(f"  Player {pid}: {player['name']} (websocket: {id(player['websocket'])})")
            print(f"  Disconnecting websocket: {id(websocket)}")
            
            # Find and remove disconnected player
            for pid, player in list(session.players.items()):
                if player['websocket'] == websocket:
                    disconnected_player_name = player['name']
                    session.remove_player(pid)
                    
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

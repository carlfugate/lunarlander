from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app = FastAPI()

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

@app.get("/health")
async def health():
    return {"status": "ok", "firebase_enabled": FIREBASE_ENABLED}

@app.get("/games")
async def list_active_games():
    """List all active game sessions"""
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
        session.spectators.append(websocket)
        print(f"Spectator joined session {session_id}")
        
        # Send current game state to spectator immediately
        init_message = {
            "type": "init",
            "terrain": session.terrain.to_dict(),
            "lander": session.lander.to_dict(),
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
                # Just wait for messages (spectators don't send input)
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except:
                break
                
    except Exception as e:
        print(f"Spectator error: {e}")
    finally:
        if session_id in sessions and websocket in sessions[session_id].spectators:
            sessions[session_id].spectators.remove(websocket)
            print(f"Spectator left session {session_id}")

@app.get("/replays")
async def list_replays():
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
async def get_replay(replay_id: str):
    """Get a specific replay"""
    if replay_id not in replays:
        return {"error": "Replay not found"}, 404
    return replays[replay_id]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    session = None
    user_id = "anonymous"
    
    try:
        # Wait for start message (with optional auth)
        data = await websocket.receive_text()
        message = json.loads(data)
        
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
            session = GameSession(session_id, websocket, difficulty)
            session.user_id = user_id
            sessions[session_id] = session
            
            # Send initial state
            await session.send_initial_state()
            
            # Start game loop in background
            import asyncio
            game_task = asyncio.create_task(session.start())
            
            # Handle incoming messages in parallel
            async def handle_messages():
                while session.running:
                    try:
                        data = await websocket.receive_text()
                        msg = json.loads(data)
                        if msg.get("type") == "input":
                            session.handle_input(msg.get("action"))
                    except Exception as e:
                        print(f"Message handling error: {e}")
                        break
            
            message_task = asyncio.create_task(handle_messages())
            
            # Wait for game to end
            await game_task
            message_task.cancel()
            
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if session_id in sessions:
            # Save replay before deleting session
            if session and session.replay:
                replay_id = f"{session_id}_{int(time.time())}"
                replays[replay_id] = session.replay.to_dict()
                print(f"Saved replay: {replay_id}")
                print(f"Total replays in memory: {len(replays)}")
            else:
                print(f"No replay to save for session {session_id}")
            del sessions[session_id]

#!/usr/bin/env python3
"""
Minimal WebSocket client for Lunar Lander
Extracted from bots/simple_bot.py for CLI use
"""
import asyncio
import websockets
import json
import aiohttp

class WebSocketClient:
    def __init__(self, uri="ws://localhost:8000"):
        self.uri = uri
        self.ws = None
        self.mode = None
        self.http_base = uri.replace("ws://", "http://").replace("/ws", "")
        
    async def connect(self, uri=None):
        """Connect to WebSocket server"""
        if uri:
            self.uri = uri
        self.ws = await websockets.connect(self.uri)
        
    async def start_game(self, difficulty="simple"):
        """Start game in play mode"""
        self.mode = "play"
        await self.ws.send(json.dumps({
            "type": "start",
            "difficulty": difficulty
        }))
        
    async def spectate(self, session_id):
        """Connect to spectate mode"""
        self.mode = "spectate"
        spectate_uri = f"{self.uri.replace('/ws', '')}/spectate/{session_id}"
        await self.connect(spectate_uri)
    
    async def fetch_games(self):
        """Fetch list of active games"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.http_base}/games") as resp:
                return await resp.json()
    
    async def fetch_replays(self):
        """Fetch list of replays"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.http_base}/replays") as resp:
                return await resp.json()
    
    async def fetch_replay(self, replay_id):
        """Fetch specific replay data"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.http_base}/replay/{replay_id}") as resp:
                return await resp.json()
        
    async def send_input(self, action):
        """Send input action (play mode only)"""
        if self.mode != "play":
            return
        await self.ws.send(json.dumps({
            "type": "input", 
            "action": action
        }))
        
    async def receive_message(self):
        """Receive next message"""
        message = await self.ws.recv()
        return json.loads(message)
        
    async def close(self):
        """Close connection"""
        if self.ws:
            await self.ws.close()
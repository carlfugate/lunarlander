import { WebSocketClient } from './websocket.js';
import config from './config.js';

export function showLobby() {
    const menuEl = document.getElementById('menu');
    menuEl.classList.remove('visible');
    menuEl.classList.add('hidden');
    document.getElementById('lobby').classList.remove('hidden');
    fetchRooms().then(rooms => renderRoomList(rooms));
}

export function hideLobby() {
    document.getElementById('lobby').classList.add('hidden');
    const menuEl = document.getElementById('menu');
    menuEl.classList.remove('hidden');
    menuEl.classList.add('visible');
}

export async function fetchRooms() {
    const response = await fetch(`${config.API_URL}/rooms`);
    return await response.json();
}

export function renderRoomList(rooms) {
    const roomList = document.getElementById('roomListContent');
    if (!roomList) return;
    
    roomList.innerHTML = '';
    
    if (rooms.length === 0) {
        roomList.innerHTML = '<div class="no-rooms">No active rooms available</div>';
        return;
    }
    
    rooms.forEach(room => {
        const roomItem = document.createElement('div');
        roomItem.className = 'room-item';
        roomItem.innerHTML = `
            <div class="room-name">${room.name || `Room ${room.id.substring(0, 8)}`}</div>
            <div class="room-info">${room.player_count}/${room.max_players} players - ${room.status}</div>
        `;
        roomItem.onclick = () => joinRoom(room.id);
        roomList.appendChild(roomItem);
    });
}

async function joinRoom(roomId) {
    console.log('Joining room:', roomId);
    
    const playerName = prompt('Enter your player name:') || 'Player';
    if (!playerName.trim()) return;
    
    try {
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        const wsClient = new WebSocketClient(wsUrl);
        
        await wsClient.connect();
        
        // Set up all game callbacks (matching single-player setup)
        wsClient.onInit = async (data) => {
            console.log('✓ Multiplayer game initialized');
            const { stateManager } = await import('./state.js');
            stateManager.setState({ terrain: data.terrain, lander: data.lander, thrusting: false });
            if (window.inputHandler) {
                window.inputHandler.wsClient = wsClient;
            }
            // Start the game loop
            if (window.startGameLoop) {
                window.startGameLoop();
            }
        };
        
        wsClient.onTelemetry = async (data) => {
            const { stateManager } = await import('./state.js');
            const stateUpdate = {
                terrain: data.terrain || stateManager.state.terrain,
                thrusting: data.thrusting || false,
                altitude: data.altitude || 0,
                speed: data.speed || 0,
                spectatorCount: data.spectator_count
            };
            
            if (data.players) {
                stateUpdate.players = data.players;
                stateUpdate.lander = null;
            } else {
                stateUpdate.lander = data.lander;
                stateUpdate.players = null;
            }
            
            stateManager.setState(stateUpdate);
        };
        
        wsClient.onGameOver = (data) => {
            const statusEl = document.getElementById('status');
            const result = data.landed ? 'LANDED!' : 'CRASHED!';
            const score = data.score || 0;
            const scoreText = data.landed ? `Score: ${score}` : '';
            const stats = `Time: ${data.time.toFixed(1)}s | Fuel: ${data.fuel_remaining.toFixed(0)} | Inputs: ${data.inputs}`;
            statusEl.innerHTML = `
                <div style="font-size: 24px;">${result}</div>
                ${scoreText ? `<div style="font-size: 20px; margin: 10px 0;">${scoreText}</div>` : ''}
                <div>${stats}</div>
                <div>Press R to restart | ESC for menu</div>
            `;
            statusEl.style.color = data.landed ? '#0f0' : '#f00';
            statusEl.style.borderColor = data.landed ? '#0f0' : '#f00';
            statusEl.classList.remove('hidden');
            statusEl.classList.add('visible');
        };
        
        await wsClient.joinRoom(roomId, playerName.trim());
        
        // Store wsClient globally for game loop access
        window.wsClient = wsClient;
        
        // Transition to game screen
        document.getElementById('lobby').style.display = 'none';
        document.getElementById('menu').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        document.getElementById('app').classList.remove('hidden');
        document.getElementById('modeIndicator').textContent = 'MULTIPLAYER';
        
        // Set current mode for game loop
        if (window.setCurrentMode) {
            window.setCurrentMode('play');
        }
        
        // Initialize game components
        if (!window.inputHandler && wsClient) {
            const { InputHandler } = await import('./input.js');
            window.inputHandler = new InputHandler(wsClient);
        }
        
        window.dispatchEvent(new Event('resize'));
        
    } catch (error) {
        console.error('Failed to join room:', error);
        alert('Failed to join room. Please try again.');
    }
}

async function createRoom(playerName) {
    try {
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        const wsClient = new WebSocketClient(wsUrl);
        
        await wsClient.connect();
        
        // Set up all game callbacks (matching single-player setup)
        wsClient.onInit = async (data) => {
            console.log('✓ Multiplayer game initialized');
            const { stateManager } = await import('./state.js');
            stateManager.setState({ terrain: data.terrain, lander: data.lander, thrusting: false });
            if (window.inputHandler) {
                window.inputHandler.wsClient = wsClient;
            }
            // Start the game loop
            if (window.startGameLoop) {
                window.startGameLoop();
            }
        };
        
        wsClient.onTelemetry = async (data) => {
            const { stateManager } = await import('./state.js');
            const stateUpdate = {
                terrain: data.terrain || stateManager.state.terrain,
                thrusting: data.thrusting || false,
                altitude: data.altitude || 0,
                speed: data.speed || 0,
                spectatorCount: data.spectator_count
            };
            
            if (data.players) {
                stateUpdate.players = data.players;
                stateUpdate.lander = null;
            } else {
                stateUpdate.lander = data.lander;
                stateUpdate.players = null;
            }
            
            stateManager.setState(stateUpdate);
        };
        
        wsClient.onGameOver = (data) => {
            const statusEl = document.getElementById('status');
            const result = data.landed ? 'LANDED!' : 'CRASHED!';
            const score = data.score || 0;
            const scoreText = data.landed ? `Score: ${score}` : '';
            const stats = `Time: ${data.time.toFixed(1)}s | Fuel: ${data.fuel_remaining.toFixed(0)} | Inputs: ${data.inputs}`;
            statusEl.innerHTML = `
                <div style="font-size: 24px;">${result}</div>
                ${scoreText ? `<div style="font-size: 20px; margin: 10px 0;">${scoreText}</div>` : ''}
                <div>${stats}</div>
                <div>Press R to restart | ESC for menu</div>
            `;
            statusEl.style.color = data.landed ? '#0f0' : '#f00';
            statusEl.style.borderColor = data.landed ? '#0f0' : '#f00';
            statusEl.classList.remove('hidden');
            statusEl.classList.add('visible');
        };
        
        await wsClient.createRoom(playerName);
        
        // Store wsClient globally for game loop access
        window.wsClient = wsClient;
        
        // Transition to game screen
        document.getElementById('lobby').style.display = 'none';
        document.getElementById('menu').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        document.getElementById('app').classList.remove('hidden');
        document.getElementById('modeIndicator').textContent = 'MULTIPLAYER';
        
        // Set current mode for game loop
        if (window.setCurrentMode) {
            window.setCurrentMode('play');
        }
        
        // Initialize game components
        if (!window.inputHandler && wsClient) {
            const { InputHandler } = await import('./input.js');
            window.inputHandler = new InputHandler(wsClient);
        }
        
        window.dispatchEvent(new Event('resize'));
        
    } catch (error) {
        console.error('Failed to create room:', error);
        alert('Failed to create room. Please try again.');
    }
}

// Event handlers
document.addEventListener('DOMContentLoaded', () => {
    const createBtn = document.getElementById('createRoomBtn');
    const joinBtn = document.getElementById('joinRoomBtn');
    const backBtn = document.getElementById('backFromLobby');
    const refreshBtn = document.getElementById('refreshRoomsBtn');
    
    if (createBtn) {
        createBtn.onclick = () => {
            const roomName = prompt('Enter room name:');
            if (roomName) {
                createRoom(roomName);
            }
        };
    }
    
    if (joinBtn) {
        joinBtn.onclick = () => {
            fetchRooms().then(rooms => renderRoomList(rooms));
        };
    }
    
    if (refreshBtn) {
        refreshBtn.onclick = () => {
            fetchRooms().then(rooms => renderRoomList(rooms));
        };
    }
    
    if (backBtn) {
        backBtn.onclick = hideLobby;
    }
});
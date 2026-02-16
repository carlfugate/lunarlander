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
        
        // Set up waiting lobby callbacks
        wsClient.onInit = async (data) => {
            console.log('✓ Joined room, showing waiting lobby');
            showWaitingLobby(wsClient, false, roomId); // false = not room creator
        };
        
        wsClient.onPlayerList = (data) => {
            updatePlayerList(data.players);
        };
        
        wsClient.onGameStarted = async () => {
            console.log('✓ Game started by room creator');
            await startMultiplayerGame(wsClient);
        };
        
        await wsClient.joinRoom(roomId, playerName.trim());
        
        // Store wsClient globally
        window.wsClient = wsClient;
        
    } catch (error) {
        console.error('Failed to join room:', error);
        alert('Failed to join room. Please try again.');
    }
}

function showCreateRoomModal() {
    const modal = document.getElementById('createRoomModal');
    const playerInput = document.getElementById('playerNameInput');
    const roomInput = document.getElementById('roomNameInput');
    
    // Clear previous values
    playerInput.value = '';
    roomInput.value = '';
    
    modal.classList.remove('hidden');
    playerInput.focus();
}

function hideCreateRoomModal() {
    document.getElementById('createRoomModal').classList.add('hidden');
}

async function createRoom(playerName, roomName) {
    try {
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        const wsClient = new WebSocketClient(wsUrl);
        
        await wsClient.connect();
        
        let roomId = null;
        
        // Set up waiting lobby callbacks
        wsClient.onInit = async (data) => {
            console.log('✓ Room created, showing waiting lobby');
            showWaitingLobby(wsClient, true, roomId); // true = is room creator
        };
        
        wsClient.onRoomCreated = (data) => {
            roomId = data.room_id;
        };
        
        wsClient.onPlayerList = (data) => {
            updatePlayerList(data.players);
        };
        
        wsClient.onGameStarted = async () => {
            console.log('✓ Game started by room creator');
            await startMultiplayerGame(wsClient);
        };
        
        await wsClient.createRoom(playerName);
        
        // Store wsClient globally
        window.wsClient = wsClient;
        
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
    
    // Modal elements
    const modal = document.getElementById('createRoomModal');
    const confirmBtn = document.getElementById('createRoomConfirm');
    const cancelBtn = document.getElementById('createRoomCancel');
    const playerInput = document.getElementById('playerNameInput');
    const roomInput = document.getElementById('roomNameInput');
    
    if (createBtn && !createBtn.onclick) {
        createBtn.onclick = () => {
            showCreateRoomModal();
        };
    }
    
    if (confirmBtn) {
        confirmBtn.onclick = () => {
            const playerName = playerInput.value.trim();
            const roomName = roomInput.value.trim();
            
            if (!playerName) {
                playerInput.focus();
                return;
            }
            if (!roomName) {
                roomInput.focus();
                return;
            }
            
            hideCreateRoomModal();
            createRoom(playerName, roomName);
        };
    }
    
    if (cancelBtn) {
        cancelBtn.onclick = hideCreateRoomModal;
    }
    
    // Handle Enter key in modal inputs
    if (playerInput) {
        playerInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                roomInput.focus();
            }
        });
    }
    
    if (roomInput) {
        roomInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                confirmBtn.click();
            }
        });
    }
    
    // Handle Escape key to close modal
    if (modal) {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                hideCreateRoomModal();
            }
        });
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

function showWaitingLobby(wsClient, isCreator, roomId) {
    // Hide lobby and menu
    document.getElementById('lobby').classList.add('hidden');
    document.getElementById('menu').classList.add('hidden');
    
    // Show waiting lobby
    const waitingLobby = document.getElementById('waitingLobby');
    waitingLobby.classList.remove('hidden');
    
    // Update room info
    document.getElementById('roomName').textContent = `Room: ${roomId ? roomId.substring(0, 8) : 'Loading...'}`;
    
    // Show/hide controls based on creator status
    const startBtn = document.getElementById('startGameBtn');
    const waitingMsg = document.getElementById('waitingMessage');
    
    if (isCreator) {
        startBtn.classList.remove('hidden');
        waitingMsg.classList.add('hidden');
    } else {
        startBtn.classList.add('hidden');
        waitingMsg.classList.remove('hidden');
    }
    
    // Add event listeners
    startBtn.onclick = () => {
        wsClient.send({ type: 'start_game' });
    };
    
    document.getElementById('leaveLobbyBtn').onclick = () => {
        wsClient.close();
        hideWaitingLobby();
        showLobby();
    };
}

function hideWaitingLobby() {
    const waitingLobby = document.getElementById('waitingLobby');
    if (waitingLobby) {
        waitingLobby.classList.add('hidden');
    }
}

function updatePlayerList(players) {
    const playerNames = document.getElementById('playerNames');
    if (!playerNames) return;
    
    playerNames.innerHTML = '';
    
    players.forEach(player => {
        const playerDiv = document.createElement('div');
        playerDiv.className = `player-item ${player.is_creator ? 'creator' : ''}`;
        playerDiv.textContent = player.name;
        playerNames.appendChild(playerDiv);
    });
}

async function startMultiplayerGame(wsClient) {
    hideWaitingLobby();
    
    // Set up game callbacks
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
    
    // Transition to game screen
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
        window.inputHandler.wsClient = wsClient;
    }
    
    // Initialize state manager
    const { stateManager } = await import('./state.js');
    stateManager.setState({ terrain: null, lander: null, players: null, thrusting: false });
    
    // Start the game loop
    if (window.startGameLoop) {
        window.startGameLoop();
    }
    
    window.dispatchEvent(new Event('resize'));
}
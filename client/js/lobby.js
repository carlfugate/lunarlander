import { WebSocketClient } from './websocket.js';
import { Renderer } from './renderer.js';
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
        wsClient.onRoomJoined = async (data) => {
            console.log('✓ Joined room, showing waiting lobby');
            showWaitingLobby(wsClient, false, roomId, null); // false = not room creator, no custom room name
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
        
        wsClient.onRoomCreated = (data) => {
            roomId = data.room_id;
            console.log('✓ Room created, showing waiting lobby');
            showWaitingLobby(wsClient, true, roomId, roomName);
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

function showWaitingLobby(wsClient, isCreator, roomId, roomName = null) {
    // Hide lobby and menu
    document.getElementById('lobby').classList.add('hidden');
    document.getElementById('menu').classList.add('hidden');
    
    // Show waiting lobby
    const waitingLobby = document.getElementById('waitingLobby');
    waitingLobby.classList.remove('hidden');
    
    // Update room info - show room name if available, otherwise show room ID
    const displayName = roomName || (roomId ? roomId.substring(0, 8) : 'Loading...');
    document.getElementById('roomName').textContent = `Room: ${displayName}`;
    
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
    
    // Add event listeners with debugging
    startBtn.onclick = () => {
        console.log('Start Game button clicked - sending start_game message');
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
    console.log('Starting multiplayer game...');
    hideWaitingLobby();
    
    // Initialize renderer like single-player does
    const canvas = document.getElementById('gameCanvas');
    if (!window.renderer) {
        window.renderer = new Renderer(canvas);
    }
    window.renderer.reset();
    
    let firstTelemetryReceived = false;
    
    // Set up game callbacks
    wsClient.onTelemetry = async (data) => {
        if (!firstTelemetryReceived) {
            console.log('First telemetry data received:', {
                players: data.players,
                terrain: data.terrain,
                dataKeys: Object.keys(data)
            });
            firstTelemetryReceived = true;
        }
        
        const { stateManager } = await import('./state.js');
        
        // Initialize terrain on first telemetry if available
        if (!stateManager.state.terrain && data.terrain) {
            stateManager.setState({ terrain: data.terrain });
        }
        
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
        
        // Render the updated state
        if (window.renderer) {
            window.renderer.render(stateManager.state, stateUpdate.thrusting);
        }
    };
    
    console.log('onTelemetry handler set up');
    
    wsClient.onGameOver = (data) => {
        const statusEl = document.getElementById('status');
        
        if (data.multiplayer && data.players_results) {
            // Multiplayer format - show all players' results
            let resultsHtml = '<div style="font-size: 24px; margin-bottom: 15px;">GAME OVER</div>';
            resultsHtml += '<div style="font-size: 18px; margin-bottom: 10px;">Results:</div>';
            
            // Sort players by score (winners first)
            const sortedResults = data.players_results.sort((a, b) => b.score - a.score);
            
            sortedResults.forEach((player, index) => {
                const isWinner = player.status === 'landed' && player.score > 0;
                const position = index + 1;
                const statusText = player.status === 'landed' ? 'LANDED' : 'CRASHED';
                const color = isWinner ? '#0f0' : (player.status === 'landed' ? '#ff0' : '#f00');
                
                resultsHtml += `
                    <div style="margin: 8px 0; padding: 5px; border: 1px solid ${color}; color: ${color};">
                        ${position}. ${player.player_name} - ${statusText}
                        <br>Score: ${player.score} | Fuel: ${player.fuel_remaining.toFixed(0)} | Time: ${player.time.toFixed(1)}s
                    </div>
                `;
            });
            
            resultsHtml += '<div style="margin-top: 15px;">Press R to restart | ESC for menu</div>';
            statusEl.innerHTML = resultsHtml;
            statusEl.style.color = '#fff';
            statusEl.style.borderColor = '#fff';
        } else {
            // Single-player format (backward compatible)
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
        }
        
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
        console.log('Game loop starting');
        window.startGameLoop();
    } else {
        console.log('Game loop NOT started - startGameLoop function not available');
    }
    
    window.dispatchEvent(new Event('resize'));
}
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
    
    rooms.forEach(room => {
        const roomItem = document.createElement('div');
        roomItem.className = 'room-item';
        roomItem.textContent = room.name;
        roomItem.onclick = () => joinRoom(room.id);
        roomList.appendChild(roomItem);
    });
}

function joinRoom(roomId) {
    console.log('Joining room:', roomId);
}

async function createRoom(playerName) {
    try {
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        const wsClient = new WebSocketClient(wsUrl);
        
        await wsClient.connect();
        
        // Set up game initialization callback
        wsClient.onInit = (data) => {
            console.log('✓ Multiplayer game initialized');
            // Initialize game UI components
            if (window.gameState) {
                window.gameState.terrain = data.terrain;
                window.gameState.lander = data.lander;
            }
            if (window.inputHandler) {
                window.inputHandler.wsClient = wsClient;
            }
        };
        
        await wsClient.createRoom(playerName);
        
        // Transition to game screen
        document.getElementById('lobby').style.display = 'none';
        document.getElementById('menu').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        document.getElementById('app').classList.remove('hidden');
        document.getElementById('modeIndicator').textContent = 'MULTIPLAYER';
        
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
    
    if (backBtn) {
        backBtn.onclick = hideLobby;
    }
});
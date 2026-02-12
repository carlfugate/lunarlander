import { Renderer } from './renderer.js';
import { WebSocketClient } from './websocket.js';
import { InputHandler } from './input.js';
import { ReplayPlayer } from './replay.js';

const canvas = document.getElementById('gameCanvas');
const renderer = new Renderer(canvas);
const statusEl = document.getElementById('status');
const menuEl = document.getElementById('menu');
const appEl = document.getElementById('app');
const modeIndicatorEl = document.getElementById('modeIndicator');

let gameState = { terrain: null, lander: null };
let inputHandler = null;
let gameActive = false;
let currentMode = null;

// Menu buttons
document.getElementById('playBtn').addEventListener('click', () => {
    menuEl.classList.add('hidden');
    appEl.classList.remove('hidden');
    currentMode = 'play';
    modeIndicatorEl.textContent = 'PLAYING';
    startGame();
});

document.getElementById('spectateBtn').addEventListener('click', async () => {
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('gameList').classList.remove('hidden');
    await loadActiveGames();
});

document.getElementById('replayBtn').addEventListener('click', async () => {
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('replayList').classList.remove('hidden');
    await loadReplays();
});

document.getElementById('backFromGames').addEventListener('click', () => {
    document.querySelector('.menu-buttons').classList.remove('hidden');
    document.getElementById('gameList').classList.add('hidden');
});

document.getElementById('backFromReplays').addEventListener('click', () => {
    document.querySelector('.menu-buttons').classList.remove('hidden');
    document.getElementById('replayList').classList.add('hidden');
});

async function loadActiveGames() {
    const response = await fetch('http://localhost:8000/games');
    const data = await response.json();
    const listEl = document.getElementById('gameListContent');
    
    if (data.games.length === 0) {
        listEl.innerHTML = '<p>No active games</p>';
        return;
    }
    
    listEl.innerHTML = data.games.map(game => `
        <div class="game-item" data-session-id="${game.session_id}">
            <div>Player: ${game.user_id}</div>
            <div>Difficulty: ${game.difficulty}</div>
            <div>Duration: ${game.duration.toFixed(0)}s | Spectators: ${game.spectators}</div>
        </div>
    `).join('');
    
    document.querySelectorAll('.game-item').forEach(item => {
        item.addEventListener('click', () => spectateGame(item.dataset.sessionId));
    });
}

async function loadReplays() {
    const response = await fetch('http://localhost:8000/replays');
    const data = await response.json();
    const listEl = document.getElementById('replayListContent');
    
    if (data.replays.length === 0) {
        listEl.innerHTML = '<p>No replays available</p>';
        return;
    }
    
    listEl.innerHTML = data.replays.map(replay => `
        <div class="replay-item" data-replay-id="${replay.replay_id}">
            <div>${replay.landed ? '✓ LANDED' : '✗ CRASHED'} - ${replay.user_id}</div>
            <div>Time: ${replay.duration.toFixed(1)}s | Difficulty: ${replay.difficulty}</div>
        </div>
    `).join('');
    
    document.querySelectorAll('.replay-item').forEach(item => {
        item.addEventListener('click', () => playReplay(item.dataset.replayId));
    });
}

function spectateGame(sessionId) {
    menuEl.classList.add('hidden');
    appEl.classList.remove('hidden');
    currentMode = 'spectate';
    modeIndicatorEl.textContent = 'SPECTATING';
    
    const wsUrl = `ws://${window.location.hostname}:8000/spectate/${sessionId}`;
    const wsClient = new WebSocketClient(wsUrl);
    
    wsClient.onInit = (data) => {
        gameState.terrain = data.terrain;
        gameState.lander = data.lander;
    };
    
    wsClient.onTelemetry = (data) => {
        gameState.lander = data.lander;
    };
    
    wsClient.onGameOver = (data) => {
        const result = data.landed ? 'LANDED!' : 'CRASHED!';
        statusEl.innerHTML = `<div style="font-size: 24px;">${result}</div><div>Press ESC for menu</div>`;
        statusEl.classList.add('visible');
    };
    
    wsClient.connect();
}

async function playReplay(replayId) {
    alert('Replay playback coming soon! For now, check console for replay data.');
    console.log('Replay ID:', replayId);
}

// Play mode WebSocket
const wsUrl = `ws://${window.location.hostname}:8000/ws`;
const wsClient = new WebSocketClient(wsUrl);

wsClient.onInit = (data) => {
    gameState.terrain = data.terrain;
    gameState.lander = data.lander;
    gameActive = true;
};

wsClient.onTelemetry = (data) => {
    gameState.lander = data.lander;
};

wsClient.onGameOver = (data) => {
    gameActive = false;
    const result = data.landed ? 'LANDED!' : 'CRASHED!';
    const stats = `Time: ${data.time.toFixed(1)}s | Fuel: ${data.fuel_remaining.toFixed(0)} | Inputs: ${data.inputs}`;
    statusEl.innerHTML = `<div style="font-size: 24px;">${result}</div><div>${stats}</div><div>Press R to restart | ESC for menu</div>`;
    statusEl.style.color = data.landed ? '#0f0' : '#f00';
    statusEl.style.borderColor = data.landed ? '#0f0' : '#f00';
    statusEl.classList.add('visible');
};

async function startGame(difficulty = 'simple') {
    try {
        statusEl.textContent = 'Connecting...';
        statusEl.classList.add('visible');
        await wsClient.connect();
        wsClient.startGame(difficulty);
        inputHandler = new InputHandler(wsClient);
        statusEl.classList.remove('visible');
    } catch (error) {
        statusEl.textContent = 'Failed to connect';
        statusEl.classList.add('visible');
    }
}

let lastFrameTime = 0;
function gameLoop(timestamp) {
    const thrusting = inputHandler ? inputHandler.isThrusting() : false;
    renderer.render(gameState, thrusting);
    requestAnimationFrame(gameLoop);
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
        if (!gameActive && currentMode === 'play') {
            wsClient.close();
            startGame();
        }
    }
    if (e.key === 'Escape') {
        wsClient.close();
        appEl.classList.add('hidden');
        menuEl.classList.remove('hidden');
        document.querySelector('.menu-buttons').classList.remove('hidden');
        document.getElementById('gameList').classList.add('hidden');
        document.getElementById('replayList').classList.add('hidden');
        statusEl.classList.remove('visible');
    }
});

requestAnimationFrame(gameLoop);

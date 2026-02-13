import { Renderer } from './renderer.js';
import { WebSocketClient } from './websocket.js';
import { InputHandler } from './input.js';
import { ReplayPlayer } from './replay.js';
import config from './config.js';

const canvas = document.getElementById('gameCanvas');
const renderer = new Renderer(canvas);
const statusEl = document.getElementById('status');
const menuEl = document.getElementById('menu');
const appEl = document.getElementById('app');
const modeIndicatorEl = document.getElementById('modeIndicator');

let gameState = { terrain: null, lander: null, thrusting: false, altitude: 0, speed: 0 };
let inputHandler = null;
let gameActive = false;
let currentMode = null;
let wsClient = null;
let animationFrameId = null;
let selectedDifficulty = 'simple';

// Menu buttons
document.getElementById('playBtn').addEventListener('click', () => {
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('difficultySelect').classList.remove('hidden');
});

// Difficulty selection
document.querySelectorAll('.difficulty-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        selectedDifficulty = btn.dataset.difficulty;
        stopGameLoop();
        menuEl.classList.add('hidden');
        appEl.classList.remove('hidden');
        appEl.style.display = 'block';
        menuEl.style.display = 'none';
        currentMode = 'play';
        modeIndicatorEl.textContent = 'PLAYING';
        window.dispatchEvent(new Event('resize'));
        startGame(selectedDifficulty);
    });
});

document.getElementById('backFromDifficulty').addEventListener('click', () => {
    document.getElementById('difficultySelect').classList.add('hidden');
    document.querySelector('.menu-buttons').classList.remove('hidden');
});

document.getElementById('spectateBtn').addEventListener('click', async () => {
    stopGameLoop();
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('gameList').classList.remove('hidden');
    await loadActiveGames();
});

document.getElementById('replayBtn').addEventListener('click', async () => {
    stopGameLoop();
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('replayList').classList.remove('hidden');
    await loadReplays();
});

document.getElementById('backFromGames').addEventListener('click', () => {
    stopGameLoop();
    document.querySelector('.menu-buttons').classList.remove('hidden');
    document.getElementById('gameList').classList.add('hidden');
});

document.getElementById('backFromReplays').addEventListener('click', () => {
    stopGameLoop();
    document.querySelector('.menu-buttons').classList.remove('hidden');
    document.getElementById('replayList').classList.add('hidden');
});

async function loadActiveGames() {
    const listEl = document.getElementById('gameListContent');
    listEl.innerHTML = '<p>Loading games...</p>';
    
    try {
        const response = await fetch(`${config.API_URL}/games`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.games.length === 0) {
            listEl.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <p style="font-size: 20px; margin-bottom: 10px;">No active games</p>
                    <p style="color: #888;">Start a new game to begin playing</p>
                </div>
            `;
            return;
        }
        
        listEl.innerHTML = '';
        data.games.forEach(game => {
            const gameItem = document.createElement('button');
            gameItem.className = 'game-item';
            gameItem.dataset.sessionId = game.session_id;
            gameItem.setAttribute('role', 'button');
            gameItem.setAttribute('aria-label', `Spectate ${game.user_id}'s game`);
            
            const playerDiv = document.createElement('div');
            playerDiv.textContent = `Player: ${game.user_id}`;
            
            const difficultyDiv = document.createElement('div');
            difficultyDiv.textContent = `Difficulty: ${game.difficulty}`;
            
            const statsDiv = document.createElement('div');
            statsDiv.textContent = `Duration: ${game.duration.toFixed(0)}s | Spectators: ${game.spectators}`;
            
            gameItem.appendChild(playerDiv);
            gameItem.appendChild(difficultyDiv);
            gameItem.appendChild(statsDiv);
            gameItem.addEventListener('click', () => spectateGame(game.session_id));
            
            listEl.appendChild(gameItem);
        });
    } catch (error) {
        console.error('Failed to load games:', error);
        listEl.innerHTML = '<p style="color: #f00;">Failed to load games. Please try again.</p>';
    }
}

async function loadReplays() {
    const listEl = document.getElementById('replayListContent');
    listEl.innerHTML = '<p>Loading replays...</p>';
    
    try {
        const response = await fetch(`${config.API_URL}/replays`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.replays.length === 0) {
            listEl.innerHTML = '<p>No replays available</p>';
            return;
        }
        
        listEl.innerHTML = '';
        data.replays.forEach(replay => {
            // Skip incomplete replays
            if (replay.duration === null || replay.landed === null) return;
            
            const replayItem = document.createElement('button');
            replayItem.className = 'replay-item';
            replayItem.dataset.replayId = replay.replay_id;
            replayItem.setAttribute('role', 'button');
            const status = replay.landed ? 'successful landing' : 'crash';
            replayItem.setAttribute('aria-label', `Watch ${replay.user_id}'s ${status} replay`);
            
            const statusDiv = document.createElement('div');
            const statusText = replay.landed ? '✓ LANDED' : '✗ CRASHED';
            statusDiv.textContent = `${statusText} - ${replay.user_id}`;
            
            const statsDiv = document.createElement('div');
            statsDiv.textContent = `Time: ${replay.duration.toFixed(1)}s | Difficulty: ${replay.difficulty}`;
            
            replayItem.appendChild(statusDiv);
            replayItem.appendChild(statsDiv);
            replayItem.addEventListener('click', () => playReplay(replay.replay_id));
            
            listEl.appendChild(replayItem);
        });
        
        // Show message if no valid replays
        if (listEl.children.length === 0) {
            listEl.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <p style="font-size: 20px; margin-bottom: 10px;">No completed replays</p>
                    <p style="color: #888;">Finish a game to create a replay</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load replays:', error);
        listEl.innerHTML = '<p style="color: #f00;">Failed to load replays. Please try again.</p>';
    }
}

let isConnecting = false;

function spectateGame(sessionId) {
    if (isConnecting) return;
    isConnecting = true;
    
    stopGameLoop();
    menuEl.classList.add('hidden');
    appEl.classList.remove('hidden');
    appEl.style.display = 'block';
    menuEl.style.display = 'none';
    currentMode = 'spectate';
    modeIndicatorEl.textContent = 'SPECTATING';
    window.dispatchEvent(new Event('resize'));
    
    const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/spectate/${sessionId}`;
    wsClient = new WebSocketClient(wsUrl);
    
    wsClient.onInit = (data) => {
        gameState.terrain = data.terrain;
        gameState.lander = data.lander;
        gameState.thrusting = false;
        startGameLoop();
        isConnecting = false;
    };
    
    wsClient.onTelemetry = (data) => {
        gameState.lander = data.lander;
        gameState.thrusting = data.thrusting || false;
        gameState.altitude = data.altitude || 0;
        gameState.speed = data.speed || 0;
        gameState.spectatorCount = data.spectator_count;
    };
    
    wsClient.onGameOver = (data) => {
        const result = data.landed ? 'LANDED!' : 'CRASHED!';
        const score = data.score || 0;
        const scoreText = data.landed ? `<div style="font-size: 20px; margin: 10px 0;">Score: ${score}</div>` : '';
        statusEl.innerHTML = `<div style="font-size: 24px;">${result}</div>${scoreText}<div>Press ESC for menu</div>`;
        statusEl.classList.add('visible');
    };
    
    wsClient.connect().catch(() => {
        isConnecting = false;
        statusEl.innerHTML = '<div style="color: #f00;">Failed to connect. Press ESC for menu.</div>';
        statusEl.classList.add('visible');
    });
}

let isLoadingReplay = false;

async function playReplay(replayId) {
    if (isLoadingReplay) return;
    isLoadingReplay = true;
    
    stopGameLoop();
    menuEl.classList.add('hidden');
    appEl.classList.remove('hidden');
    appEl.style.display = 'block';
    menuEl.style.display = 'none';
    currentMode = 'replay';
    modeIndicatorEl.textContent = 'REPLAY';
    window.dispatchEvent(new Event('resize'));
    
    try {
        // Fetch replay data
        const response = await fetch(`${config.API_URL}/replay/${replayId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const replayData = await response.json();
        
        // Set up game state with replay terrain
        gameState.terrain = replayData.metadata.terrain;
        gameState.lander = null;
        
        // Create replay player
        const replayPlayer = new ReplayPlayer(replayData);
        
        // Play the replay
        let frameIndex = 0;
        const playbackSpeed = 1.0; // 1x speed
        const frameDelay = (1000 / 30) / playbackSpeed; // 30Hz playback
        
        startGameLoop();
        isLoadingReplay = false;
        
        function replayLoop() {
            if (currentMode !== 'replay') return; // Stop if mode changed
            
            if (frameIndex >= replayData.frames.length) {
                statusEl.innerHTML = `<div style="font-size: 24px;">REPLAY ENDED</div><div>Press ESC for menu</div>`;
                statusEl.classList.add('visible');
                return;
            }
            
            const frame = replayData.frames[frameIndex];
            gameState.lander = frame.lander;
            gameState.altitude = frame.altitude || 0;
            gameState.speed = frame.speed || 0;
            gameState.thrusting = frame.thrusting || false;
            
            frameIndex++;
            setTimeout(() => requestAnimationFrame(replayLoop), frameDelay);
        }
        
        replayLoop();
    } catch (error) {
        console.error('Failed to load replay:', error);
        statusEl.innerHTML = '<p style="color: #f00;">Failed to load replay. Press ESC for menu.</p>';
        statusEl.classList.add('visible');
        isLoadingReplay = false;
    }
}

// Play mode WebSocket
async function startGame(difficulty = 'simple') {
    try {
        stopGameLoop();
        renderer.reset();
        statusEl.textContent = 'Connecting...';
        statusEl.classList.add('visible');
        
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        wsClient = new WebSocketClient(wsUrl);
        
        wsClient.onInit = (data) => {
            console.log('✓ Received init message:', data);
            gameState.terrain = data.terrain;
            gameState.lander = data.lander;
            gameState.thrusting = false;
            gameActive = true;
            statusEl.classList.remove('visible');
            startGameLoop();
            isConnecting = false;
        };
        
        wsClient.onTelemetry = (data) => {
            gameState.lander = data.lander;
            gameState.thrusting = data.thrusting || false;
            gameState.altitude = data.altitude || 0;
            gameState.speed = data.speed || 0;
            gameState.spectatorCount = data.spectator_count;
        };
        
        wsClient.onGameOver = (data) => {
            gameActive = false;
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
            statusEl.classList.add('visible');
        };
        
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
let lastRenderState = null;
let frameCount = 0;

function gameLoop(timestamp) {
    try {
        const thrusting = gameState.thrusting || (inputHandler ? inputHandler.isThrusting() : false);
        
        // Always render if there are particles or explosion (they animate)
        const hasAnimation = renderer.particles.length > 0 || renderer.explosion;
        
        // Only render if state changed OR animation is active
        const currentState = JSON.stringify({
            lander: gameState.lander,
            thrusting: thrusting,
            altitude: gameState.altitude,
            speed: gameState.speed
        });
        
        if (currentState !== lastRenderState || hasAnimation) {
            renderer.render(gameState, thrusting);
            lastRenderState = currentState;
        }
    } catch (e) {
        console.error("Error in game loop:", e);
    }
    
    // Only continue loop if in active mode
    if (currentMode === 'play' || currentMode === 'spectate' || currentMode === 'replay') {
        animationFrameId = requestAnimationFrame(gameLoop);
    }
}

function stopGameLoop() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

function startGameLoop() {
    if (!animationFrameId) {
        animationFrameId = requestAnimationFrame(gameLoop);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
        if (!gameActive && currentMode === 'play') {
            if (wsClient) wsClient.close();
            startGame();
        }
    }
    if (e.key === 'Escape') {
        stopGameLoop();
        if (wsClient) wsClient.close();
        if (inputHandler) {
            inputHandler = null;
        }
        currentMode = null;
        appEl.classList.add('hidden');
        menuEl.classList.remove('hidden');
        document.querySelector('.menu-buttons').classList.remove('hidden');
        document.getElementById('difficultySelect').classList.add('hidden');
        document.getElementById('gameList').classList.add('hidden');
        document.getElementById('replayList').classList.add('hidden');
        statusEl.classList.remove('visible');
        gameState = { terrain: null, lander: null, thrusting: false, altitude: 0, speed: 0 };
    }
});

startGameLoop();

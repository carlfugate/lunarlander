/**
 * @typedef {Object} Lander
 * @property {number} x - X position
 * @property {number} y - Y position
 * @property {number} vx - X velocity
 * @property {number} vy - Y velocity
 * @property {number} rotation - Rotation in degrees
 * @property {number} fuel - Remaining fuel
 */

/**
 * @typedef {Object} GameState
 * @property {Array<{x: number, y: number}>|null} terrain - Terrain points
 * @property {Lander|null} lander - Lander state
 * @property {boolean} thrusting - Is thrust active
 * @property {number} altitude - Current altitude
 * @property {number} speed - Current speed
 * @property {number} [spectatorCount] - Number of spectators
 */

/**
 * @typedef {Object} TelemetryData
 * @property {string} type - Message type
 * @property {Lander} lander - Lander state
 * @property {number} altitude - Altitude above ground
 * @property {number} speed - Current speed
 * @property {boolean} thrusting - Thrust status
 * @property {number} timestamp - Game timestamp
 * @property {number} [spectator_count] - Number of spectators
 * @property {Object} [nearest_landing_zone] - Nearest landing zone info
 */

/**
 * @typedef {Object} GameOverData
 * @property {string} type - Message type
 * @property {boolean} landed - Successfully landed
 * @property {boolean} crashed - Crashed
 * @property {number} time - Game duration
 * @property {number} fuel_remaining - Fuel left
 * @property {number} inputs - Number of inputs
 * @property {number} score - Final score
 * @property {string} replay_id - Replay identifier
 */

import { Renderer } from './renderer.js';
import { WebSocketClient } from './websocket.js';
import { InputHandler } from './input.js';
import { ReplayPlayer } from './replay.js';
import { MobileControls } from './mobile-controls.js';
import { DevTools } from './devtools.js';
import { logger } from './logger.js';
import { stateManager } from './state.js';
import { perfMonitor } from './performance.js';
import config from './config.js';
import * as lobby from './lobby.js';

const canvas = document.getElementById('gameCanvas');
const renderer = new Renderer(canvas);
const statusEl = document.getElementById('status');
const devTools = new DevTools();
const menuEl = document.getElementById('menu');

// Make perfMonitor globally available for WebSocket
window.perfMonitor = perfMonitor;

// Global helper function for joining rooms from console
window.joinRoom = async function(roomId, playerName = 'Player2') {
    try {
        stopGameLoop();
        renderer.reset();
        statusEl.textContent = 'Connecting...';
        statusEl.classList.add('visible');
        
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        wsClient = new WebSocketClient(wsUrl);
        
        wsClient.onInit = (data) => {
            console.log('Received init message:', data);
            stateManager.setState({ terrain: data.terrain, lander: data.lander, thrusting: false });
            gameActive = true;
            statusEl.classList.remove('visible');
            startGameLoop();
            isConnecting = false;
            console.log('Game loop started, gameState:', gameState);
        };
        
        wsClient.onTelemetry = (data) => {
            console.log('data.players exists:', !!data.players);
            console.log('data.lander exists:', !!data.lander);
            console.log('Setting mode:', data.players ? 'multiplayer' : 'single-player');
            
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
            devTools.update(gameState);
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
            statusEl.classList.remove('hidden');
            statusEl.classList.add('visible');
        };
        
        // Hide lobby and menu, show game
        document.getElementById('lobby').style.display = 'none';
        menuEl.classList.add('hidden');
        appEl.classList.remove('hidden');
        appEl.style.display = 'block';
        menuEl.style.display = 'none';
        currentMode = 'play';
        modeIndicatorEl.textContent = 'PLAYING';
        window.dispatchEvent(new Event('resize'));
        
        await wsClient.connect();
        await wsClient.joinRoom(roomId, playerName);
        inputHandler = new InputHandler(wsClient, () => isPaused);
        
        const isMobile = window.innerWidth <= 768 || 
                        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        devTools.setStatus('devWsStatus', 'Connected', 'ok');
        devTools.setText('devMobile', isMobile ? 'Yes' : 'No');
        devTools.setText('devDebugMode', localStorage.getItem('debug') === 'true' ? 'On' : 'Off');
        
        if (isMobile) {
            try {
                mobileControls = new MobileControls(wsClient);
                mobileControls.show();
                logger.info('Mobile controls initialized and shown');
            } catch (error) {
                console.error('Error initializing mobile controls:', error);
            }
        }
        
        console.log(`Joined room ${roomId} as ${playerName}`);
    } catch (error) {
        console.error('Failed to join room:', error);
        statusEl.textContent = 'Failed to connect';
        statusEl.classList.add('visible');
    }
};
const appEl = document.getElementById('app');
const modeIndicatorEl = document.getElementById('modeIndicator');

/** @type {InputHandler|null} */
let inputHandler = null;
/** @type {MobileControls|null} */
let mobileControls = null;
let gameActive = false;
let currentMode = null;
let wsClient = null;
let animationFrameId = null;
let selectedDifficulty = 'simple';
let isPaused = false;

// Menu buttons
document.getElementById('playBtn').addEventListener('click', () => {
    console.log('Play button clicked');
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('difficultySelect').classList.remove('hidden');
});

document.getElementById('multiplayerBtn').addEventListener('click', () => {
    lobby.showLobby();
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

document.getElementById('helpBtn').addEventListener('click', () => {
    document.querySelector('.menu-buttons').classList.add('hidden');
    document.getElementById('helpScreen').classList.remove('hidden');
});

document.getElementById('backFromHelp').addEventListener('click', () => {
    document.querySelector('.menu-buttons').classList.remove('hidden');
    document.getElementById('helpScreen').classList.add('hidden');
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

/**
 * Load list of active games for spectating
 * @returns {Promise<void>}
 */
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

/**
 * Load list of available replays
 * @returns {Promise<void>}
 */
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

/**
 * Start spectating a live game
 * @param {string} sessionId - Game session ID to spectate
 */
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
    
    // Lazy load spectate module
    import('./modes/spectate.js').then(({ startSpectate }) => {
        wsClient = startSpectate(
            sessionId,
            () => {
                startGameLoop();
                isConnecting = false;
            },
            (result, scoreText) => {
                console.log('Game over callback:', result, scoreText);
                statusEl.classList.remove('hidden');
                statusEl.innerHTML = `<div style="font-size: 24px;">${result}</div>${scoreText}<div>Press ESC for menu</div>`;
                statusEl.classList.add('visible');
                console.log('After update - classes:', statusEl.className);
            }
        );
    }).catch((error) => {
        console.error('Failed to load spectate module:', error);
        isConnecting = false;
        statusEl.innerHTML = '<div style="color: #f00;">Failed to load. Press ESC for menu.</div>';
        statusEl.classList.add('visible');
    });
}

let isLoadingReplay = false;

/**
 * Play a recorded replay
 * @param {string} replayId - Replay ID to play
 * @returns {Promise<void>}
 */
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
        // Lazy load replay module
        const { startReplay } = await import('./modes/replay.js');
        
        await startReplay(
            replayId,
            () => {
                startGameLoop();
                isLoadingReplay = false;
            },
            () => {
                statusEl.innerHTML = `<div style="font-size: 24px;">REPLAY ENDED</div><div>Press ESC for menu</div>`;
                statusEl.classList.add('visible');
            }
        );
    } catch (error) {
        console.error('Failed to load replay:', error);
        statusEl.innerHTML = '<p style="color: #f00;">Failed to load replay. Press ESC for menu.</p>';
        statusEl.classList.add('visible');
        isLoadingReplay = false;
    }
}

// Play mode WebSocket
/**
 * Start a new game with specified difficulty
 * @param {string} [difficulty='simple'] - Difficulty level (simple, medium, hard)
 * @returns {Promise<void>}
 */
async function startGame(difficulty = 'simple') {
    try {
        stopGameLoop();
        renderer.reset();
        statusEl.textContent = 'Connecting...';
        statusEl.classList.add('visible');
        
        const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/ws`;
        wsClient = new WebSocketClient(wsUrl);
        
        wsClient.onInit = (data) => {
            console.log('Received init message:', data);
            stateManager.setState({ terrain: data.terrain, lander: data.lander, thrusting: false });
            gameActive = true;
            statusEl.classList.remove('visible');
            startGameLoop();
            isConnecting = false;
            console.log('Game loop started, gameState:', gameState);
        };
        
        wsClient.onTelemetry = (data) => {
            console.log('data.players exists:', !!data.players);
            console.log('data.lander exists:', !!data.lander);
            console.log('Setting mode:', data.players ? 'multiplayer' : 'single-player');
            
            const stateUpdate = {
                terrain: data.terrain || stateManager.state.terrain,
                thrusting: data.thrusting || false,
                altitude: data.altitude || 0,
                speed: data.speed || 0,
                spectatorCount: data.spectator_count
            };
            
            // Multiplayer mode
            if (data.players) {
                stateUpdate.players = data.players;
                stateUpdate.lander = null;
            } 
            // Single player mode
            else {
                stateUpdate.lander = data.lander;
                stateUpdate.players = null;
            }
            
            stateManager.setState(stateUpdate);
            devTools.update(gameState);
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
            statusEl.classList.remove('hidden');
            statusEl.classList.add('visible');
        };
        
        await wsClient.connect();
        wsClient.startGame(difficulty);
        inputHandler = new InputHandler(wsClient, () => isPaused);
        
        // Show mobile controls on mobile devices or small screens
        const isMobile = window.innerWidth <= 768 || 
                        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        logger.debug('Mobile detection:', { isMobile, width: window.innerWidth, userAgent: navigator.userAgent });
        
        // Update dev tools
        devTools.setStatus('devWsStatus', 'Connected', 'ok');
        devTools.setText('devMobile', isMobile ? 'Yes' : 'No');
        devTools.setText('devDebugMode', localStorage.getItem('debug') === 'true' ? 'On' : 'Off');
        
        if (isMobile) {
            try {
                mobileControls = new MobileControls(wsClient);
                mobileControls.show();
                logger.info('Mobile controls initialized and shown');
            } catch (error) {
                console.error('Error initializing mobile controls:', error);
            }
        }
        
        statusEl.classList.remove('visible');
    } catch (error) {
        statusEl.textContent = 'Failed to connect';
        statusEl.classList.add('visible');
    }
}

let lastFrameTime = 0;
let lastRenderState = null;

function gameLoop(timestamp) {
    try {
        // Update performance monitor
        perfMonitor.update(timestamp);
        
        // Skip rendering if paused (but keep loop running)
        if (!isPaused) {
            const thrusting = stateManager.state.thrusting || (inputHandler ? inputHandler.isThrusting() : false);
            
            // Always render if there are particles or explosion (they animate)
            const hasAnimation = renderer.particles.length > 0 || renderer.explosion;
            
            // Only render if state changed OR animation is active
            const currentState = JSON.stringify({
                lander: stateManager.state.lander,
                thrusting: thrusting,
                altitude: stateManager.state.altitude,
                speed: stateManager.state.speed
            });
            
            if (currentState !== lastRenderState || hasAnimation) {
                renderer.render(stateManager.state, thrusting);
                lastRenderState = currentState;
            }
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
    if (mobileControls) {
        mobileControls.hide();
    }
}

function startGameLoop() {
    if (!animationFrameId) {
        animationFrameId = requestAnimationFrame(gameLoop);
    }
}

document.addEventListener('keydown', (e) => {
    // F key - toggle performance monitor
    if (e.key === 'f' || e.key === 'F') {
        perfMonitor.toggle();
    }
    
    if (e.key === 'p' || e.key === 'P') {
        // Only allow pause in play mode (not spectate or replay)
        if (currentMode === 'play' && gameState.lander && !gameState.lander.crashed && !gameState.lander.landed) {
            isPaused = !isPaused;
            const pauseOverlay = document.getElementById('pauseOverlay');
            if (isPaused) {
                pauseOverlay.classList.remove('hidden');
            } else {
                pauseOverlay.classList.add('hidden');
            }
        }
    }
    if (e.key === 'r' || e.key === 'R') {
        if (!gameActive && currentMode === 'play') {
            if (wsClient) wsClient.close();
            startGame();
        }
    }
    if (e.key === 'Escape') {
        // Unpause if paused
        if (isPaused) {
            isPaused = false;
            document.getElementById('pauseOverlay').classList.add('hidden');
        }
        
        stopGameLoop();
        if (wsClient) wsClient.close();
        if (inputHandler) {
            inputHandler = null;
        }
        currentMode = null;
        appEl.classList.add('hidden');
        document.getElementById('lobby').style.display = 'none';
        menuEl.classList.remove('hidden');
        document.querySelector('.menu-buttons').classList.remove('hidden');
        document.getElementById('difficultySelect').classList.add('hidden');
        document.getElementById('gameList').classList.add('hidden');
        document.getElementById('replayList').classList.add('hidden');
        document.getElementById('helpScreen').classList.add('hidden');
        statusEl.classList.remove('visible');
        stateManager.reset();
    }
});

startGameLoop();

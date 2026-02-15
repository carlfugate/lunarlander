import { Renderer } from './renderer.js';
import { WebSocketClient } from './websocket.js';
import { InputHandler } from './input.js';

const canvas = document.getElementById('gameCanvas');
const renderer = new Renderer(canvas);
const statusEl = document.getElementById('status');

let gameState = {
    terrain: null,
    lander: null
};

let inputHandler = null;
let gameActive = false;

// WebSocket setup
const wsUrl = `ws://${window.location.hostname}:8000/ws`;
const wsClient = new WebSocketClient(wsUrl);

wsClient.onInit = (data) => {
    console.log('✓ Game initialized');
    gameState.terrain = data.terrain;
    gameState.lander = data.lander;
    gameActive = true;
    statusEl.classList.remove('visible');
};

wsClient.onTelemetry = (data) => {
    gameState.lander = data.lander;
};

wsClient.onGameOver = (data) => {
    gameActive = false;
    const result = data.landed ? 'LANDED!' : 'CRASHED!';
    const stats = `Time: ${data.time.toFixed(1)}s | Fuel: ${data.fuel_remaining.toFixed(0)} | Inputs: ${data.inputs}`;
    statusEl.innerHTML = `<div style="font-size: 24px; margin-bottom: 10px;">${result}</div><div>${stats}</div><div style="margin-top: 10px;">Press R to restart</div>`;
    statusEl.style.color = data.landed ? '#0f0' : '#f00';
    statusEl.style.borderColor = data.landed ? '#0f0' : '#f00';
    statusEl.classList.add('visible');
};

wsClient.onError = (error) => {
    statusEl.textContent = 'Connection Error';
    statusEl.style.color = '#f00';
};

// Connect and start game
async function startGame(difficulty = 'simple') {
    try {
        statusEl.textContent = 'Connecting...';
        statusEl.style.color = '#0f0';
        statusEl.style.borderColor = '#0f0';
        statusEl.classList.add('visible');
        console.log('Attempting to connect to:', wsUrl);
        await wsClient.connect();
        console.log('Connected! Starting game...');
        wsClient.startGame(difficulty);
        inputHandler = new InputHandler(wsClient);
        console.log('Input handler created');
        statusEl.classList.remove('visible');
    } catch (error) {
        console.error('Failed to start game:', error);
        statusEl.textContent = 'Failed to connect to server';
        statusEl.style.color = '#f00';
        statusEl.style.borderColor = '#f00';
        statusEl.classList.add('visible');
    }
}

// Render loop
let lastFrameTime = 0;
function gameLoop(timestamp) {
    const deltaTime = timestamp - lastFrameTime;
    lastFrameTime = timestamp;
    
    const thrusting = inputHandler ? inputHandler.isThrusting() : false;
    renderer.render(gameState, thrusting);
    
    requestAnimationFrame(gameLoop);
}

// Restart handler
document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
        if (!gameActive) {
            wsClient.close();
            startGame();
        }
    }
});

// Start
requestAnimationFrame(gameLoop);
startGame();

console.log('Lunar Lander initialized');

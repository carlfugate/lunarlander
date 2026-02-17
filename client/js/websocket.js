import { logger } from './logger.js';

/**
 * WebSocket client for game communication
 */
export class WebSocketClient {
    /**
     * Create a WebSocket client
     * @param {string} url - WebSocket server URL
     */
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.connected = false;
        this.onTelemetry = null;
        this.onInit = null;
        this.onGameOver = null;
        this.onGameStarted = null;
        this.onRoomCreated = null;
        this.onRoomJoined = null;
        this.onPlayerList = null;
        this.onError = null;
        this.lastPingTime = null;
        this.pingInterval = null;
        this.isMultiplayer = false;
    }
    
    /**
     * Connect to WebSocket server with retry logic
     * @param {number} [maxRetries=3] - Maximum connection attempts
     * @returns {Promise<void>}
     */
    async connect(maxRetries = 3) {
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                await this._attemptConnect();
                return;
            } catch (error) {
                console.log(`Connection attempt ${attempt + 1}/${maxRetries} failed`);
                if (attempt === maxRetries - 1) {
                    throw error;
                }
                // Exponential backoff: 1s, 2s, 4s
                await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)));
            }
        }
    }
    
    _attemptConnect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                this.connected = true;
                console.log('✓ WebSocket connected');
                
                // Start ping interval
                this.pingInterval = setInterval(() => {
                    if (this.connected) {
                        this.lastPingTime = Date.now();
                        this.send({ type: 'ping' });
                    }
                }, 2000); // Ping every 2 seconds
                
                resolve();
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                if (this.onError) this.onError(error);
                reject(error);
            };
            
            this.ws.onclose = () => {
                this.connected = false;
                console.log('WebSocket closed');
                
                // Clear ping interval
                if (this.pingInterval) {
                    clearInterval(this.pingInterval);
                    this.pingInterval = null;
                }
                
                // Notify user of disconnection
                if (typeof statusEl !== 'undefined' && statusEl) {
                    statusEl.innerHTML = '<div style="font-size: 20px;">Connection lost</div><div>Press ESC for menu</div>';
                    statusEl.style.color = '#f00';
                    statusEl.classList.add('visible');
                }
            };
        });
    }
    
    /**
     * Handle incoming WebSocket message
     * @param {Object} data - Message data
     * @param {string} data.type - Message type (init, telemetry, game_over, error)
     */
    handleMessage(data) {
        logger.debug('WS Receive:', { type: data.type, data });
        
        switch (data.type) {
            case 'init':
                if (this.onInit) this.onInit(data);
                break;
            case 'telemetry':
                console.log('Telemetry data received:', data);
                if (data.players) {
                    console.log('Players object found:', data.players);
                }
                console.log('onTelemetry callback exists?', !!this.onTelemetry);
                if (this.onTelemetry) this.onTelemetry(data);
                break;
            case 'game_over':
                if (this.onGameOver) this.onGameOver(data);
                break;
            case 'pong':
                // Calculate latency from ping
                if (this.lastPingTime && window.perfMonitor) {
                    const latency = Date.now() - this.lastPingTime;
                    window.perfMonitor.recordLatency(latency);
                }
                break;
            case 'room_created':
                console.log('🏠 ROOM CREATED:', data.room_id);
                this._displayRoomId(data.room_id);
                if (this.onRoomCreated) this.onRoomCreated(data);
                break;
            case 'player_list':
                console.log('👥 PLAYER LIST:', data.players);
                if (this.onPlayerList) this.onPlayerList(data);
                break;
            case 'player_joined':
                console.log('👤 PLAYER JOINED:', data);
                break;
            case 'player_left':
                console.log('👋 PLAYER LEFT:', data);
                break;
            case 'game_started':
                console.log('🎮 GAME STARTED');
                if (this.onGameStarted) this.onGameStarted();
                break;
            case 'room_joined':
                console.log('🏠 ROOM JOINED');
                if (this.onRoomJoined) this.onRoomJoined(data);
                break;
            case 'error':
                logger.error('Server error:', data.message);
                if (this.onError) this.onError(data);
                break;
        }
    }
    
    /**
     * Display room ID in top-right corner
     * @param {string} roomId - Room ID to display
     */
    _displayRoomId(roomId) {
        if (!this.isMultiplayer) return;
        
        let roomDiv = document.getElementById('room-display');
        if (!roomDiv) {
            roomDiv = document.createElement('div');
            roomDiv.id = 'room-display';
            roomDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:rgba(0,0,0,0.7);color:white;padding:5px 10px;border-radius:3px;font-family:monospace;font-size:12px;z-index:1000';
            document.body.appendChild(roomDiv);
        }
        roomDiv.textContent = `Room: ${roomId}`;
    }
    
    /**
     * Create a new room
     * @param {string} [playerName='Player1'] - Player name
     * @param {string} [roomName=null] - Custom room name
     * @returns {Promise<void>}
     */
    async createRoom(playerName = 'Player1', roomName = null) {
        if (!this.connected) {
            await this.connect();
        }
        
        this.isMultiplayer = true;
        
        this.send({
            type: 'create_room',
            difficulty: 'simple',
            player_name: playerName,
            room_name: roomName
        });
    }
    
    /**
     * Join a room
     * @param {string} roomId - Room ID to join
     * @param {string} [playerName='Player2'] - Player name
     * @returns {Promise<void>}
     */
    async joinRoom(roomId, playerName = 'Player2') {
        if (!this.connected) {
            await this.connect();
        }
        
        this.isMultiplayer = true;
        
        this.send({
            type: 'join_room',
            room_id: roomId,
            player_name: playerName
        });
        
        // Wait for room_joined confirmation from server
        return new Promise((resolve, reject) => {
            const originalOnRoomJoined = this.onRoomJoined;
            const timeout = setTimeout(() => {
                reject(new Error('Join room timeout'));
            }, 10000); // 10 second timeout
            
            this.onRoomJoined = (data) => {
                clearTimeout(timeout);
                if (originalOnRoomJoined) {
                    originalOnRoomJoined(data);
                }
                resolve();
            };
        });
    }
    
    /**
     * Start a new game
     * @param {string} [difficulty='simple'] - Difficulty level
     * @param {string|null} [token=null] - Authentication token
     * @param {string} [telemetryMode='standard'] - Telemetry mode
     * @param {number} [updateRate=60] - Update rate in Hz
     */
    startGame(difficulty = 'simple', token = null, telemetryMode = 'standard', updateRate = 60) {
        this.isMultiplayer = false;
        
        const message = {
            type: 'start',
            difficulty: difficulty,
            telemetry_mode: telemetryMode,
            update_rate: updateRate
        };
        if (token) {
            message.token = token;
        }
        this.send(message);
    }
    
    sendInput(action) {
        this.send({
            type: 'input',
            action: action
        });
    }
    
    /**
     * Send data to server
     * @param {Object} data - Data to send
     */
    send(data) {
        if (this.connected && this.ws.readyState === WebSocket.OPEN) {
            logger.debug('WS Send:', data);
            this.ws.send(JSON.stringify(data));
        }
    }
    
    close() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
        
        if (this.ws) {
            // Clean up event handlers to prevent memory leaks
            this.ws.onopen = null;
            this.ws.onmessage = null;
            this.ws.onerror = null;
            this.ws.onclose = null;
            this.ws.close();
            this.ws = null;
        }
        this.connected = false;
        this.onTelemetry = null;
        this.onInit = null;
        this.onGameOver = null;
        this.onGameStarted = null;
        this.onRoomCreated = null;
        this.onRoomJoined = null;
        this.onPlayerList = null;
        this.onError = null;
    }
}

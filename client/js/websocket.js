import { logger } from './logger.js';

export class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.connected = false;
        this.onTelemetry = null;
        this.onInit = null;
        this.onGameOver = null;
        this.onError = null;
    }
    
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
                // Notify user of disconnection
                if (typeof statusEl !== 'undefined' && statusEl) {
                    statusEl.innerHTML = '<div style="font-size: 20px;">Connection lost</div><div>Press ESC for menu</div>';
                    statusEl.style.color = '#f00';
                    statusEl.classList.add('visible');
                }
            };
        });
    }
    
    handleMessage(data) {
        logger.debug('WS Receive:', { type: data.type, data });
        
        switch (data.type) {
            case 'init':
                if (this.onInit) this.onInit(data);
                break;
            case 'telemetry':
                if (this.onTelemetry) this.onTelemetry(data);
                break;
            case 'game_over':
                if (this.onGameOver) this.onGameOver(data);
                break;
            case 'error':
                logger.error('Server error:', data.message);
                if (this.onError) this.onError(data);
                break;
        }
    }
    
    startGame(difficulty = 'simple', token = null, telemetryMode = 'standard', updateRate = 60) {
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
    
    send(data) {
        if (this.connected && this.ws.readyState === WebSocket.OPEN) {
            logger.debug('WS Send:', data);
            this.ws.send(JSON.stringify(data));
        }
    }
    
    close() {
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
        this.onError = null;
    }
}

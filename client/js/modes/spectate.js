import { WebSocketClient } from '../websocket.js';
import { stateManager } from '../state.js';
import config from '../config.js';

export function startSpectate(sessionId, onStart, onGameOver) {
    const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/spectate/${sessionId}`;
    const wsClient = new WebSocketClient(wsUrl);
    
    wsClient.onInit = (data) => {
        stateManager.setState({ terrain: data.terrain, lander: data.lander, thrusting: false });
        onStart();
    };
    
    wsClient.onTelemetry = (data) => {
        stateManager.setState({
            lander: data.lander,
            thrusting: data.thrusting || false,
            altitude: data.altitude || 0,
            speed: data.speed || 0,
            spectatorCount: data.spectator_count
        });
    };
    
    wsClient.onGameOver = (data) => {
        const result = data.landed ? 'LANDED!' : 'CRASHED!';
        onGameOver(result);
    };
    
    wsClient.connect();
    return wsClient;
}

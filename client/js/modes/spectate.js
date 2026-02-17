import { WebSocketClient } from '../websocket.js';
import { stateManager } from '../state.js';
import config from '../config.js';

export function startSpectate(sessionId, onStart, onGameOver) {
    const wsUrl = `${config.WS_PROTOCOL}//${config.WS_HOST}/spectate/${sessionId}`;
    const wsClient = new WebSocketClient(wsUrl);
    
    wsClient.onInit = (data) => {
        const stateUpdate = { terrain: data.terrain, thrusting: false };
        if (data.players) {
            stateUpdate.players = data.players;
            stateUpdate.lander = null;
        } else {
            stateUpdate.lander = data.lander;
            stateUpdate.players = null;
        }
        stateManager.setState(stateUpdate);
        onStart();
    };
    
    wsClient.onTelemetry = (data) => {
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
        console.log('Spectate game over:', data);
        
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
            
            onGameOver('', resultsHtml);
        } else {
            // Single-player format
            const result = data.landed ? 'LANDED!' : 'CRASHED!';
            const score = data.score || 0;
            const scoreText = data.landed ? `<div style="font-size: 20px; margin: 10px 0;">Score: ${score}</div>` : '';
            onGameOver(result, scoreText);
        }
    };
    
    wsClient.connect();
    return wsClient;
}

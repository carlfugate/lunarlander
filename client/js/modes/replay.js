import { stateManager } from '../state.js';
import { ReplayPlayer } from '../replay.js';
import config from '../config.js';

export async function startReplay(replayId, onStart, onEnd) {
    const response = await fetch(`${config.API_URL}/replay/${replayId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const replayData = await response.json();
    
    stateManager.setState({ terrain: replayData.metadata.terrain, lander: null });
    const replayPlayer = new ReplayPlayer(replayData);
    
    onStart();
    
    let frameIndex = 0;
    const frameDelay = 1000 / 30;
    let stopped = false;
    
    function replayLoop() {
        if (stopped) return;
        
        if (frameIndex >= replayData.frames.length) {
            onEnd();
            return;
        }
        
        const frame = replayData.frames[frameIndex];
        stateManager.setState({
            lander: frame.lander,
            altitude: frame.altitude || 0,
            speed: frame.speed || 0,
            thrusting: frame.thrusting || false
        });
        
        frameIndex++;
        setTimeout(() => requestAnimationFrame(replayLoop), frameDelay);
    }
    
    replayLoop();
    
    return {
        stop: () => { stopped = true; }
    };
}

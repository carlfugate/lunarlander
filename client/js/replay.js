export class ReplayPlayer {
    constructor(renderer) {
        this.renderer = renderer;
        this.replayData = null;
        this.currentFrame = 0;
        this.playing = false;
        this.speed = 1.0;
    }
    
    async loadReplay(replayId) {
        const response = await fetch(`http://localhost:8000/replay/${replayId}`);
        this.replayData = await response.json();
        this.currentFrame = 0;
        console.log(`Loaded replay: ${this.replayData.frames.length} frames`);
    }
    
    play() {
        this.playing = true;
        this.playLoop();
    }
    
    pause() {
        this.playing = false;
    }
    
    playLoop() {
        if (!this.playing || !this.replayData) return;
        
        if (this.currentFrame < this.replayData.frames.length) {
            const frame = this.replayData.frames[this.currentFrame];
            const gameState = {
                terrain: { points: [], landing_zones: [] }, // Would need to store terrain in replay
                lander: frame.lander
            };
            
            this.renderer.render(gameState, false);
            this.currentFrame++;
            
            setTimeout(() => this.playLoop(), (1000 / 60) / this.speed);
        } else {
            this.playing = false;
            console.log('Replay finished');
        }
    }
    
    setSpeed(speed) {
        this.speed = speed;
    }
}

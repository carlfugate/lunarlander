import { logger } from './logger.js';

export class DevTools {
    constructor() {
        this.panel = document.getElementById('devTools');
        this.visible = false;
        this.lastFrameTime = performance.now();
        this.frameCount = 0;
        this.fps = 0;
        
        // Toggle with backtick key
        document.addEventListener('keydown', (e) => {
            if (e.key === '`') {
                e.preventDefault();
                this.toggle();
            }
        });
        
        // Update FPS counter
        this.fpsInterval = setInterval(() => {
            this.fps = this.frameCount;
            this.frameCount = 0;
        }, 1000);
    }
    
    toggle() {
        this.visible = !this.visible;
        this.panel.classList.toggle('hidden', !this.visible);
        logger.debug('Dev tools:', this.visible ? 'shown' : 'hidden');
    }
    
    update(gameState) {
        if (!this.visible) return;
        
        this.frameCount++;
        const now = performance.now();
        const frameTime = now - this.lastFrameTime;
        this.lastFrameTime = now;
        
        // Update display
        this.setText('devFps', this.fps);
        this.setText('devFrameTime', `${frameTime.toFixed(2)}ms`);
        
        if (gameState?.lander) {
            this.setText('devPosition', `(${gameState.lander.x.toFixed(0)}, ${gameState.lander.y.toFixed(0)})`);
            this.setText('devVelocity', `(${gameState.lander.vx.toFixed(2)}, ${gameState.lander.vy.toFixed(2)})`);
            this.setText('devRotation', `${gameState.lander.rotation.toFixed(2)}°`);
            this.setText('devFuel', gameState.lander.fuel.toFixed(0));
        }
    }
    
    setStatus(id, value, status = 'ok') {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
            el.className = `dev-value dev-status-${status}`;
        }
    }
    
    setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }
    
    destroy() {
        clearInterval(this.fpsInterval);
    }
}

/**
 * Performance monitoring utility
 */
class PerformanceMonitor {
    constructor() {
        this.fps = 0;
        this.frameCount = 0;
        this.lastTime = performance.now();
        this.frameTimes = [];
        this.maxFrameTimes = 60;
        
        this.wsLatency = 0;
        this.wsLatencies = [];
        this.maxLatencies = 10;
        
        this.element = null;
        this.visible = false;
    }
    
    /**
     * Create and show performance overlay
     */
    show() {
        if (this.element) return;
        
        this.element = document.createElement('div');
        this.element.id = 'perfMonitor';
        this.element.innerHTML = `
            <div class="perf-row"><span>FPS:</span> <span id="perfFps">--</span></div>
            <div class="perf-row"><span>Frame:</span> <span id="perfFrame">--</span></div>
            <div class="perf-row"><span>WS Ping:</span> <span id="perfWs">--</span></div>
        `;
        document.body.appendChild(this.element);
        this.visible = true;
    }
    
    /**
     * Hide performance overlay
     */
    hide() {
        if (this.element) {
            this.element.remove();
            this.element = null;
        }
        this.visible = false;
    }
    
    /**
     * Toggle visibility
     */
    toggle() {
        if (this.visible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    /**
     * Update FPS calculation
     * @param {number} timestamp - Current timestamp
     */
    update(timestamp) {
        this.frameCount++;
        
        // Calculate frame time
        const frameTime = timestamp - this.lastTime;
        this.frameTimes.push(frameTime);
        if (this.frameTimes.length > this.maxFrameTimes) {
            this.frameTimes.shift();
        }
        
        // Update FPS every second
        if (frameTime >= 1000) {
            this.fps = Math.round(this.frameCount * 1000 / frameTime);
            this.frameCount = 0;
            this.lastTime = timestamp;
            
            this.render();
        }
    }
    
    /**
     * Record WebSocket latency
     * @param {number} latency - Latency in ms
     */
    recordLatency(latency) {
        this.wsLatencies.push(latency);
        if (this.wsLatencies.length > this.maxLatencies) {
            this.wsLatencies.shift();
        }
        
        // Calculate average
        this.wsLatency = Math.round(
            this.wsLatencies.reduce((a, b) => a + b, 0) / this.wsLatencies.length
        );
        
        this.render();
    }
    
    /**
     * Get average frame time
     * @returns {number} Average frame time in ms
     */
    getAvgFrameTime() {
        if (this.frameTimes.length === 0) return 0;
        return this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
    }
    
    /**
     * Check if performance is degraded
     * @returns {boolean}
     */
    isLagging() {
        return this.fps < 30 || this.getAvgFrameTime() > 33;
    }
    
    /**
     * Render performance stats
     */
    render() {
        if (!this.element) return;
        
        const fpsEl = document.getElementById('perfFps');
        const frameEl = document.getElementById('perfFrame');
        const wsEl = document.getElementById('perfWs');
        
        if (fpsEl) {
            fpsEl.textContent = this.fps;
            fpsEl.className = this.fps < 30 ? 'perf-warn' : this.fps < 50 ? 'perf-ok' : 'perf-good';
        }
        
        if (frameEl) {
            const avgFrame = this.getAvgFrameTime().toFixed(1);
            frameEl.textContent = `${avgFrame}ms`;
            frameEl.className = avgFrame > 33 ? 'perf-warn' : avgFrame > 20 ? 'perf-ok' : 'perf-good';
        }
        
        if (wsEl) {
            wsEl.textContent = this.wsLatency ? `${this.wsLatency}ms` : '--';
            wsEl.className = this.wsLatency > 100 ? 'perf-warn' : this.wsLatency > 50 ? 'perf-ok' : 'perf-good';
        }
    }
    
    /**
     * Get performance summary
     * @returns {Object}
     */
    getStats() {
        return {
            fps: this.fps,
            avgFrameTime: this.getAvgFrameTime(),
            wsLatency: this.wsLatency,
            isLagging: this.isLagging()
        };
    }
}

export const perfMonitor = new PerformanceMonitor();

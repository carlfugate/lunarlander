export class InputHandler {
    constructor(wsClient, getPauseState) {
        this.wsClient = wsClient;
        this.getPauseState = getPauseState;
        this.keys = {};
        this.thrusting = false;
        this.rotating = null;
        
        this.setupListeners();
    }
    
    setupListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
    }
    
    handleKeyDown(e) {
        if (this.getPauseState && this.getPauseState()) return; // Ignore input when paused
        if (this.keys[e.key]) return; // Already pressed
        this.keys[e.key] = true;
        
        switch (e.key) {
            case 'ArrowUp':
                this.thrusting = true;
                this.wsClient.sendInput('thrust_on');
                e.preventDefault();
                break;
            case 'ArrowLeft':
                this.rotating = 'left';
                this.wsClient.sendInput('rotate_left');
                e.preventDefault();
                break;
            case 'ArrowRight':
                this.rotating = 'right';
                this.wsClient.sendInput('rotate_right');
                e.preventDefault();
                break;
        }
    }
    
    handleKeyUp(e) {
        if (this.getPauseState && this.getPauseState()) return; // Ignore input when paused
        this.keys[e.key] = false;
        
        switch (e.key) {
            case 'ArrowUp':
                this.thrusting = false;
                this.wsClient.sendInput('thrust_off');
                e.preventDefault();
                break;
            case 'ArrowLeft':
            case 'ArrowRight':
                this.rotating = null;
                this.wsClient.sendInput('rotate_stop');
                e.preventDefault();
                break;
        }
    }
    
    isThrusting() {
        return this.thrusting;
    }
}

export class InputHandler {
    constructor(wsClient) {
        this.wsClient = wsClient;
        this.keys = {};
        this.thrusting = false;
        this.rotating = null;
        
        this.setupListeners();
    }
    
    setupListeners() {
        console.log('Setting up input listeners...');
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));
        console.log('Input listeners ready');
    }
    
    handleKeyDown(e) {
        if (this.keys[e.key]) return; // Already pressed
        this.keys[e.key] = true;
        
        switch (e.key) {
            case 'ArrowUp':
                this.thrusting = true;
                this.wsClient.sendInput('thrust');
                console.log('Thrust ON');
                e.preventDefault();
                break;
            case 'ArrowLeft':
                this.rotating = 'left';
                this.wsClient.sendInput('rotate_left');
                console.log('Rotate LEFT');
                e.preventDefault();
                break;
            case 'ArrowRight':
                this.rotating = 'right';
                this.wsClient.sendInput('rotate_right');
                console.log('Rotate RIGHT');
                e.preventDefault();
                break;
        }
    }
    
    handleKeyUp(e) {
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

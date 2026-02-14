// Mobile touch controls for Lunar Lander
export class MobileControls {
    constructor(websocketManager) {
        this.ws = websocketManager;
        this.controlsDiv = document.getElementById('mobileControls');
        this.thrustBtn = document.getElementById('thrust');
        this.leftBtn = document.getElementById('rotateLeft');
        this.rightBtn = document.getElementById('rotateRight');
        
        this.setupControls();
    }
    
    setupControls() {
        // Thrust button
        this.thrustBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.ws.sendInput('thrust_on');
        });
        this.thrustBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.ws.sendInput('thrust_off');
        });
        
        // Left rotation
        this.leftBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_left');
        });
        this.leftBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_stop');
        });
        
        // Right rotation
        this.rightBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_right');
        });
        this.rightBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_stop');
        });
    }
    
    show() {
        this.controlsDiv.classList.remove('hidden');
        this.controlsDiv.classList.add('visible');
    }
    
    hide() {
        this.controlsDiv.classList.remove('visible');
        this.controlsDiv.classList.add('hidden');
    }
}

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
        // Thrust button - both touch and mouse for testing
        this.thrustBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            console.log('Thrust ON');
            this.ws.sendInput('thrust_on');
        });
        this.thrustBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            console.log('Thrust OFF');
            this.ws.sendInput('thrust_off');
        });
        this.thrustBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            console.log('Thrust ON (mouse)');
            this.ws.sendInput('thrust_on');
        });
        this.thrustBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            console.log('Thrust OFF (mouse)');
            this.ws.sendInput('thrust_off');
        });
        
        // Left rotation
        this.leftBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            console.log('Rotate LEFT');
            this.ws.sendInput('rotate_left');
        });
        this.leftBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            console.log('Rotate STOP');
            this.ws.sendInput('rotate_stop');
        });
        this.leftBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            console.log('Rotate LEFT (mouse)');
            this.ws.sendInput('rotate_left');
        });
        this.leftBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            console.log('Rotate STOP (mouse)');
            this.ws.sendInput('rotate_stop');
        });
        
        // Right rotation
        this.rightBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            console.log('Rotate RIGHT');
            this.ws.sendInput('rotate_right');
        });
        this.rightBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            console.log('Rotate STOP');
            this.ws.sendInput('rotate_stop');
        });
        this.rightBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            console.log('Rotate RIGHT (mouse)');
            this.ws.sendInput('rotate_right');
        });
        this.rightBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            console.log('Rotate STOP (mouse)');
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

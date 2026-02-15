// Mobile touch controls for Lunar Lander
export class MobileControls {
    constructor(websocketManager) {
        this.ws = websocketManager;
        this.controlsDiv = document.getElementById('mobileControls');
        this.menuControlsDiv = document.getElementById('mobileMenuControls');
        this.thrustBtn = document.getElementById('thrust');
        this.leftBtn = document.getElementById('rotateLeft');
        this.rightBtn = document.getElementById('rotateRight');
        this.restartBtn = document.getElementById('mobileRestart');
        this.menuBtn = document.getElementById('mobileMenu');
        this.swapBtn = document.getElementById('controlSwap');
        this.leftGroup = document.getElementById('leftControls');
        this.rightGroup = document.getElementById('rightControls');
        
        this.thrustOnLeft = true; // Default: thrust on left
        this.loadPreference();
        this.swapControls(); // Initialize layout
        this.setupControls();
        this.setupMenuControls();
        this.setupSwapButton();
    }
    
    loadPreference() {
        const saved = localStorage.getItem('mobileControlSide');
        if (saved === 'right') {
            this.thrustOnLeft = false;
            this.swapControls();
        }
    }
    
    savePreference() {
        localStorage.setItem('mobileControlSide', this.thrustOnLeft ? 'left' : 'right');
    }
    
    swapControls() {
        if (this.thrustOnLeft) {
            // Thrust on left (default)
            this.leftGroup.innerHTML = '';
            this.rightGroup.innerHTML = '';
            this.leftGroup.appendChild(this.thrustBtn);
            this.rightGroup.appendChild(this.leftBtn);
            this.rightGroup.appendChild(this.rightBtn);
        } else {
            // Thrust on right (swapped)
            this.leftGroup.innerHTML = '';
            this.rightGroup.innerHTML = '';
            this.leftGroup.appendChild(this.leftBtn);
            this.leftGroup.appendChild(this.rightBtn);
            this.rightGroup.appendChild(this.thrustBtn);
        }
    }
    
    setupSwapButton() {
        this.swapBtn.addEventListener('click', () => {
            this.thrustOnLeft = !this.thrustOnLeft;
            this.swapControls();
            this.savePreference();
        });
    }
    
    setupMenuControls() {
        // Restart button (R key)
        this.restartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const event = new KeyboardEvent('keydown', { key: 'r' });
            document.dispatchEvent(event);
        });
        
        // Menu button (ESC key)
        this.menuBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const event = new KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(event);
        });
    }
    
    setupControls() {
        // Thrust button - both touch and mouse
        this.thrustBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.ws.sendInput('thrust_on');
        });
        this.thrustBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.ws.sendInput('thrust_off');
        });
        this.thrustBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.ws.sendInput('thrust_on');
        });
        this.thrustBtn.addEventListener('mouseup', (e) => {
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
        this.leftBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_left');
        });
        this.leftBtn.addEventListener('mouseup', (e) => {
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
        this.rightBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_right');
        });
        this.rightBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.ws.sendInput('rotate_stop');
        });
    }
    
    show() {
        this.controlsDiv.classList.remove('hidden');
        this.controlsDiv.classList.add('visible');
        this.menuControlsDiv.classList.remove('hidden');
        this.menuControlsDiv.classList.add('visible');
        this.swapBtn.classList.remove('hidden');
        this.swapBtn.classList.add('visible');
    }
    
    hide() {
        this.controlsDiv.classList.remove('visible');
        this.controlsDiv.classList.add('hidden');
        this.menuControlsDiv.classList.remove('visible');
        this.menuControlsDiv.classList.add('hidden');
        this.swapBtn.classList.remove('visible');
        this.swapBtn.classList.add('hidden');
    }
}

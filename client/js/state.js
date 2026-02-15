/**
 * @typedef {Object} GameState
 * @property {Array<{x: number, y: number}>|null} terrain
 * @property {Object|null} lander
 * @property {boolean} thrusting
 * @property {number} altitude
 * @property {number} speed
 * @property {number} [spectatorCount]
 */

/**
 * Simple centralized state management
 */
class StateManager {
    constructor() {
        /** @type {GameState} */
        this.state = {
            terrain: null,
            lander: null,
            thrusting: false,
            altitude: 0,
            speed: 0,
        };
        
        this.listeners = [];
    }
    
    /**
     * Get current state
     * @returns {GameState}
     */
    getState() {
        return this.state;
    }
    
    /**
     * Update state and notify listeners
     * @param {Partial<GameState>} updates - State updates
     */
    setState(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };
        
        // Update global reference
        window.gameState = this.state;
        
        // Notify listeners
        this.listeners.forEach(listener => {
            listener(this.state, oldState);
        });
    }
    
    /**
     * Subscribe to state changes
     * @param {Function} listener - Callback function
     * @returns {Function} Unsubscribe function
     */
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
    
    /**
     * Reset state to initial values
     */
    reset() {
        this.setState({
            terrain: null,
            lander: null,
            thrusting: false,
            altitude: 0,
            speed: 0,
            spectatorCount: undefined,
        });
    }
}

// Export singleton instance
export const stateManager = new StateManager();

// Make available globally for error tracking
window.gameState = stateManager.state;

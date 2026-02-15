// Debug logging utility with environment-based control
// Enable with: ?debug=true in URL or localStorage.setItem('debug', 'true') in console

const isDebugEnabled = () => {
    return localStorage.getItem('debug') === 'true' || 
           new URLSearchParams(window.location.search).get('debug') === 'true';
};

export const logger = {
    debug: (...args) => {
        if (isDebugEnabled()) {
            console.log('[DEBUG]', ...args);
        }
    },
    
    info: (...args) => console.log('[INFO]', ...args),
    
    warn: (...args) => console.warn('[WARN]', ...args),
    
    error: (...args) => console.error('[ERROR]', ...args)
};

// Enable debug mode from console: logger.enable()
// Disable debug mode from console: logger.disable()
logger.enable = () => {
    localStorage.setItem('debug', 'true');
    console.log('Debug logging enabled. Reload page to take effect.');
};

logger.disable = () => {
    localStorage.removeItem('debug');
    console.log('Debug logging disabled. Reload page to take effect.');
};

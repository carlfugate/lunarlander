import { logger } from './logger.js';

// Global error handlers
window.addEventListener('error', (e) => {
    logger.error('Unhandled error:', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error?.stack
    });
});

window.addEventListener('unhandledrejection', (e) => {
    logger.error('Unhandled promise rejection:', {
        reason: e.reason,
        promise: e.promise
    });
});

// Debug logging utility with environment-based control
// Enable with: ?debug=true in URL or localStorage.setItem('debug', 'true') in console

const isDebugEnabled = () => {
    try {
        return localStorage.getItem('debug') === 'true' || 
               new URLSearchParams(window.location.search).get('debug') === 'true';
    } catch {
        return false;
    }
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

// Performance monitoring
logger.perf = {
    mark: (name) => performance.mark(name),
    measure: (name, startMark) => {
        performance.measure(name, startMark);
        const measure = performance.getEntriesByName(name)[0];
        logger.debug(`Performance [${name}]:`, `${measure.duration.toFixed(2)}ms`);
    },
    memory: () => {
        if (performance.memory) {
            logger.debug('Memory:', {
                used: `${(performance.memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
                total: `${(performance.memory.totalJSHeapSize / 1048576).toFixed(2)} MB`
            });
        }
    }
};

// Local storage inspector
logger.storage = () => {
    const storage = {};
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        storage[key] = localStorage.getItem(key);
    }
    logger.debug('LocalStorage:', storage);
};

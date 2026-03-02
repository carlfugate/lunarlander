import * as Sentry from '@sentry/browser';
import { logger } from './logger.js';

/**
 * Initialize error tracking
 * Set SENTRY_DSN environment variable or pass dsn parameter
 * @param {string} [dsn] - Sentry DSN (optional, uses env var if not provided)
 */
export function initErrorTracking(dsn) {
    // Only initialize if DSN is provided
    const sentryDsn = dsn || import.meta.env.VITE_SENTRY_DSN;
    
    if (!sentryDsn) {
        logger.info('Sentry not configured (no DSN). Error tracking disabled.');
        return;
    }
    
    Sentry.init({
        dsn: sentryDsn,
        environment: import.meta.env.MODE || 'development',
        
        // Performance monitoring
        tracesSampleRate: 0.1, // 10% of transactions
        
        // Only send errors in production
        enabled: import.meta.env.PROD || false,
        
        // Release tracking
        release: import.meta.env.VITE_APP_VERSION || 'dev',
        
        // Ignore common errors
        ignoreErrors: [
            'ResizeObserver loop limit exceeded',
            'Non-Error promise rejection captured',
        ],
        
        // Add context to errors
        beforeSend(event, hint) {
            // Add game state context
            if (window.gameState) {
                event.contexts = event.contexts || {};
                event.contexts.game = {
                    has_terrain: !!window.gameState.terrain,
                    has_lander: !!window.gameState.lander,
                    thrusting: window.gameState.thrusting,
                };
            }
            
            // Log to console in development
            if (import.meta.env.DEV) {
                logger.error('Sentry captured error:', hint.originalException || hint.syntheticException);
            }
            
            return event;
        },
    });
    
    logger.info('Error tracking initialized');
}

/**
 * Manually capture an error
 * @param {Error} error - Error to capture
 * @param {Object} [context] - Additional context
 */
export function captureError(error, context) {
    Sentry.captureException(error, { extra: context });
}

/**
 * Set user context for error tracking
 * @param {Object} user - User information
 * @param {string} [user.id] - User ID
 * @param {string} [user.username] - Username
 */
export function setUser(user) {
    Sentry.setUser(user);
}

/**
 * Add breadcrumb for debugging
 * @param {string} message - Breadcrumb message
 * @param {string} [category='info'] - Category
 * @param {Object} [data] - Additional data
 */
export function addBreadcrumb(message, category = 'info', data = {}) {
    Sentry.addBreadcrumb({
        message,
        category,
        data,
        level: 'info',
    });
}

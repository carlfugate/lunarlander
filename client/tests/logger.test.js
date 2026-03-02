import { describe, it, expect } from 'vitest';
import { logger } from '../js/logger.js';

describe('Logger', () => {
    it('should have debug, info, warn, error methods', () => {
        expect(logger.debug).toBeDefined();
        expect(logger.info).toBeDefined();
        expect(logger.warn).toBeDefined();
        expect(logger.error).toBeDefined();
    });

    it('should have enable/disable methods', () => {
        expect(logger.enable).toBeDefined();
        expect(logger.disable).toBeDefined();
    });
});

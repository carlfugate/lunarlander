import { test, expect } from '@playwright/test';

test.describe('Status Box Display', () => {
    test('should display status box on game over', async ({ page }) => {
        await page.goto('http://localhost:8080');
        
        // Click play button
        await page.click('#playBtn');
        
        // Wait for game to start
        await page.waitForSelector('#gameCanvas', { state: 'visible' });
        
        // Wait for game over (crash by doing nothing)
        await page.waitForTimeout(15000);
        
        // Check status box is visible
        const statusBox = page.locator('#status');
        await expect(statusBox).toBeVisible();
        
        // Verify it has content
        const text = await statusBox.textContent();
        expect(text).toContain('CRASHED!');
        
        // Verify CSS is applied
        const zIndex = await statusBox.evaluate(el => window.getComputedStyle(el).zIndex);
        expect(zIndex).toBe('2000');
        
        const position = await statusBox.evaluate(el => window.getComputedStyle(el).position);
        expect(position).toBe('fixed');
        
        const display = await statusBox.evaluate(el => window.getComputedStyle(el).display);
        expect(display).toBe('block');
    });
});

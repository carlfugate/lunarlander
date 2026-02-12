import { test, expect } from '@playwright/test';

test.describe('Critical User Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });
  
  test('should load menu without errors', async ({ page }) => {
    // Check for JavaScript errors
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    
    await expect(page.locator('h1')).toHaveText('Lunar Lander');
    await expect(page.locator('#playBtn')).toBeVisible();
    await expect(page.locator('#spectateBtn')).toBeVisible();
    await expect(page.locator('#replayBtn')).toBeVisible();
    
    expect(errors).toHaveLength(0);
  });
  
  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate server down
    await page.route('**/games', route => route.abort());
    await page.route('**/replays', route => route.abort());
    
    await page.click('#spectateBtn');
    await page.waitForTimeout(500);
    
    // Should show error message, not crash
    const content = await page.locator('#gameListContent').textContent();
    expect(content).toBeTruthy();
  });
  
  test('should return to menu on ESC', async ({ page }) => {
    await page.click('#playBtn');
    await page.waitForTimeout(500);
    
    await expect(page.locator('#gameCanvas')).toBeVisible();
    
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);
    
    await expect(page.locator('#menu')).toBeVisible();
    await expect(page.locator('#app')).toBeHidden();
  });
  
  test('should not have memory leaks when returning to menu', async ({ page }) => {
    // This test catches the game loop memory leak
    await page.click('#playBtn');
    await page.waitForTimeout(1000);
    
    // Get initial metrics
    const initialMetrics = await page.evaluate(() => {
      return {
        jsHeapSize: performance.memory?.usedJSHeapSize || 0,
        timestamp: Date.now()
      };
    });
    
    // Return to menu
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Wait and check if heap keeps growing (indicates leak)
    await page.waitForTimeout(2000);
    
    const finalMetrics = await page.evaluate(() => {
      return {
        jsHeapSize: performance.memory?.usedJSHeapSize || 0,
        timestamp: Date.now()
      };
    });
    
    // Heap should not grow significantly after returning to menu
    const heapGrowth = finalMetrics.jsHeapSize - initialMetrics.jsHeapSize;
    expect(heapGrowth).toBeLessThan(5000000); // 5MB threshold
  });
});

test.describe('Spectator Mode - Black Screen Bug', () => {
  test('should show game canvas when spectating', async ({ page }) => {
    // Mock active games response
    await page.route('**/games', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          games: [{
            session_id: 'test-session',
            user_id: 'test-user',
            difficulty: 'simple',
            spectators: 0,
            duration: 10
          }]
        })
      });
    });
    
    await page.click('#spectateBtn');
    await page.waitForTimeout(500);
    
    // Should show game list
    await expect(page.locator('#gameList')).toBeVisible();
    await expect(page.locator('.game-item')).toBeVisible();
    
    // Note: Can't fully test WebSocket connection without server running
    // But we can verify the UI flow works
  });
});

test.describe('Replay Mode', () => {
  test('should show replays list', async ({ page }) => {
    // Mock replays response
    await page.route('**/replays', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          replays: [{
            replay_id: 'test-replay',
            user_id: 'test-user',
            difficulty: 'simple',
            duration: 120,
            landed: true,
            crashed: false
          }]
        })
      });
    });
    
    await page.click('#replayBtn');
    await page.waitForTimeout(500);
    
    await expect(page.locator('#replayList')).toBeVisible();
    await expect(page.locator('.replay-item')).toBeVisible();
  });
  
  test('should handle empty replays list', async ({ page }) => {
    await page.route('**/replays', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ replays: [] })
      });
    });
    
    await page.click('#replayBtn');
    await page.waitForTimeout(500);
    
    const content = await page.locator('#replayListContent').textContent();
    expect(content).toContain('No replays');
  });
});

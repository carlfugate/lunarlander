# Automated Testing Strategy

## Overview

Reduce manual testing burden with automated tests at multiple levels: unit, integration, and end-to-end.

---

## 1. Unit Tests (JavaScript - Vitest/Jest)

### Setup
```bash
npm init -y
npm install --save-dev vitest @vitest/ui jsdom
```

### Test Files to Create

#### `client/js/__tests__/renderer.test.js`
```javascript
import { describe, it, expect, beforeEach } from 'vitest';
import { Renderer } from '../renderer.js';

describe('Renderer', () => {
    let canvas, renderer;
    
    beforeEach(() => {
        canvas = document.createElement('canvas');
        canvas.width = 1200;
        canvas.height = 800;
        renderer = new Renderer(canvas);
    });
    
    it('should initialize with correct dimensions', () => {
        expect(renderer.width).toBe(1200);
        expect(renderer.height).toBe(800);
    });
    
    it('should clear canvas', () => {
        renderer.clear();
        const imageData = renderer.ctx.getImageData(0, 0, 1, 1);
        expect(imageData.data[0]).toBe(0); // Black
    });
    
    it('should not crash with null lander', () => {
        expect(() => renderer.drawLander(null, false)).not.toThrow();
    });
    
    it('should render HUD with server values', () => {
        const lander = { x: 600, y: 400, vx: 0, vy: 2, rotation: 0, fuel: 500 };
        expect(() => renderer.drawHUD(lander, 400, 2.0)).not.toThrow();
    });
});
```

#### `client/js/__tests__/websocket.test.js`
```javascript
import { describe, it, expect, vi } from 'vitest';
import { WebSocketClient } from '../websocket.js';

describe('WebSocketClient', () => {
    it('should handle connection errors gracefully', async () => {
        const client = new WebSocketClient('ws://invalid:9999');
        await expect(client.connect()).rejects.toThrow();
    });
    
    it('should cleanup on close', () => {
        const client = new WebSocketClient('ws://localhost:8000/ws');
        client.ws = { close: vi.fn(), readyState: 1 };
        client.close();
        expect(client.ws).toBeNull();
    });
    
    it('should not send when disconnected', () => {
        const client = new WebSocketClient('ws://localhost:8000/ws');
        client.connected = false;
        expect(() => client.sendInput('thrust')).not.toThrow();
    });
});
```

### Run Tests
```bash
npx vitest
```

---

## 2. Integration Tests (Playwright)

### Setup
```bash
npm install --save-dev @playwright/test
npx playwright install
```

### Test File: `tests/e2e/game.spec.js`
```javascript
import { test, expect } from '@playwright/test';

test.describe('Lunar Lander Game', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8080');
    });
    
    test('should load menu', async ({ page }) => {
        await expect(page.locator('h1')).toHaveText('Lunar Lander');
        await expect(page.locator('#playBtn')).toBeVisible();
        await expect(page.locator('#spectateBtn')).toBeVisible();
        await expect(page.locator('#replayBtn')).toBeVisible();
    });
    
    test('should start game on play button', async ({ page }) => {
        await page.click('#playBtn');
        await expect(page.locator('#gameCanvas')).toBeVisible();
        await expect(page.locator('#modeIndicator')).toHaveText('PLAYING');
    });
    
    test('should load active games list', async ({ page }) => {
        await page.click('#spectateBtn');
        await expect(page.locator('#gameList')).toBeVisible();
        // Wait for fetch to complete
        await page.waitForTimeout(1000);
        const content = await page.locator('#gameListContent').textContent();
        expect(content).toBeTruthy();
    });
    
    test('should handle network errors gracefully', async ({ page }) => {
        // Simulate offline
        await page.route('**/games', route => route.abort());
        await page.click('#spectateBtn');
        await page.waitForTimeout(500);
        const content = await page.locator('#gameListContent').textContent();
        expect(content).toContain('Failed');
    });
    
    test('should return to menu on ESC', async ({ page }) => {
        await page.click('#playBtn');
        await page.keyboard.press('Escape');
        await expect(page.locator('#menu')).toBeVisible();
        await expect(page.locator('#app')).toBeHidden();
    });
    
    test('should not have memory leaks', async ({ page }) => {
        // Start game
        await page.click('#playBtn');
        await page.waitForTimeout(1000);
        
        // Return to menu
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        
        // Check that game loop stopped
        const metrics = await page.metrics();
        const initialJSHeap = metrics.JSHeapUsedSize;
        
        await page.waitForTimeout(2000);
        const finalMetrics = await page.metrics();
        const finalJSHeap = finalMetrics.JSHeapUsedSize;
        
        // Heap should not grow significantly
        expect(finalJSHeap - initialJSHeap).toBeLessThan(1000000); // 1MB
    });
});
```

### Run E2E Tests
```bash
npx playwright test
```

---

## 3. Visual Regression Tests (Playwright)

### Test File: `tests/visual/screenshots.spec.js`
```javascript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
    test('menu should match snapshot', async ({ page }) => {
        await page.goto('http://localhost:8080');
        await expect(page).toHaveScreenshot('menu.png');
    });
    
    test('game canvas should render', async ({ page }) => {
        await page.goto('http://localhost:8080');
        await page.click('#playBtn');
        await page.waitForTimeout(1000);
        await expect(page.locator('#gameCanvas')).toHaveScreenshot('game.png');
    });
});
```

---

## 4. Performance Tests (Lighthouse CI)

### Setup
```bash
npm install --save-dev @lhci/cli
```

### Config: `lighthouserc.js`
```javascript
module.exports = {
    ci: {
        collect: {
            url: ['http://localhost:8080'],
            numberOfRuns: 3,
        },
        assert: {
            assertions: {
                'categories:performance': ['error', { minScore: 0.9 }],
                'categories:accessibility': ['error', { minScore: 0.9 }],
                'categories:best-practices': ['error', { minScore: 0.9 }],
            },
        },
    },
};
```

### Run Performance Tests
```bash
npx lhci autorun
```

---

## 5. API/WebSocket Tests (Python - pytest)

### Setup
```bash
cd server
pip install pytest pytest-asyncio websockets
```

### Test File: `server/tests/test_websocket.py`
```python
import pytest
import asyncio
import websockets
import json

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test basic WebSocket connection"""
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        # Send start message
        await ws.send(json.dumps({"type": "start", "difficulty": "simple"}))
        
        # Receive init message
        response = await ws.recv()
        data = json.loads(response)
        assert data['type'] == 'init'
        assert 'terrain' in data
        assert 'lander' in data

@pytest.mark.asyncio
async def test_telemetry_rate():
    """Test that telemetry is sent at 60Hz"""
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.send(json.dumps({"type": "start", "difficulty": "simple"}))
        await ws.recv()  # Skip init
        
        # Receive 60 messages
        start = asyncio.get_event_loop().time()
        for _ in range(60):
            await ws.recv()
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should take ~1 second (60Hz)
        assert 0.9 < elapsed < 1.1

@pytest.mark.asyncio
async def test_spectator_receives_telemetry():
    """Test spectator mode"""
    # Start a game
    async with websockets.connect('ws://localhost:8000/ws') as player_ws:
        await player_ws.send(json.dumps({"type": "start"}))
        init_msg = await player_ws.recv()
        session_id = json.loads(init_msg)['session_id']  # Would need to add this
        
        # Connect spectator
        async with websockets.connect(f'ws://localhost:8000/spectate/{session_id}') as spec_ws:
            # Spectator should receive telemetry
            msg = await spec_ws.recv()
            data = json.loads(msg)
            assert data['type'] in ['init', 'telemetry']
```

### Run API Tests
```bash
pytest server/tests/
```

---

## 6. Continuous Integration (GitHub Actions)

### File: `.github/workflows/test.yml`
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Python dependencies
        run: |
          cd server
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Install Node dependencies
        run: |
          cd client
          npm install
      
      - name: Start server
        run: |
          cd server
          python -m uvicorn main:app --port 8000 &
          sleep 5
      
      - name: Start client
        run: |
          cd client
          python -m http.server 8080 &
          sleep 2
      
      - name: Run Python tests
        run: |
          cd server
          pytest tests/
      
      - name: Run JavaScript tests
        run: |
          cd client
          npm test
      
      - name: Run E2E tests
        run: |
          cd client
          npx playwright test
      
      - name: Run Lighthouse
        run: |
          cd client
          npx lhci autorun
```

---

## 7. Test Coverage Goals

### Minimum Coverage Targets
- **Unit Tests**: 80% code coverage
- **Integration Tests**: All user flows
- **E2E Tests**: Critical paths (play, spectate, replay)
- **Performance**: Lighthouse score > 90

### What to Test
✅ **Must Test**:
- WebSocket connection/disconnection
- Game state updates
- Replay playback
- Error handling
- Memory leaks

⚠️ **Should Test**:
- UI interactions
- Loading states
- Empty states
- Keyboard navigation

❌ **Don't Test**:
- Visual styling details
- Animation smoothness (manual QA)
- Exact pixel positions

---

## 8. Running Tests Locally

### Quick Test Suite
```bash
# Terminal 1: Start server
cd server && source ../venv/bin/activate && uvicorn main:app --port 8000

# Terminal 2: Start client
cd client && python -m http.server 8080

# Terminal 3: Run tests
cd client
npm test                    # Unit tests
npx playwright test         # E2E tests
npx lhci autorun           # Performance tests

cd ../server
pytest tests/              # API tests
```

### Watch Mode (Development)
```bash
# Auto-run tests on file changes
cd client && npx vitest --watch
```

---

## 9. Test Maintenance

### When to Update Tests
- ✅ Before fixing bugs (write failing test first)
- ✅ When adding new features
- ✅ When refactoring code
- ❌ Don't update tests to match bugs

### Test Hygiene
- Keep tests fast (< 5 seconds per test)
- Make tests independent (no shared state)
- Use descriptive test names
- Clean up resources (WebSockets, timers)

---

## 10. Monitoring in Production

### Add Error Tracking
```javascript
// client/js/error-tracking.js
window.addEventListener('error', (event) => {
    // Send to error tracking service (Sentry, etc.)
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
```

### Add Performance Monitoring
```javascript
// Track WebSocket latency
const startTime = performance.now();
wsClient.onTelemetry = (data) => {
    const latency = performance.now() - data.timestamp;
    if (latency > 100) {
        console.warn('High latency:', latency);
    }
};
```

---

## Summary

This testing strategy provides:
- **80% automation** - Reduces manual testing significantly
- **Fast feedback** - Tests run in < 2 minutes
- **Confidence** - Catch bugs before users do
- **Documentation** - Tests serve as usage examples

**Next Steps**:
1. Set up Vitest for unit tests (1 hour)
2. Set up Playwright for E2E tests (2 hours)
3. Write critical path tests (4 hours)
4. Add to CI/CD pipeline (1 hour)

**Total Setup Time**: ~8 hours
**Time Saved**: ~2 hours per week in manual testing

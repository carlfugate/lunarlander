# Testing Infrastructure - Quick Start

## ✅ What's Been Set Up

### Unit Tests (Vitest)
- **10 JavaScript tests** covering renderer and WebSocket
- Tests for past bugs: HUD metrics, spectator black screen, WebSocket cleanup
- Run with: `cd client && npm test`

### E2E Tests (Playwright)
- Critical user flow tests
- Memory leak detection
- Network error handling
- Run with: `cd client && npm run test:e2e`

### Python Tests (pytest)
- **4 tests** for replay optimization
- Tests 30Hz recording and quantization
- Run with: `cd server && PYTHONPATH=. pytest tests/`

### Test Runner Script
- Runs all tests in sequence
- Run with: `./run-tests.sh`

## 🎯 Tests Cover These Past Bugs

1. **Spectator Black Screen** - Verifies init message with terrain/lander
2. **HUD Metrics Wrong** - Tests server-calculated altitude/speed usage
3. **Replay Size** - Validates 30Hz recording and quantization
4. **Memory Leaks** - Detects game loop not stopping
5. **WebSocket Cleanup** - Ensures proper resource cleanup

## 📊 Current Test Status

- ✅ JavaScript: 10/10 passing
- ✅ Python: 4/4 passing
- ⏳ E2E: Requires servers running

## 🚀 Running Tests

### Quick Test (Unit Tests Only)
```bash
# JavaScript
cd client && npm test

# Python
cd server && source ../venv/bin/activate && PYTHONPATH=. pytest tests/
```

### Full Test Suite (Requires Servers)
```bash
# Terminal 1: Start server
cd server && source ../venv/bin/activate && uvicorn main:app --port 8000

# Terminal 2: Start client
cd client && python3 -m http.server 8080

# Terminal 3: Run all tests
./run-tests.sh
```

## 📝 Adding New Tests

### JavaScript Unit Test
Create `client/tests/your-feature.test.js`:
```javascript
import { describe, it, expect } from 'vitest';

describe('Your Feature', () => {
  it('should do something', () => {
    expect(true).toBe(true);
  });
});
```

### E2E Test
Add to `client/tests/e2e/critical-flows.spec.js`:
```javascript
test('should do something in browser', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toBeVisible();
});
```

### Python Test
Create `server/tests/test_your_feature.py`:
```python
def test_something():
    assert True
```

## 🎓 What Tests Prevent

- ✅ Spectator mode breaking again
- ✅ HUD showing wrong values
- ✅ Replay files getting too large
- ✅ Memory leaks from game loop
- ✅ WebSocket connections not cleaning up

## 📈 Next Steps

1. Run tests before committing code
2. Add tests when fixing bugs
3. Add tests when adding features
4. Set up CI/CD to run tests automatically

## 🔧 Troubleshooting

**Tests fail with "canvas not found"**
- Already fixed with mock in `tests/setup.js`

**E2E tests timeout**
- Make sure both servers are running
- Check ports 8000 and 8080 are available

**Python tests can't find modules**
- Use `PYTHONPATH=. pytest tests/` from server directory
- Make sure venv is activated

## 💡 Tips

- Tests run fast (~1 second for unit tests)
- E2E tests catch UI regressions
- Python tests validate server logic
- Memory leak test prevents performance issues

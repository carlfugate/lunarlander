# CLI Testing Checklist

## Automated Testing (Required Before Commit)

### Quick Test
```bash
cd cli
./run_all_tests.sh
```

This runs:
1. ✅ Unit tests (must pass)
2. ✅ Coverage check (75% minimum)
3. ✅ E2E tests (if server running)
4. ✅ Reminds you to do manual testing

### Pre-Commit Hook
The pre-commit hook automatically runs `run_all_tests.sh` when you commit CLI changes.

**To bypass (emergency only):**
```bash
git commit --no-verify
```

## Manual Testing (Required Before Declaring Complete)

### Basic Smoke Test
```bash
cd cli
source ../.venv/bin/activate
python terminal_client.py
```

**Verify:**
- [ ] Menu displays correctly
- [ ] Can select difficulty
- [ ] Game starts without errors
- [ ] **Terrain renders as lines** (not dots)
- [ ] **Lander renders and rotates** (^, <, >, v)
- [ ] Controls work (arrow keys or WASD)
- [ ] HUD shows fuel/speed/altitude
- [ ] Game over displays correctly
- [ ] Can quit with ESC or Q

### Edge Cases
```bash
# Test without server
python terminal_client.py  # Should show connection error

# Test ASCII mode
python terminal_client.py --ansi-strict

# Test direct start
python terminal_client.py --no-menu --difficulty hard
```

## Testing Workflow

### Before Making Changes
```bash
# Establish baseline
./run_all_tests.sh
```

### After Making Changes
```bash
# Run automated tests
./run_all_tests.sh

# If tests pass, do manual smoke test
python terminal_client.py

# If everything works, commit
git add .
git commit -m "Your message"
# Pre-commit hook runs automatically
```

### If Tests Fail
1. Read the error message
2. Fix the code
3. Run `./run_all_tests.sh` again
4. Repeat until green

## Common Issues to Watch For

1. **Type mismatches**: Dict vs Object (GameState, TerminalCapabilities)
2. **None values**: Always check if attributes exist before accessing
3. **Data structure assumptions**: Check server code for actual format
4. **Radians vs degrees**: Rotation is in radians, convert for display
5. **Coordinate systems**: Server uses (x, y), screen uses inverted y
6. **Terrain rendering**: Points are [x, y] pairs, draw lines between them

## Test Coverage Goals

- Unit tests: 75%+ coverage (enforced)
- Integration tests: Cover all main workflows
- E2E tests: Cover happy path + critical errors
- Manual testing: Every feature, every change

## Remember

**Tests passing ≠ Application working**

Always do manual verification. The tests can mock away real problems:
- Runtime type errors
- User experience issues
- Rendering glitches
- Input handling problems

## Quick Commands

```bash
# Run all tests
./run_all_tests.sh

# Run only unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run E2E tests
python test_e2e.py

# Manual test
python terminal_client.py
```

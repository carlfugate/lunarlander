# Contributing to Lunar Lander

## Development Workflow

### Setup
```bash
# Clone the repository
git clone <repo-url>
cd lunarlander

# Setup Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r cli/requirements.txt
pip install -r cli/requirements-dev.txt

# Setup server
cd server
python3 -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
```

### Before Making Changes

1. **Ensure tests pass:**
   ```bash
   ./cli/run_all_tests.sh
   ```

2. **Start the server (for E2E tests):**
   ```bash
   cd server
   source ../venv/bin/activate
   uvicorn main:app --port 8000
   ```

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run tests frequently:**
   ```bash
   ./cli/run_all_tests.sh
   ```

### Before Committing

1. **Run full test suite:**
   ```bash
   ./cli/run_all_tests.sh
   ```
   
   This checks:
   - ✅ Unit tests pass
   - ✅ Coverage ≥ 75%
   - ✅ E2E tests pass (if server running)

2. **Do manual testing:**
   ```bash
   cd cli
   python terminal_client.py
   ```
   
   Verify:
   - [ ] Menu displays
   - [ ] Game starts
   - [ ] Terrain renders as lines
   - [ ] Lander renders and rotates
   - [ ] Controls work
   - [ ] HUD updates
   - [ ] Game over works

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```
   
   The pre-commit hook will automatically run tests. If they fail, fix the issues and try again.

### Commit Message Format

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### Pre-Commit Hook

The pre-commit hook automatically runs when you commit CLI changes. It will:
1. Run unit tests (must pass)
2. Check code coverage (75% minimum)
3. Run E2E tests (if server is running)
4. Remind you to do manual testing

**If tests fail:**
- Read the error message
- Fix the issue
- Run `./cli/run_all_tests.sh` again
- Commit again

**To bypass (emergency only):**
```bash
git commit --no-verify
```

⚠️ **Warning:** Only bypass the hook if you have a very good reason. Broken code should not be committed.

### Testing Guidelines

#### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution (< 1 second per test)
- Located in `cli/tests/test_*.py`

#### Integration Tests
- Test component interactions
- Use real objects when possible
- Marked with `@pytest.mark.integration`

#### E2E Tests
- Test full workflows
- Require running server
- Located in `cli/test_e2e.py`

#### Manual Tests
- Always required before declaring feature complete
- Follow checklist in `cli/TESTING_CHECKLIST.md`
- Test actual user experience

### Common Issues

#### Tests Pass But App Doesn't Work
This happens when tests mock away real problems. Always do manual testing!

#### Import Errors in Tests
```bash
cd cli
export PYTHONPATH="$(pwd):$PYTHONPATH"
pytest tests/
```

#### Coverage Too Low
Add tests for uncovered code or mark as skip if testing is not practical.

#### E2E Tests Fail
Ensure server is running on `localhost:8000` without Firebase auth.

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused
- Comment complex logic

### Pull Requests

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Keep PRs focused and small
5. Reference related issues

### Questions?

Open an issue or ask in discussions!

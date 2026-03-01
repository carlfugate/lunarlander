# CLI Testing Documentation

This directory contains comprehensive tests for the Lunar Lander CLI client following CI/CD best practices.

## Test Structure

```
cli/tests/
├── conftest.py                      # Test fixtures and configuration
├── test_game_state.py              # Unit tests for game state management
├── test_terminal_caps.py           # Unit tests for terminal capabilities
├── test_websocket_client.py        # Unit tests for WebSocket client
├── test_renderer.py                # Unit tests for terminal renderer
├── test_input_handler.py           # Unit tests for input handling
└── test_terminal_client_integration.py  # Integration tests
```

## Running Tests

### Local Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python run_tests.py

# Run specific test categories
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests only
pytest tests/ -m "not slow"    # Skip slow tests

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### CI/CD Pipeline

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Changes to `cli/` directory

The pipeline runs tests on Python 3.9, 3.10, and 3.11.

## Test Categories

### Unit Tests
- **game_state.py**: State management, data updates, coordinate scaling
- **terminal_caps.py**: Terminal capability detection, color/unicode support
- **websocket_client.py**: WebSocket connection, message handling, HTTP requests
- **renderer.py**: Terminal rendering, game visualization, HUD display
- **input_handler.py**: Keyboard input, action mapping, event handling

### Integration Tests
- **terminal_client.py**: Full game session simulation, component interaction
- End-to-end workflows: play mode, spectate mode, replay mode
- Error handling and recovery scenarios

## Test Fixtures

Key fixtures available in `conftest.py`:
- `mock_terminal`: Mocked blessed Terminal
- `sample_game_data`: Complete game state data
- `mock_websocket`: Async WebSocket mock
- `mock_keyboard`: Keyboard library mock
- `mock_console`: Rich console mock

## Mocking Strategy

- **WebSocket**: Mock connections and message flows
- **Terminal**: Mock terminal capabilities and I/O
- **Keyboard**: Mock input events and key handling
- **HTTP**: Mock aiohttp sessions for API calls

## Coverage Goals

- Minimum 90% line coverage
- 100% coverage for critical paths (game logic, WebSocket handling)
- Edge case coverage for error conditions

## Best Practices

1. **Isolation**: Each test is independent with proper setup/teardown
2. **Mocking**: External dependencies are mocked to ensure reliability
3. **Async Testing**: Proper async/await patterns with pytest-asyncio
4. **Parametrization**: Multiple scenarios tested with @pytest.mark.parametrize
5. **Markers**: Tests categorized with custom markers (unit, integration, slow)

## Continuous Integration

GitHub Actions workflow (`.github/workflows/cli-tests.yml`):
- Multi-Python version testing
- Dependency caching
- Code linting with flake8
- Coverage reporting to Codecov
- Separate unit and integration test runs
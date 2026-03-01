import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from blessed import Terminal

@pytest.fixture
def mock_terminal():
    """Mock terminal for testing terminal capabilities."""
    term = Mock(spec=Terminal)
    term.width = 80
    term.height = 24
    term.number_of_colors = 256
    term.does_styling = True
    term.move_up = "\x1b[A"
    term.clear_eol = "\x1b[K"
    term.clear = "\x1b[2J"
    term.bold = "\x1b[1m"
    term.underline = "\x1b[4m"
    term.reverse = "\x1b[7m"
    term.normal = "\x1b[0m"
    term.color = lambda x: f"\x1b[38;5;{x}m"
    term.color_rgb = lambda r, g, b: f"\x1b[38;2;{r};{g};{b}m"
    term.blue = "\x1b[34m"
    term.green = "\x1b[32m"
    term.yellow = "\x1b[33m"
    term.red = "\x1b[31m"
    return term

@pytest.fixture
def sample_game_data():
    """Sample game data for testing."""
    return {
        'terrain': {'points': [(0, 100), (100, 150), (200, 120), (300, 180)]},
        'lander': {'x': 150, 'y': 200, 'rotation': 0, 'fuel': 500},
        'constants': {'terrain_width': 1200, 'terrain_height': 800},
        'telemetry': {'speed': 5.2, 'altitude': 150, 'thrusting': False}
    }

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock()
    ws.close = AsyncMock()
    return ws

@pytest.fixture
def mock_keyboard():
    """Mock keyboard library."""
    keyboard = Mock()
    keyboard.on_press_key = Mock()
    keyboard.on_release_key = Mock()
    keyboard.unhook_all = Mock()
    return keyboard

@pytest.fixture
def mock_console():
    """Mock Rich console."""
    console = Mock()
    console.size = (80, 24)
    console.clear = Mock()
    console.print = Mock()
    return console

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for HTTP requests."""
    session = AsyncMock()
    response = AsyncMock()
    response.json = AsyncMock(return_value={"status": "ok"})
    session.get.return_value.__aenter__ = AsyncMock(return_value=response)
    session.get.return_value.__aexit__ = AsyncMock(return_value=None)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session

@pytest.fixture
def game_over_data():
    """Sample game over data."""
    return {
        'landed': True,
        'crashed': False,
        'score': 1000,
        'fuel_remaining': 250
    }

@pytest.fixture
def telemetry_data():
    """Sample telemetry data."""
    return {
        'lander': {'x': 150, 'y': 200, 'rotation': 0.2, 'fuel': 400},
        'speed': 4.5,
        'altitude': 180,
        'thrusting': True,
        'timestamp': 1234567890
    }
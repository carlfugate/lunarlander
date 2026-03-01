import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from terminal_client import TerminalClient

class TestTerminalClientIntegration:
    @pytest.fixture
    def mock_components(self):
        """Mock all components for integration testing."""
        with patch('terminal_client.TerminalCapabilities') as mock_caps, \
             patch('terminal_client.GameState') as mock_state, \
             patch('terminal_client.WebSocketClient') as mock_ws, \
             patch('terminal_client.TerminalRenderer') as mock_renderer, \
             patch('terminal_client.InputHandler') as mock_input, \
             patch('terminal_client.Console') as mock_console:
            
            # Setup mocks
            mock_caps_instance = Mock()
            mock_caps.return_value = mock_caps_instance
            
            mock_state_instance = Mock()
            mock_state.return_value = mock_state_instance
            
            mock_ws_instance = AsyncMock()
            mock_ws.return_value = mock_ws_instance
            
            mock_renderer_instance = Mock()
            mock_renderer.return_value = mock_renderer_instance
            
            mock_input_instance = Mock()
            mock_input.return_value = mock_input_instance
            
            mock_console_instance = Mock()
            mock_console.return_value = mock_console_instance
            
            yield {
                'caps': mock_caps_instance,
                'state': mock_state_instance,
                'ws': mock_ws_instance,
                'renderer': mock_renderer_instance,
                'input': mock_input_instance,
                'console': mock_console_instance
            }

    def test_init(self, mock_components):
        client = TerminalClient("ws://test.com/ws", "hard", True)
        assert client.uri == "ws://test.com/ws"
        assert client.difficulty == "hard"
        assert client.running is False
        assert client.mode == "play"

    @pytest.mark.asyncio
    async def test_list_games_empty(self, mock_components):
        mock_components['ws'].fetch_games.return_value = []
        
        client = TerminalClient()
        result = await client.list_games()
        
        assert result is None
        mock_components['console'].print.assert_called_with("[yellow]No active games found[/yellow]")

    @pytest.mark.asyncio
    async def test_list_games_with_data(self, mock_components):
        games_data = [
            {"id": 1, "session_id": "abc123", "difficulty": "simple", "spectators": 2},
            {"id": 2, "session_id": "def456", "difficulty": "hard", "spectators": 0}
        ]
        mock_components['ws'].fetch_games.return_value = games_data
        
        with patch('terminal_client.Prompt.ask', return_value="1"):
            client = TerminalClient()
            result = await client.list_games()
            
            assert result == "abc123"

    @pytest.mark.asyncio
    async def test_play_game_flow(self, mock_components):
        # Setup WebSocket message sequence
        messages = [
            {"type": "init", "terrain": [], "lander": {"x": 100, "y": 200}},
            {"type": "telemetry", "lander": {"x": 105, "y": 195}},
            {"type": "game_over", "landed": True}
        ]
        mock_components['ws'].receive_message.side_effect = messages
        mock_components['input'].get_actions.return_value = []
        
        client = TerminalClient()
        client.running = True
        
        # Mock the game loop to run only a few iterations
        with patch('asyncio.sleep') as mock_sleep:
            mock_sleep.side_effect = [None, None, KeyboardInterrupt()]  # Stop after 3 iterations
            
            try:
                await client._game_loop()
            except KeyboardInterrupt:
                pass
        
        # Verify state updates were called
        mock_components['state'].update_from_init.assert_called()
        mock_components['state'].update_from_telemetry.assert_called()
        mock_components['state'].update_from_game_over.assert_called()

    @pytest.mark.asyncio
    async def test_handle_input_actions(self, mock_components):
        mock_components['input'].get_actions.return_value = ['thrust_on', 'rotate_left']
        
        client = TerminalClient()
        await client._handle_input()
        
        # Should send both actions
        assert mock_components['ws'].send_input.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_quit_action(self, mock_components):
        mock_components['input'].get_actions.return_value = ['quit']
        
        client = TerminalClient()
        client.running = True
        
        await client._handle_input()
        
        assert client.running is False

    @pytest.mark.asyncio
    async def test_spectate_mode_setup(self, mock_components):
        client = TerminalClient()
        
        await client.spectate("test_session")
        
        mock_components['ws'].spectate.assert_called_once_with("test_session")
        assert client.mode == "spectate"

    @pytest.mark.asyncio
    async def test_cleanup_on_exit(self, mock_components):
        client = TerminalClient()
        client.running = True
        
        await client.cleanup()
        
        mock_components['input'].stop.assert_called_once()
        mock_components['ws'].close.assert_called_once()
        assert client.running is False

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_components):
        mock_components['ws'].connect.side_effect = ConnectionError("Connection failed")
        
        client = TerminalClient()
        
        with pytest.raises(ConnectionError):
            await client.connect()

    @pytest.mark.asyncio
    async def test_message_processing_error_handling(self, mock_components):
        # Simulate malformed message
        mock_components['ws'].receive_message.side_effect = [
            {"type": "unknown_type", "data": "invalid"},
            {"type": "game_over", "landed": True}
        ]
        mock_components['input'].get_actions.return_value = []
        
        client = TerminalClient()
        client.running = True
        
        with patch('asyncio.sleep') as mock_sleep:
            mock_sleep.side_effect = [None, KeyboardInterrupt()]
            
            try:
                await client._game_loop()
            except KeyboardInterrupt:
                pass
        
        # Should continue processing despite unknown message type
        mock_components['renderer'].render_frame.assert_called()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_game_session_simulation(self, mock_components):
        """Test a complete game session from start to finish."""
        # Setup complete message sequence
        init_msg = {
            "type": "init",
            "terrain": {"points": [(0, 100), (100, 150)]},
            "lander": {"x": 100, "y": 200, "fuel": 1000},
            "constants": {"terrain_width": 1200, "terrain_height": 800}
        }
        
        telemetry_msgs = [
            {"type": "telemetry", "lander": {"x": 105, "y": 195}, "speed": 2.0},
            {"type": "telemetry", "lander": {"x": 110, "y": 190}, "speed": 3.0},
        ]
        
        game_over_msg = {"type": "game_over", "landed": True, "crashed": False}
        
        messages = [init_msg] + telemetry_msgs + [game_over_msg]
        mock_components['ws'].receive_message.side_effect = messages
        
        # Simulate user input sequence
        input_sequence = [
            ['thrust_on'],
            ['thrust_on', 'rotate_left'],
            ['thrust_off'],
            []
        ]
        mock_components['input'].get_actions.side_effect = input_sequence
        
        client = TerminalClient()
        client.running = True
        
        with patch('asyncio.sleep') as mock_sleep:
            mock_sleep.side_effect = [None] * len(messages) + [KeyboardInterrupt()]
            
            try:
                await client._game_loop()
            except KeyboardInterrupt:
                pass
        
        # Verify complete flow
        mock_components['state'].update_from_init.assert_called_once()
        assert mock_components['state'].update_from_telemetry.call_count == 2
        mock_components['state'].update_from_game_over.assert_called_once()
        assert mock_components['ws'].send_input.call_count >= 3  # At least 3 input actions sent
import pytest
from unittest.mock import Mock, patch
from renderer import TerminalRenderer

class TestTerminalRenderer:
    @patch('renderer.Console')
    def test_init_unicode_colors(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        terminal_caps = {'unicode': True, 'colors': True}
        renderer = TerminalRenderer(terminal_caps)
        
        assert renderer.unicode is True
        assert renderer.colors is True
        assert renderer.terrain_chars['flat'] == '─'
        assert renderer.lander_chars['up'] == '▲'

    @patch('renderer.Console')
    def test_init_ascii_no_colors(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        terminal_caps = {'unicode': False, 'colors': False}
        renderer = TerminalRenderer(terminal_caps)
        
        assert renderer.unicode is False
        assert renderer.colors is False
        assert renderer.terrain_chars['flat'] == '-'
        assert renderer.lander_chars['up'] == '^'

    @patch('renderer.Console')
    @patch('renderer.Layout')
    @patch('renderer.Panel')
    def test_render_frame_play_mode(self, mock_panel, mock_layout_class, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        # Create a proper mock layout with split_column method
        mock_game_panel = Mock()
        mock_hud_panel = Mock()
        mock_layout = Mock()
        mock_layout.__getitem__ = Mock(side_effect=lambda key: mock_game_panel if key == "game" else mock_hud_panel)
        mock_layout.split_column = Mock()
        mock_layout_class.return_value = mock_layout
        
        renderer = TerminalRenderer({'unicode': True, 'colors': True})
        game_state = {
            'lander': {'x': 100, 'y': 200, 'rotation': 0, 'fuel': 500},
            'telemetry': {'speed': 5.0, 'altitude': 150, 'thrusting': False}
        }
        
        renderer.render_frame(game_state)
        
        # Should print (cursor home + layout), not clear
        assert mock_console.print.call_count >= 1

    @patch('renderer.Console')
    def test_draw_game_area(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        renderer = TerminalRenderer({'unicode': True, 'colors': True})
        game_state = {
            'terrain': [100, 120, 110, 130],
            'lander': {'x': 600, 'y': 400, 'angle': 0},
            'landing_zones': [{'start': 500, 'end': 700, 'y': 100}]
        }
        
        result = renderer._draw_game_area(game_state)
        assert result is not None

    @patch('renderer.Console')
    def test_draw_hud_with_telemetry(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        renderer = TerminalRenderer({'unicode': True, 'colors': True})
        game_state = {
            'lander': {'fuel': 250, 'rotation': 0.5},
            'telemetry': {'speed': 3.2, 'altitude': 120, 'thrusting': True}
        }
        
        result = renderer._draw_hud(game_state)
        assert result is not None

    @patch('renderer.Console')
    def test_draw_hud_replay_mode(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        renderer = TerminalRenderer({'unicode': True, 'colors': True})
        game_state = {
            'lander': {'fuel': 100, 'rotation': 1.0},
            'telemetry': {'speed': 8.5, 'altitude': 50, 'thrusting': False}
        }
        
        result = renderer._draw_hud(game_state, mode="replay")
        assert result is not None

    @patch('renderer.Console')
    def test_draw_lander_different_angles(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        renderer = TerminalRenderer({'unicode': True, 'colors': True})
        grid = [[' ' for _ in range(76)] for _ in range(18)]
        
        # Test different angles
        game_states = [
            {'lander': {'x': 600, 'y': 400, 'angle': 0}},    # up
            {'lander': {'x': 600, 'y': 400, 'angle': 90}},   # right
            {'lander': {'x': 600, 'y': 400, 'angle': -90}},  # left
        ]
        
        for state in game_states:
            renderer._draw_lander(grid, state, 76/1200, 18/800)
            # Should not raise exception

    @patch('renderer.Console')
    def test_draw_terrain_empty(self, mock_console_class, mock_console):
        mock_console.size = (80, 24)
        mock_console_class.return_value = mock_console
        
        renderer = TerminalRenderer({'unicode': True, 'colors': True})
        grid = [[' ' for _ in range(76)] for _ in range(18)]
        game_state = {'terrain': []}
        
        renderer._draw_terrain(grid, game_state, 1.0, 1.0)
        # Should not raise exception
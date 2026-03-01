import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from input_handler import InputHandler

class TestInputHandler:
    def test_init_with_keyboard(self):
        with patch('input_handler.keyboard', create=True) as mock_keyboard:
            handler = InputHandler()
            assert handler.use_keyboard is True
            assert handler.keyboard == mock_keyboard

    def test_init_without_keyboard(self):
        with patch('input_handler.keyboard', side_effect=ImportError):
            with patch('input_handler.Terminal') as mock_terminal:
                handler = InputHandler()
                assert handler.use_keyboard is False
                assert hasattr(handler, 'term')

    def test_init_keyboard_permission_error(self):
        with patch('input_handler.keyboard', side_effect=PermissionError):
            with patch('input_handler.Terminal') as mock_terminal:
                handler = InputHandler()
                assert handler.use_keyboard is False

    def test_start_keyboard_mode(self, mock_keyboard):
        with patch('input_handler.keyboard', mock_keyboard):
            handler = InputHandler()
            handler._setup_keyboard_hooks = Mock()
            
            handler.start()
            assert handler.running is True
            assert len(handler.actions) == 0
            handler._setup_keyboard_hooks.assert_called_once()

    def test_start_blessed_mode(self):
        with patch('input_handler.keyboard', side_effect=ImportError):
            with patch('input_handler.Terminal') as mock_terminal:
                with patch('input_handler.threading.Thread') as mock_thread:
                    handler = InputHandler()
                    handler.start()
                    assert handler.running is True
                    mock_thread.assert_called_once()

    def test_stop_keyboard_mode(self, mock_keyboard):
        with patch('input_handler.keyboard', mock_keyboard):
            handler = InputHandler()
            handler.running = True
            handler.stop()
            assert handler.running is False
            mock_keyboard.unhook_all.assert_called_once()

    def test_stop_blessed_mode(self):
        with patch('input_handler.keyboard', side_effect=ImportError):
            with patch('input_handler.Terminal'):
                handler = InputHandler()
                handler.thread = Mock()
                handler.thread.join = Mock()
                handler.running = True
                
                handler.stop()
                assert handler.running is False
                handler.thread.join.assert_called_once_with(timeout=0.1)

    def test_get_actions(self):
        handler = InputHandler()
        handler.actions = {'thrust', 'rotate_left'}
        actions = handler.get_actions()
        assert set(actions) == {'thrust', 'rotate_left'}

    def test_on_key_press_thrust(self):
        handler = InputHandler()
        handler._on_key_press('thrust')
        assert 'thrust_on' in handler.actions
        assert 'thrust_off' not in handler.actions

    def test_on_key_press_space_toggle(self):
        handler = InputHandler()
        # First press
        handler._on_key_press(' ')
        assert ' ' in handler.actions
        # Second press (toggle off)
        handler._on_key_press(' ')
        assert ' ' not in handler.actions

    def test_on_key_press_other_actions(self):
        handler = InputHandler()
        handler._on_key_press('rotate_left')
        assert 'rotate_left' in handler.actions

    def test_on_key_release_thrust(self):
        handler = InputHandler()
        handler.actions.add('thrust_on')
        handler._on_key_release('thrust')
        assert 'thrust_off' in handler.actions
        assert 'thrust_on' not in handler.actions

    def test_on_key_release_other_actions(self):
        handler = InputHandler()
        handler.actions.add('rotate_left')
        handler._on_key_release('rotate_left')
        assert 'rotate_left' not in handler.actions

    def test_handle_blessed_key_mapping(self):
        with patch('input_handler.keyboard', side_effect=ImportError):
            with patch('input_handler.Terminal'):
                handler = InputHandler()
                handler._on_key_press = Mock()
                
                # Test key mappings
                test_cases = [
                    ('KEY_UP', 'thrust'),
                    ('w', 'thrust'),
                    ('KEY_LEFT', 'rotate_left'),
                    ('a', 'rotate_left'),
                    ('KEY_RIGHT', 'rotate_right'),
                    ('d', 'rotate_right'),
                    (' ', ' '),
                    ('KEY_ESCAPE', 'quit'),
                    ('q', 'quit')
                ]
                
                for key, expected_action in test_cases:
                    handler._handle_blessed_key(key)
                    handler._on_key_press.assert_called_with(expected_action)

    def test_handle_blessed_key_unknown(self):
        with patch('input_handler.keyboard', side_effect=ImportError):
            with patch('input_handler.Terminal'):
                handler = InputHandler()
                handler._on_key_press = Mock()
                
                handler._handle_blessed_key('unknown_key')
                handler._on_key_press.assert_not_called()

    def test_setup_keyboard_hooks_permission_error(self, mock_keyboard):
        mock_keyboard.on_press_key.side_effect = PermissionError()
        with patch('input_handler.keyboard', mock_keyboard):
            with patch('input_handler.Terminal') as mock_terminal:
                with patch('input_handler.threading.Thread') as mock_thread:
                    handler = InputHandler()
                    handler._setup_keyboard_hooks()
                    # Should fallback to blessed mode
                    assert handler.use_keyboard is False
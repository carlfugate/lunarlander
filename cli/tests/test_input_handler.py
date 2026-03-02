import pytest
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from input_handler import InputHandler

class TestInputHandler:
    def test_init_uses_blessed(self):
        handler = InputHandler()
        assert handler.use_keyboard is False
        assert hasattr(handler, 'term')

    def test_start_blessed_thread(self):
        handler = InputHandler()
        handler.start()
        assert handler.running is True
        assert handler.thread is not None
        handler.stop()

    def test_stop_blessed_thread(self):
        handler = InputHandler()
        handler.start()
        handler.stop()
        assert handler.running is False

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
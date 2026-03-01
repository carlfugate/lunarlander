import pytest
from unittest.mock import patch, Mock
from terminal_caps import TerminalCapabilities

class TestTerminalCapabilities:
    @patch('terminal_caps.Terminal')
    def test_init(self, mock_terminal_class, mock_terminal):
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.term == mock_terminal

    @patch('terminal_caps.Terminal')
    def test_color_support_truecolor(self, mock_terminal_class, mock_terminal):
        mock_terminal.number_of_colors = 16777216
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.color_support == 'truecolor'

    @patch('terminal_caps.Terminal')
    def test_color_support_256(self, mock_terminal_class, mock_terminal):
        mock_terminal.number_of_colors = 256
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.color_support == '256'

    @patch('terminal_caps.Terminal')
    def test_color_support_16(self, mock_terminal_class, mock_terminal):
        mock_terminal.number_of_colors = 16
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.color_support == '16'

    @patch('terminal_caps.Terminal')
    def test_color_support_mono(self, mock_terminal_class, mock_terminal):
        mock_terminal.number_of_colors = 1
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.color_support == 'mono'

    @patch('terminal_caps.Terminal')
    def test_unicode_support(self, mock_terminal_class, mock_terminal):
        mock_terminal.does_styling = True
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.unicode_support is True

    @patch('terminal_caps.Terminal')
    def test_force_ascii_mode(self, mock_terminal_class, mock_terminal):
        mock_terminal.does_styling = True
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities(force_ascii=True)
        assert caps.force_ascii is True
        assert caps.unicode_support is False

    @patch('terminal_caps.Terminal')
    def test_force_ascii_default(self, mock_terminal_class, mock_terminal):
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.force_ascii is False

    @patch('terminal_caps.Terminal')
    def test_dimensions(self, mock_terminal_class, mock_terminal):
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.width == 80
        assert caps.height == 24

    @patch('terminal_caps.Terminal')
    def test_get_charset_unicode(self, mock_terminal_class, mock_terminal):
        mock_terminal.does_styling = True
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        charset = caps.get_charset()
        assert charset['horizontal'] == '─'
        assert charset['vertical'] == '│'

    @patch('terminal_caps.Terminal')
    def test_get_charset_ascii(self, mock_terminal_class, mock_terminal):
        mock_terminal.does_styling = False
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        charset = caps.get_charset()
        assert charset['horizontal'] == '-'
        assert charset['vertical'] == '|'

    @patch('terminal_caps.Terminal')
    def test_get_color_scheme_truecolor(self, mock_terminal_class, mock_terminal):
        mock_terminal.number_of_colors = 16777216
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        colors = caps.get_color_scheme()
        assert 'primary' in colors
        assert 'success' in colors
        assert 'error' in colors

    @patch('terminal_caps.Terminal')
    def test_supports_feature(self, mock_terminal_class, mock_terminal):
        mock_terminal.number_of_colors = 256
        mock_terminal.does_styling = True
        mock_terminal_class.return_value = mock_terminal
        caps = TerminalCapabilities()
        assert caps.supports_feature('colors') is True
        assert caps.supports_feature('unicode') is True
        assert caps.supports_feature('cursor_movement') is True
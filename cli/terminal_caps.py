"""Terminal capability detection using blessed library."""

from blessed import Terminal


class TerminalCapabilities:
    """Detect and manage terminal capabilities for graceful degradation."""
    
    def __init__(self, force_ascii=False):
        self.term = Terminal()
        self.force_ascii = force_ascii
    
    @property
    def color_support(self):
        """Detect color support level: truecolor, 256, 16, or mono."""
        if self.term.number_of_colors >= 16777216:
            return 'truecolor'
        elif self.term.number_of_colors >= 256:
            return '256'
        elif self.term.number_of_colors >= 16:
            return '16'
        else:
            return 'mono'
    
    @property
    def unicode_support(self):
        """Check if terminal supports Unicode characters."""
        if self.force_ascii:
            return False
        return self.term.does_styling
    
    @property
    def is_vt100(self):
        """Check VT100 compatibility."""
        return bool(self.term.move_up and self.term.clear_eol)
    
    @property
    def width(self):
        """Terminal width in columns."""
        return self.term.width
    
    @property
    def height(self):
        """Terminal height in rows."""
        return self.term.height
    
    def get_charset(self):
        """Get appropriate character set based on Unicode support."""
        if self.unicode_support:
            return {
                'horizontal': '─',
                'vertical': '│',
                'top_left': '┌',
                'top_right': '┐',
                'bottom_left': '└',
                'bottom_right': '┘',
                'cross': '┼',
                'bullet': '•',
                'arrow': '→'
            }
        else:
            return {
                'horizontal': '-',
                'vertical': '|',
                'top_left': '+',
                'top_right': '+',
                'bottom_left': '+',
                'bottom_right': '+',
                'cross': '+',
                'bullet': '*',
                'arrow': '->'
            }
    
    def get_color_scheme(self):
        """Get color scheme based on terminal capabilities."""
        color_support = self.color_support
        
        if color_support == 'truecolor':
            return {
                'primary': self.term.color_rgb(0, 150, 255),
                'success': self.term.color_rgb(0, 200, 0),
                'warning': self.term.color_rgb(255, 165, 0),
                'error': self.term.color_rgb(255, 0, 0),
                'reset': self.term.normal
            }
        elif color_support == '256':
            return {
                'primary': self.term.color(39),
                'success': self.term.color(46),
                'warning': self.term.color(214),
                'error': self.term.color(196),
                'reset': self.term.normal
            }
        elif color_support == '16':
            return {
                'primary': self.term.blue,
                'success': self.term.green,
                'warning': self.term.yellow,
                'error': self.term.red,
                'reset': self.term.normal
            }
        else:
            return {
                'primary': '',
                'success': '',
                'warning': '',
                'error': '',
                'reset': ''
            }
    
    def supports_feature(self, feature):
        """Check if terminal supports specific feature."""
        features = {
            'colors': self.color_support != 'mono',
            'unicode': self.unicode_support,
            'cursor_movement': bool(self.term.move_up),
            'clear_screen': bool(self.term.clear),
            'bold': bool(self.term.bold),
            'underline': bool(self.term.underline),
            'reverse': bool(self.term.reverse)
        }
        return features.get(feature, False)
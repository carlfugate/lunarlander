from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live


class TerminalRenderer:
    def __init__(self, terminal_caps):
        self.console = Console()
        self.width, self.height = self.console.size
        self.live = None
        
        # Handle both dict and TerminalCapabilities object
        if isinstance(terminal_caps, dict):
            self.unicode = terminal_caps.get('unicode', True)
            self.colors = terminal_caps.get('colors', True)
        else:
            self.unicode = terminal_caps.unicode_support
            self.colors = terminal_caps.color_support != 'mono'
        
        # Character sets based on capabilities
        if self.unicode:
            self.terrain_chars = {'flat': '─', 'up': '╱', 'down': '╲'}
            self.lander_chars = {'up': '▲', 'left': '◄', 'right': '►', 'down': '▼'}
        else:
            self.terrain_chars = {'flat': '-', 'up': '/', 'down': '\\'}
            self.lander_chars = {'up': '^', 'left': '<', 'right': '>', 'down': 'v'}
    
    def render_frame(self, game_state, mode=None):
        layout = Layout()
        layout.split_column(
            Layout(name="game", ratio=4),
            Layout(name="hud", size=3)
        )
        
        # Game area
        title = "Lunar Lander"
        if mode == "replay":
            title = "🔄 REPLAY - Lunar Lander"
        elif mode == "spectate":
            title = "👁️ SPECTATING - Lunar Lander"
        game_content = self._draw_game_area(game_state)
        layout["game"].update(Panel(game_content, title=title))
        
        # HUD
        hud_content = self._draw_hud(game_state, mode)
        layout["hud"].update(Panel(hud_content, title="HUD"))
        
        # Use home position instead of clear to avoid flicker
        self.console.print("\033[H", end="")  # Move cursor to home
        self.console.print(layout)
    
    def _draw_game_area(self, game_state):
        lines = []
        game_height = self.height - 6  # Account for panels and HUD
        game_width = self.width - 4    # Account for panel borders
        
        # Scale game coordinates (1200x800) to terminal size
        scale_x = game_width / 1200
        scale_y = game_height / 800
        
        # Initialize empty grid
        grid = [[' ' for _ in range(game_width)] for _ in range(game_height)]
        
        # Draw terrain
        self._draw_terrain(grid, game_state, scale_x, scale_y)
        
        # Draw landing zones
        self._draw_landing_zones(grid, game_state, scale_x, scale_y)
        
        # Draw lander
        self._draw_lander(grid, game_state, scale_x, scale_y)
        
        # Convert grid to text
        for row in grid:
            lines.append(''.join(row))
        
        return Text('\n'.join(lines))
    
    def _get_attr(self, obj, key, default=None):
        """Get attribute from object or dict."""
        if hasattr(obj, key):
            return getattr(obj, key, default)
        elif isinstance(obj, dict):
            return obj.get(key, default)
        return default
    
    def _draw_terrain(self, grid, game_state, scale_x, scale_y):
        terrain = self._get_attr(game_state, 'terrain')
        if not terrain:
            return
        
        # Terrain is a dict with 'points' key - list of [x, y] coordinates
        points = self._get_attr(terrain, 'points', [])
        if not points or len(points) < 2:
            return
            
        height = len(grid)
        width = len(grid[0])
        
        # Draw lines between consecutive terrain points
        # Server uses Y=0 at top, Y=800 at bottom
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # Scale to screen coordinates (Y already increases downward)
            sx1 = int(x1 * scale_x)
            sy1 = int(y1 * scale_y)
            sx2 = int(x2 * scale_x)
            sy2 = int(y2 * scale_y)
            
            # Draw line using simple interpolation
            if sx1 == sx2:
                # Vertical line
                for y in range(min(sy1, sy2), max(sy1, sy2) + 1):
                    if 0 <= sx1 < width and 0 <= y < height:
                        grid[y][sx1] = self.terrain_chars['flat']
            else:
                # Interpolate between points
                steps = abs(sx2 - sx1)
                for step in range(steps + 1):
                    t = step / steps if steps > 0 else 0
                    x = int(sx1 + (sx2 - sx1) * t)
                    y = int(sy1 + (sy2 - sy1) * t)
                    if 0 <= x < width and 0 <= y < height:
                        grid[y][x] = self.terrain_chars['flat']
    
    def _draw_lander(self, grid, game_state, scale_x, scale_y):
        lander = self._get_attr(game_state, 'lander', {})
        if not lander:
            return
        # Server uses Y=0 at top, Y=800 at bottom (same as screen)
        x = int(self._get_attr(lander, 'x', 0) * scale_x)
        y = int(self._get_attr(lander, 'y', 0) * scale_y)
        rotation = self._get_attr(lander, 'rotation', 0)  # In radians
        
        # Convert radians to degrees
        angle_deg = rotation * 57.2958  # 180/π
        
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
            # Choose lander character based on angle (in degrees)
            if -45 <= angle_deg <= 45:
                char = self.lander_chars['up']
            elif 45 < angle_deg <= 135:
                char = self.lander_chars['right']
            elif angle_deg > 135 or angle_deg < -135:
                char = self.lander_chars['down']
            else:  # -135 to -45
                char = self.lander_chars['left']
            
            grid[y][x] = char
    
    def _draw_landing_zones(self, grid, game_state, scale_x, scale_y):
        landing_zones = self._get_attr(game_state, 'landing_zones', [])
        if not landing_zones:
            return
        height = len(grid)
        
        for zone in landing_zones:
            start_x = int(self._get_attr(zone, 'start', 0) * scale_x)
            end_x = int(self._get_attr(zone, 'end', 0) * scale_x)
            zone_y = int(self._get_attr(zone, 'y', 0) * scale_y)
            
            # Highlight landing zone
            for x in range(start_x, min(end_x + 1, len(grid[0]))):
                if 0 <= x < len(grid[0]) and 0 <= zone_y < height:
                    if grid[zone_y][x] == ' ':
                        grid[zone_y][x] = '='
    
    def _draw_hud(self, game_state, mode=None):
        lander = self._get_attr(game_state, 'lander', {})
        telemetry = self._get_attr(game_state, 'telemetry', {})
        if not lander:
            lander = {}
        if not telemetry:
            telemetry = {}
        fuel = self._get_attr(lander, 'fuel', 0)
        speed = self._get_attr(telemetry, 'speed', 0)
        altitude = self._get_attr(telemetry, 'altitude', 0)
        angle = abs(self._get_attr(lander, 'rotation', 0) * 57.3)
        thrusting = self._get_attr(telemetry, 'thrusting', False)
        
        hud_text = Text()
        
        # Mode indicators
        if mode == "replay":
            hud_text.append("REPLAY", style="bold red" if self.colors else None)
            hud_text.append("  ")
        elif mode == "spectate":
            hud_text.append("SPECTATING", style="bold blue" if self.colors else None)
            hud_text.append("  ")
        
        # Fuel
        fuel_color = "red" if fuel < 100 else "yellow" if fuel < 300 else "green"
        hud_text.append(f"Fuel: {fuel:.0f}", style=fuel_color if self.colors else None)
        hud_text.append("  ")
        
        # Speed with safety indicator
        speed_color = "green" if speed < 5.0 else "yellow" if speed < 10.0 else "red"
        hud_text.append(f"Speed: {speed:.1f}m/s", style=speed_color if self.colors else None)
        if speed < 5.0:
            hud_text.append(" ✓", style="green" if self.colors else None)
        else:
            hud_text.append(" ✗", style="red" if self.colors else None)
        hud_text.append("  ")
        
        # Altitude
        hud_text.append(f"Alt: {altitude:.0f}m")
        hud_text.append("  ")
        
        # Angle with safety indicator
        angle_color = "green" if angle < 17 else "yellow" if angle < 30 else "red"
        hud_text.append(f"Angle: {angle:.0f}°", style=angle_color if self.colors else None)
        if angle < 17:
            hud_text.append(" ✓", style="green" if self.colors else None)
        
        # Thrust indicator
        if thrusting:
            flame = "🔥" if self.unicode else "*"
            hud_text.append(f"  THRUST {flame}", style="yellow" if self.colors else None)
        
        return hud_text
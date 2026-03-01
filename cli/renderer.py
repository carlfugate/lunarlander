from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text


class TerminalRenderer:
    def __init__(self, terminal_caps):
        self.console = Console()
        self.width, self.height = self.console.size
        self.unicode = terminal_caps.get('unicode', True)
        self.colors = terminal_caps.get('colors', True)
        
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
        
        self.console.clear()
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
    
    def _draw_terrain(self, grid, game_state, scale_x, scale_y):
        terrain = game_state.get('terrain', [])
        height = len(grid)
        
        for i, terrain_height in enumerate(terrain):
            x = int(i * scale_x)
            y = height - int(terrain_height * scale_y) - 1
            
            if 0 <= x < len(grid[0]) and 0 <= y < height:
                # Simple terrain representation
                grid[y][x] = self.terrain_chars['flat']
    
    def _draw_lander(self, grid, game_state, scale_x, scale_y):
        lander = game_state.get('lander', {})
        x = int(lander.get('x', 0) * scale_x)
        y = len(grid) - int(lander.get('y', 0) * scale_y) - 1
        angle = lander.get('angle', 0)
        
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
            # Choose lander character based on angle
            if -45 <= angle <= 45:
                char = self.lander_chars['up']
            elif angle > 45:
                char = self.lander_chars['right']
            else:
                char = self.lander_chars['left']
            
            grid[y][x] = char
    
    def _draw_landing_zones(self, grid, game_state, scale_x, scale_y):
        landing_zones = game_state.get('landing_zones', [])
        height = len(grid)
        
        for zone in landing_zones:
            start_x = int(zone.get('start', 0) * scale_x)
            end_x = int(zone.get('end', 0) * scale_x)
            zone_y = height - int(zone.get('y', 0) * scale_y) - 1
            
            # Highlight landing zone
            for x in range(start_x, min(end_x + 1, len(grid[0]))):
                if 0 <= x < len(grid[0]) and 0 <= zone_y < height:
                    if grid[zone_y][x] == ' ':
                        grid[zone_y][x] = '='
    
    def _draw_hud(self, game_state, mode=None):
        lander = game_state.get('lander', {})
        telemetry = game_state.get('telemetry', {})
        fuel = lander.get('fuel', 0)
        speed = telemetry.get('speed', 0)
        altitude = telemetry.get('altitude', 0)
        angle = abs(lander.get('rotation', 0) * 57.3)
        thrusting = telemetry.get('thrusting', False)
        
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
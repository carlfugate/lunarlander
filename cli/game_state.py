class GameState:
    def __init__(self):
        self.terrain = None
        self.lander = None
        self.telemetry = None
        self.constants = None
        self.game_over = False
        self.landed = False
        self.crashed = False

    def update_from_init(self, data):
        self.terrain = data.get('terrain')
        self.lander = data.get('lander')
        self.constants = data.get('constants')

    def update_from_telemetry(self, data):
        self.telemetry = data
        self.lander = data.get('lander')

    def update_from_game_over(self, data):
        self.game_over = True
        self.landed = data.get('landed', False)
        self.crashed = data.get('crashed', False)

    def get_scaled_terrain(self, width, height):
        if not self.terrain:
            return []
        
        terrain_width = self.constants.get('terrain_width', 1200)
        terrain_height = self.constants.get('terrain_height', 800)
        
        x_scale = width / terrain_width
        y_scale = height / terrain_height
        
        return [(int(x * x_scale), int(y * y_scale)) for x, y in self.terrain['points']]

    def get_lander_char(self, use_unicode=True):
        if not self.lander:
            return '^'
        
        rotation = self.lander.get('rotation', 0)
        
        if use_unicode:
            if -0.785 <= rotation <= 0.785:  # -45° to 45°
                return '▲'
            elif 0.785 < rotation <= 2.356:  # 45° to 135°
                return '►'
            elif rotation > 2.356 or rotation < -2.356:  # 135° to 225°
                return '▼'
            else:  # -135° to -45°
                return '◄'
        else:
            if -0.785 <= rotation <= 0.785:
                return '^'
            elif 0.785 < rotation <= 2.356:
                return '>'
            elif rotation > 2.356 or rotation < -2.356:
                return 'v'
            else:
                return '<'
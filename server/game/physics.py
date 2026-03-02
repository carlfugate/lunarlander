import math

GRAVITY = 1.62  # m/s² (lunar gravity)
THRUST_POWER = 8.0  # m/s² acceleration (increased for better control)
ROTATION_SPEED = 3.0  # radians/s
INITIAL_FUEL = 1000.0
FUEL_CONSUMPTION_RATE = 10.0  # units/s when thrusting

# Fuel presets for different game modes
FUEL_PRESETS = {
    'unlimited': 1000.0,
    'standard': 1000.0,
    'limited': 300.0,    # ~30 seconds of thrust
    'challenge': 150.0,  # ~15 seconds of thrust
}

class Lander:
    def __init__(self, x=600, y=100, fuel_mode='standard'):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.rotation = 0.0  # radians, 0 = pointing up
        self.fuel = FUEL_PRESETS.get(fuel_mode, INITIAL_FUEL)
        self.max_fuel = self.fuel  # Track max for percentage calculations
        self.crashed = False
        self.landed = False
        
    def update(self, dt, thrust, rotate):
        if self.crashed or self.landed:
            return
            
        # Apply rotation
        if rotate == "left":
            self.rotation -= ROTATION_SPEED * dt
        elif rotate == "right":
            self.rotation += ROTATION_SPEED * dt
        
        # Normalize rotation to -pi to pi
        while self.rotation > math.pi:
            self.rotation -= 2 * math.pi
        while self.rotation < -math.pi:
            self.rotation += 2 * math.pi
            
        # Apply thrust
        if thrust and self.fuel > 0:
            thrust_x = math.sin(self.rotation) * THRUST_POWER * dt
            thrust_y = -math.cos(self.rotation) * THRUST_POWER * dt
            self.vx += thrust_x
            self.vy += thrust_y
            self.fuel -= FUEL_CONSUMPTION_RATE * dt
            self.fuel = max(0, self.fuel)
            
        # Apply gravity
        self.vy += GRAVITY * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
    def check_collision(self, terrain_y, is_landing_zone=False):
        # Check collision for nose (top of triangle at -30 in local coords)
        nose_x = self.x
        nose_y = self.y - 30 * math.cos(self.rotation)
        
        # Check collision for bottom or nose
        if self.y >= terrain_y or nose_y >= terrain_y:
            speed = math.sqrt(self.vx**2 + self.vy**2)
            angle_upright = abs(self.rotation) < 0.3  # ~17 degrees
            angle_degrees = abs(self.rotation) * 180 / math.pi
            
            import time
            timestamp = time.time()
            
            if is_landing_zone and angle_upright and speed < 5.0:  # Increased from 2.0 to 5.0
                self.landed = True
                self.y = terrain_y
                self.vx = 0
                self.vy = 0
            else:
                self.crashed = True
                self.y = terrain_y
                
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "rotation": self.rotation,
            "fuel": self.fuel,
            "crashed": self.crashed,
            "landed": self.landed
        }

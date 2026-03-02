"""
Game metrics data structure - minimal and efficient
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class GameMetrics:
    """Lightweight game metrics - only essential data"""
    # Identifiers
    game_id: str
    player_id: str
    difficulty: str
    started_at: float
    fuel_mode: str = "standard"  # standard, limited, challenge, unlimited
    ended_at: Optional[float] = None
    
    # Core results
    landed: bool = False
    crashed: bool = False
    score: int = 0
    duration: float = 0
    
    # Flight characteristics (extremes only)
    max_altitude: float = 0
    min_altitude: float = 0
    max_speed: float = 0
    altitude_at_end: float = 0
    speed_at_end: float = 0
    angle_at_end: float = 0
    
    # Landing quality (if landed)
    landing_speed: float = 0
    landing_angle: float = 0
    
    # Fuel management
    fuel_remaining: int = 0
    fuel_used: int = 0
    thrust_frames: int = 0
    
    # Control metrics
    total_inputs: int = 0
    rotation_count: int = 0
    rotation_changes: int = 0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def is_perfect_landing(self):
        """Check if this was a perfect landing"""
        return (self.landed and 
                self.landing_speed < 2.0 and 
                self.landing_angle < 5.0 and 
                self.fuel_remaining > 800)
    
    def thrust_percentage(self):
        """Calculate percentage of time spent thrusting"""
        if self.duration <= 0:
            return 0
        # Assuming 60 FPS
        total_frames = self.duration * 60
        return (self.thrust_frames / total_frames * 100) if total_frames > 0 else 0

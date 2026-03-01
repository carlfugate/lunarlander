"""
Analytics configuration for conference-optimized metrics
"""
from dataclasses import dataclass


@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    # Time windows
    default_window_hours: int = 8  # Conference day
    max_window_hours: int = 168  # 7 days max
    infinite_mode: bool = False  # Continuous across days
    
    # Update intervals
    cache_ttl_seconds: int = 60  # Refresh every 60 seconds
    
    # Fidelity settings
    recent_events_window: int = 300  # 5 minutes for "recent" stats
    trending_window: int = 3600  # 1 hour for trends
    
    # Performance limits
    max_games_in_memory: int = 10000  # Safety limit
    
    def get_time_window(self):
        """Get time window in seconds"""
        if self.infinite_mode:
            return None  # No limit
        return self.default_window_hours * 3600

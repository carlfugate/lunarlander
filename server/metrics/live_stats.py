"""
Live statistics tracker with incremental aggregation
"""
import time
from collections import deque


class LiveStatsTracker:
    """Tracks real-time statistics with pre-aggregated counters"""
    
    def __init__(self):
        # Pre-aggregated counters (no recalculation needed)
        self.counters = {
            'active_sessions': 0,
            'peak_sessions': 0,
            'total_games': 0,
            'total_landings': 0,
            'total_crashes': 0,
            'total_score': 0,
            'total_fuel_burned': 0,
            'total_flight_time': 0,
        }
        
        # Per-difficulty (nested counters)
        self.by_difficulty = {
            'simple': {'games': 0, 'landings': 0, 'total_score': 0},
            'medium': {'games': 0, 'landings': 0, 'total_score': 0},
            'hard': {'games': 0, 'landings': 0, 'total_score': 0},
        }
        
        # Circular buffer for recent events (fixed size, no growth)
        self.recent_events = deque(maxlen=100)  # Auto-drops old events
    
    def session_started(self):
        """Increment active session count"""
        self.counters['active_sessions'] += 1
        self.counters['peak_sessions'] = max(
            self.counters['peak_sessions'], 
            self.counters['active_sessions']
        )
    
    def session_ended(self):
        """Decrement active session count"""
        self.counters['active_sessions'] = max(0, self.counters['active_sessions'] - 1)
    
    def game_completed(self, metrics_dict):
        """Increment counters - O(1) operation"""
        self.counters['total_games'] += 1
        self.counters['total_score'] += metrics_dict['score']
        self.counters['total_fuel_burned'] += metrics_dict['fuel_used']
        self.counters['total_flight_time'] += metrics_dict['duration']
        
        diff = metrics_dict['difficulty']
        if diff in self.by_difficulty:
            self.by_difficulty[diff]['games'] += 1
        
        if metrics_dict['landed']:
            self.counters['total_landings'] += 1
            if diff in self.by_difficulty:
                self.by_difficulty[diff]['landings'] += 1
                self.by_difficulty[diff]['total_score'] += metrics_dict['score']
            self.recent_events.append(('landing', time.time()))
        elif metrics_dict['crashed']:
            self.counters['total_crashes'] += 1
            self.recent_events.append(('crash', time.time()))
    
    def get_stats(self):
        """Return pre-calculated stats - no computation"""
        total = self.counters['total_games']
        
        return {
            'active_sessions': self.counters['active_sessions'],
            'peak_sessions': self.counters['peak_sessions'],
            'total_games': total,
            'total_landings': self.counters['total_landings'],
            'total_crashes': self.counters['total_crashes'],
            'success_rate': self.counters['total_landings'] / max(1, total),
            'landings_last_minute': self._count_recent('landing', 60),
            'crashes_last_minute': self._count_recent('crash', 60),
            'avg_score': self.counters['total_score'] / max(1, self.counters['total_landings']),
            'total_flight_time': self.counters['total_flight_time'],
            'total_fuel_burned': self.counters['total_fuel_burned'],
            'by_difficulty': self._format_difficulty_stats()
        }
    
    def _count_recent(self, event_type, seconds):
        """Count recent events - O(n) but n is small (max 100)"""
        cutoff = time.time() - seconds
        return sum(1 for e, t in self.recent_events if e == event_type and t > cutoff)
    
    def _format_difficulty_stats(self):
        """Format difficulty stats - simple dict operations"""
        result = {}
        for diff, stats in self.by_difficulty.items():
            games = stats['games']
            landings = stats['landings']
            result[diff] = {
                'games': games,
                'landings': landings,
                'success_rate': landings / max(1, games),
                'avg_score': stats['total_score'] / max(1, landings)
            }
        return result

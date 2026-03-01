"""
Analytics engine for historical game data analysis
Conference-optimized with configurable time windows
"""
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict
from .config import AnalyticsConfig


class AnalyticsEngine:
    """Analyzes historical game data with configurable time windows"""
    
    def __init__(self, storage_path="data/metrics", config=None):
        self.storage_path = Path(storage_path)
        self.config = config or AnalyticsConfig()
        self.cache = {}
        self.cache_timestamp = {}
    
    def get_aggregate_stats(self, hours=None):
        """Get aggregate statistics for time window"""
        hours = hours or self.config.default_window_hours
        cache_key = f"aggregate_{hours}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]
        
        games = self._load_games_by_hours(hours)
        stats = self._calculate_aggregate_stats(games, hours)
        self._cache_result(cache_key, stats)
        
        return stats
    
    def get_trending_stats(self):
        """Get trending statistics (last hour vs previous hour)"""
        cache_key = "trending"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]
        
        last_hour = self._load_games_by_hours(1)
        previous_hour = self._load_games_by_hours(1, offset_hours=1)
        
        trends = {
            'current_hour': self._calculate_aggregate_stats(last_hour, 1),
            'previous_hour': self._calculate_aggregate_stats(previous_hour, 1),
            'change': self._calculate_change(last_hour, previous_hour)
        }
        
        self._cache_result(cache_key, trends)
        return trends
    
    def get_recent_activity(self, minutes=5):
        """Get very recent activity (last N minutes)"""
        cache_key = f"recent_{minutes}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]
        
        cutoff = time.time() - (minutes * 60)
        games = self._load_games_since(cutoff)
        
        activity = {
            'games_count': len(games),
            'landings': sum(1 for g in games if g['landed']),
            'crashes': sum(1 for g in games if g['crashed']),
            'avg_score': sum(g['score'] for g in games if g['landed']) / max(1, sum(1 for g in games if g['landed'])),
            'timestamp': time.time()
        }
        
        self._cache_result(cache_key, activity)
        return activity
    
    def get_fun_facts(self, hours=None):
        """Get fun facts for presentation"""
        hours = hours or self.config.default_window_hours
        cache_key = f"fun_facts_{hours}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]
        
        games = self._load_games_by_hours(hours)
        facts = self._calculate_fun_facts(games)
        self._cache_result(cache_key, facts)
        
        return facts
    
    def _load_games_by_hours(self, hours, offset_hours=0):
        """Load games from last N hours with optional offset"""
        if self.config.infinite_mode:
            return self._load_all_games()
        
        now = time.time()
        start_time = now - ((hours + offset_hours) * 3600)
        end_time = now - (offset_hours * 3600)
        
        return self._load_games_in_range(start_time, end_time)
    
    def _load_games_in_range(self, start_time, end_time):
        """Load games within time range"""
        games = []
        
        start_date = datetime.fromtimestamp(start_time).date()
        end_date = datetime.fromtimestamp(end_time).date()
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            file_path = self.storage_path / f"games_{date_str}.json"
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    daily_games = json.load(f)
                    games.extend([
                        g for g in daily_games 
                        if start_time <= g['started_at'] <= end_time
                    ])
            
            current_date += timedelta(days=1)
        
        return games
    
    def _load_games_since(self, cutoff_time):
        """Load games since cutoff timestamp"""
        return self._load_games_in_range(cutoff_time, time.time())
    
    def _load_all_games(self):
        """Load all available games (infinite mode)"""
        games = []
        for file_path in sorted(self.storage_path.glob("games_*.json")):
            with open(file_path, 'r') as f:
                games.extend(json.load(f))
        
        if len(games) > self.config.max_games_in_memory:
            games = games[-self.config.max_games_in_memory:]
        
        return games
    
    def _is_cached(self, key):
        """Check if result is cached and fresh"""
        if key not in self.cache:
            return False
        
        age = time.time() - self.cache_timestamp.get(key, 0)
        return age < self.config.cache_ttl_seconds
    
    def _cache_result(self, key, result):
        """Cache result with timestamp"""
        self.cache[key] = result
        self.cache_timestamp[key] = time.time()
    
    def _calculate_aggregate_stats(self, games, hours):
        """Calculate aggregate statistics"""
        if not games:
            return self._empty_stats(hours)
        
        total_games = len(games)
        landings = [g for g in games if g['landed']]
        crashes = [g for g in games if g['crashed']]
        
        stats = {
            'time_window_hours': hours,
            'total_games': total_games,
            'total_landings': len(landings),
            'total_crashes': len(crashes),
            'success_rate': len(landings) / total_games if total_games > 0 else 0,
            'total_flight_time': sum(g['duration'] for g in games),
            'total_fuel_burned': sum(g['fuel_used'] for g in games),
            'perfect_landings': sum(1 for g in landings 
                if g.get('landing_speed', 999) < 2.0 
                and g.get('landing_angle', 999) < 5.0 
                and g.get('fuel_remaining', 0) > 800),
            'avg_game_duration': sum(g['duration'] for g in games) / total_games,
            'avg_score': sum(g['score'] for g in landings) / max(1, len(landings)),
            'highest_score': max((g['score'] for g in landings), default=0),
            'fastest_landing': min((g['duration'] for g in landings), default=0) if landings else 0,
            'by_difficulty': self._stats_by_difficulty(games),
            'calculated_at': time.time()
        }
        
        return stats
    
    def _calculate_change(self, current_games, previous_games):
        """Calculate change between time periods"""
        current_count = len(current_games)
        previous_count = len(previous_games)
        
        if previous_count == 0:
            return {'games': current_count, 'percentage': 0, 'trend': 'new'}
        
        change_pct = ((current_count - previous_count) / previous_count) * 100
        
        return {
            'games': current_count - previous_count,
            'percentage': round(change_pct, 1),
            'trend': 'up' if change_pct > 0 else 'down' if change_pct < 0 else 'stable'
        }
    
    def _calculate_fun_facts(self, games):
        """Calculate fun facts for presentation"""
        if not games:
            return {}
        
        landings = [g for g in games if g['landed']]
        crashes = [g for g in games if g['crashed']]
        
        facts = {}
        
        # Smoothest pilot (fewest inputs for successful landing)
        if landings:
            smoothest = min(landings, key=lambda g: g.get('total_inputs', 999))
            facts['smoothest_pilot'] = {
                'player_id': smoothest['player_id'],
                'inputs': smoothest.get('total_inputs', 0),
                'score': smoothest['score']
            }
        
        # Most persistent (most games played)
        player_games = defaultdict(int)
        for game in games:
            player_games[game['player_id']] += 1
        
        if player_games:
            most_persistent = max(player_games.items(), key=lambda x: x[1])
            facts['most_persistent'] = {
                'player_id': most_persistent[0],
                'games_played': most_persistent[1]
            }
        
        # Luckiest landing (worst stats but still landed)
        if landings:
            luckiest = max(landings, key=lambda g: g.get('landing_speed', 0) + g.get('landing_angle', 0))
            facts['luckiest_landing'] = {
                'player_id': luckiest['player_id'],
                'landing_speed': luckiest.get('landing_speed', 0),
                'landing_angle': luckiest.get('landing_angle', 0),
                'score': luckiest['score']
            }
        
        # Crash statistics
        if crashes:
            facts['crash_stats'] = {
                'avg_crash_altitude': sum(g.get('altitude_at_end', 0) for g in crashes) / len(crashes),
                'avg_crash_speed': sum(g.get('speed_at_end', 0) for g in crashes) / len(crashes),
                'most_spectacular': max(crashes, key=lambda g: g.get('speed_at_end', 0))['speed_at_end']
            }
        
        return facts
    
    def _stats_by_difficulty(self, games):
        """Calculate per-difficulty statistics"""
        by_diff = defaultdict(lambda: {'games': 0, 'landings': 0, 'total_score': 0})
        
        for game in games:
            diff = game['difficulty']
            by_diff[diff]['games'] += 1
            if game['landed']:
                by_diff[diff]['landings'] += 1
                by_diff[diff]['total_score'] += game['score']
        
        result = {}
        for diff, stats in by_diff.items():
            games_count = stats['games']
            landings_count = stats['landings']
            result[diff] = {
                'games': games_count,
                'landings': landings_count,
                'success_rate': landings_count / max(1, games_count),
                'avg_score': stats['total_score'] / max(1, landings_count)
            }
        
        return result
    
    def _empty_stats(self, hours):
        """Return empty stats structure"""
        return {
            'time_window_hours': hours,
            'total_games': 0,
            'total_landings': 0,
            'total_crashes': 0,
            'success_rate': 0,
            'total_flight_time': 0,
            'total_fuel_burned': 0,
            'perfect_landings': 0,
            'avg_game_duration': 0,
            'avg_score': 0,
            'highest_score': 0,
            'fastest_landing': 0,
            'by_difficulty': {},
            'calculated_at': time.time()
        }

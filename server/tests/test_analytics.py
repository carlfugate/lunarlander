"""
Test analytics engine
"""
import pytest
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from metrics.analytics import AnalyticsEngine
from metrics.config import AnalyticsConfig


@pytest.fixture
def test_storage(tmp_path):
    """Create temporary storage with test data"""
    storage = tmp_path / "metrics"
    storage.mkdir()
    
    # Create test games for today
    today = datetime.now().strftime('%Y-%m-%d')
    games_today = []
    
    now = time.time()
    for i in range(10):
        games_today.append({
            'game_id': f'game-{i}',
            'player_id': f'player-{i % 3}',  # 3 players
            'difficulty': 'simple' if i < 5 else 'medium',
            'started_at': now - (i * 600),  # Every 10 minutes
            'landed': i % 2 == 0,  # 50% success
            'crashed': i % 2 == 1,
            'score': 1000 + i * 100,
            'duration': 30.0 + i,
            'fuel_used': 200 + i * 10,
            'total_inputs': 50 + i * 5,
            'landing_speed': 1.5 if i % 2 == 0 else 0,
            'landing_angle': 3.0 if i % 2 == 0 else 0,
            'fuel_remaining': 800 - i * 10,
            'altitude_at_end': 0 if i % 2 == 0 else 500 + i * 50,
            'speed_at_end': 1.5 if i % 2 == 0 else 10.0 + i
        })
    
    with open(storage / f"games_{today}.json", 'w') as f:
        json.dump(games_today, f)
    
    return storage


def test_analytics_config():
    """Test analytics configuration"""
    config = AnalyticsConfig()
    assert config.default_window_hours == 8
    assert config.cache_ttl_seconds == 60
    assert config.infinite_mode is False
    
    # Test time window calculation
    assert config.get_time_window() == 8 * 3600
    
    config.infinite_mode = True
    assert config.get_time_window() is None


def test_analytics_engine_initialization(test_storage):
    """Test analytics engine initialization"""
    engine = AnalyticsEngine(storage_path=test_storage)
    assert engine.storage_path == test_storage
    assert engine.config.default_window_hours == 8
    assert len(engine.cache) == 0


def test_aggregate_stats(test_storage):
    """Test aggregate statistics calculation"""
    engine = AnalyticsEngine(storage_path=test_storage)
    stats = engine.get_aggregate_stats(hours=24)
    
    assert stats['total_games'] == 10
    assert stats['total_landings'] == 5
    assert stats['total_crashes'] == 5
    assert stats['success_rate'] == 0.5
    assert stats['time_window_hours'] == 24
    assert 'by_difficulty' in stats
    assert 'simple' in stats['by_difficulty']
    assert 'medium' in stats['by_difficulty']


def test_aggregate_stats_caching(test_storage):
    """Test that aggregate stats are cached"""
    config = AnalyticsConfig(cache_ttl_seconds=60)
    engine = AnalyticsEngine(storage_path=test_storage, config=config)
    
    # First call - should calculate
    stats1 = engine.get_aggregate_stats(hours=24)
    assert 'aggregate_24' in engine.cache
    
    # Second call - should return cached
    stats2 = engine.get_aggregate_stats(hours=24)
    assert stats1 == stats2
    assert stats1['calculated_at'] == stats2['calculated_at']


def test_empty_stats(test_storage):
    """Test empty stats when no games exist"""
    empty_storage = test_storage / "empty"
    empty_storage.mkdir()
    
    engine = AnalyticsEngine(storage_path=empty_storage)
    stats = engine.get_aggregate_stats(hours=24)
    
    assert stats['total_games'] == 0
    assert stats['total_landings'] == 0
    assert stats['success_rate'] == 0


def test_trending_stats(test_storage):
    """Test trending statistics"""
    engine = AnalyticsEngine(storage_path=test_storage)
    trends = engine.get_trending_stats()
    
    assert 'current_hour' in trends
    assert 'previous_hour' in trends
    assert 'change' in trends
    assert 'trend' in trends['change']
    assert trends['change']['trend'] in ['up', 'down', 'stable', 'new']


def test_recent_activity(test_storage):
    """Test recent activity tracking"""
    engine = AnalyticsEngine(storage_path=test_storage)
    activity = engine.get_recent_activity(minutes=60)
    
    assert 'games_count' in activity
    assert 'landings' in activity
    assert 'crashes' in activity
    assert 'avg_score' in activity
    assert 'timestamp' in activity


def test_fun_facts(test_storage):
    """Test fun facts calculation"""
    engine = AnalyticsEngine(storage_path=test_storage)
    facts = engine.get_fun_facts(hours=24)
    
    # Should have some facts
    assert 'smoothest_pilot' in facts
    assert 'most_persistent' in facts
    assert 'luckiest_landing' in facts
    assert 'crash_stats' in facts
    
    # Check smoothest pilot structure
    assert 'player_id' in facts['smoothest_pilot']
    assert 'inputs' in facts['smoothest_pilot']
    assert 'score' in facts['smoothest_pilot']


def test_by_difficulty_stats(test_storage):
    """Test per-difficulty statistics"""
    engine = AnalyticsEngine(storage_path=test_storage)
    stats = engine.get_aggregate_stats(hours=24)
    
    by_diff = stats['by_difficulty']
    assert 'simple' in by_diff
    assert 'medium' in by_diff
    
    # Check simple difficulty
    simple = by_diff['simple']
    assert simple['games'] == 5
    assert 'success_rate' in simple
    assert 'avg_score' in simple


def test_time_window_filtering(test_storage):
    """Test that time window filtering works"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    # Get stats for different windows
    stats_1h = engine.get_aggregate_stats(hours=1)
    stats_24h = engine.get_aggregate_stats(hours=24)
    
    # 24h should have more games than 1h
    assert stats_24h['total_games'] >= stats_1h['total_games']


def test_infinite_mode(test_storage):
    """Test infinite mode loads all games"""
    config = AnalyticsConfig(infinite_mode=True)
    engine = AnalyticsEngine(storage_path=test_storage, config=config)
    
    stats = engine.get_aggregate_stats()
    assert stats['total_games'] == 10  # All games


def test_cache_expiration(test_storage):
    """Test that cache expires after TTL"""
    config = AnalyticsConfig(cache_ttl_seconds=1)  # 1 second TTL
    engine = AnalyticsEngine(storage_path=test_storage, config=config)
    
    # First call
    stats1 = engine.get_aggregate_stats(hours=24)
    timestamp1 = stats1['calculated_at']
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Second call - should recalculate
    stats2 = engine.get_aggregate_stats(hours=24)
    timestamp2 = stats2['calculated_at']
    
    assert timestamp2 > timestamp1


def test_perfect_landings_detection(test_storage):
    """Test perfect landings are detected"""
    engine = AnalyticsEngine(storage_path=test_storage)
    stats = engine.get_aggregate_stats(hours=24)
    
    # Should detect perfect landings (speed <2, angle <5, fuel >800)
    assert 'perfect_landings' in stats
    assert stats['perfect_landings'] >= 0


def test_crash_statistics(test_storage):
    """Test crash statistics calculation"""
    engine = AnalyticsEngine(storage_path=test_storage)
    facts = engine.get_fun_facts(hours=24)
    
    crash_stats = facts['crash_stats']
    assert 'avg_crash_altitude' in crash_stats
    assert 'avg_crash_speed' in crash_stats
    assert 'most_spectacular' in crash_stats
    assert crash_stats['avg_crash_altitude'] > 0
    assert crash_stats['avg_crash_speed'] > 0

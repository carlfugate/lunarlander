"""
Performance tests for metrics and analytics
"""
import pytest
import time
import json
import asyncio
from pathlib import Path
from datetime import datetime
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
            'player_id': f'player-{i % 3}',
            'difficulty': 'simple' if i < 5 else 'medium',
            'started_at': now - (i * 600),
            'landed': i % 2 == 0,
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


def test_analytics_cold_cache_performance(test_storage):
    """Test analytics performance with cold cache"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    start = time.time()
    stats = engine.get_aggregate_stats(hours=24)
    duration = time.time() - start
    
    print(f"\n  Cold cache: {duration*1000:.2f}ms")
    
    assert duration < 0.5, f"Cold cache too slow: {duration*1000:.2f}ms"
    assert stats['total_games'] > 0


def test_analytics_warm_cache_performance(test_storage):
    """Test analytics performance with warm cache"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    # Prime the cache
    engine.get_aggregate_stats(hours=24)
    
    # Test cached performance
    start = time.time()
    stats = engine.get_aggregate_stats(hours=24)
    duration = time.time() - start
    
    print(f"\n  Warm cache: {duration*1000:.2f}ms")
    
    assert duration < 0.01, f"Warm cache too slow: {duration*1000:.2f}ms"


def test_multiple_time_windows(test_storage):
    """Test performance with multiple time windows"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    windows = [1, 4, 8, 24]
    durations = []
    
    for hours in windows:
        start = time.time()
        stats = engine.get_aggregate_stats(hours=hours)
        duration = time.time() - start
        durations.append(duration)
        print(f"\n  {hours}h window: {duration*1000:.2f}ms")
    
    # All should be reasonably fast
    assert all(d < 0.5 for d in durations)


@pytest.mark.asyncio
async def test_concurrent_requests(test_storage):
    """Test concurrent API requests"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    async def make_request():
        return engine.get_aggregate_stats(hours=24)
    
    # Make 10 concurrent requests
    tasks = [make_request() for _ in range(10)]
    start = time.time()
    results = await asyncio.gather(*tasks)
    duration = time.time() - start
    
    print(f"\n  10 concurrent requests: {duration*1000:.2f}ms")
    print(f"  Avg per request: {duration*1000/10:.2f}ms")
    
    assert duration < 1.0, f"Concurrent requests too slow: {duration*1000:.2f}ms"
    assert len(results) == 10
    assert all(r['total_games'] > 0 for r in results)


def test_fun_facts_performance(test_storage):
    """Test fun facts calculation performance"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    start = time.time()
    facts = engine.get_fun_facts(hours=24)
    duration = time.time() - start
    
    print(f"\n  Fun facts: {duration*1000:.2f}ms")
    
    assert duration < 0.5, f"Fun facts too slow: {duration*1000:.2f}ms"
    assert len(facts) > 0


def test_trending_performance(test_storage):
    """Test trending stats performance"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    start = time.time()
    trends = engine.get_trending_stats()
    duration = time.time() - start
    
    print(f"\n  Trending stats: {duration*1000:.2f}ms")
    
    assert duration < 0.5, f"Trending stats too slow: {duration*1000:.2f}ms"


def test_recent_activity_performance(test_storage):
    """Test recent activity performance"""
    engine = AnalyticsEngine(storage_path=test_storage)
    
    start = time.time()
    activity = engine.get_recent_activity(minutes=5)
    duration = time.time() - start
    
    print(f"\n  Recent activity: {duration*1000:.2f}ms")
    
    assert duration < 0.1, f"Recent activity too slow: {duration*1000:.2f}ms"


def test_cache_efficiency(test_storage):
    """Test cache hit rate"""
    config = AnalyticsConfig(cache_ttl_seconds=60)
    engine = AnalyticsEngine(storage_path=test_storage, config=config)
    
    # First call - cache miss
    start = time.time()
    engine.get_aggregate_stats(hours=24)
    miss_time = time.time() - start
    
    # Subsequent calls - cache hits
    hit_times = []
    for _ in range(10):
        start = time.time()
        engine.get_aggregate_stats(hours=24)
        hit_times.append(time.time() - start)
    
    avg_hit_time = sum(hit_times) / len(hit_times)
    speedup = miss_time / avg_hit_time
    
    print(f"\n  Cache miss: {miss_time*1000:.2f}ms")
    print(f"  Cache hit avg: {avg_hit_time*1000:.2f}ms")
    print(f"  Speedup: {speedup:.1f}x")
    
    assert speedup > 10, f"Cache not effective enough: {speedup:.1f}x"

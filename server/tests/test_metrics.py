"""
Test metrics collection system
"""
import pytest
import asyncio
import time
from metrics.game_metrics import GameMetrics
from metrics.collector import MetricsCollector
from metrics.live_stats import LiveStatsTracker


def test_game_metrics_creation():
    """Test creating a GameMetrics object"""
    metrics = GameMetrics(
        game_id="test-123",
        player_id="player-1",
        difficulty="simple",
        started_at=time.time(),
        landed=True,
        score=1500,
        duration=45.5,
        max_altitude=600,
        fuel_remaining=750
    )
    
    assert metrics.game_id == "test-123"
    assert metrics.landed is True
    assert metrics.score == 1500
    assert metrics.to_dict()['difficulty'] == "simple"


def test_perfect_landing_detection():
    """Test perfect landing detection"""
    perfect = GameMetrics(
        game_id="test",
        player_id="player",
        difficulty="simple",
        started_at=time.time(),
        landed=True,
        landing_speed=1.5,
        landing_angle=3.0,
        fuel_remaining=850
    )
    
    assert perfect.is_perfect_landing() is True
    
    not_perfect = GameMetrics(
        game_id="test",
        player_id="player",
        difficulty="simple",
        started_at=time.time(),
        landed=True,
        landing_speed=5.0,  # Too fast
        landing_angle=3.0,
        fuel_remaining=850
    )
    
    assert not_perfect.is_perfect_landing() is False


@pytest.mark.asyncio
async def test_metrics_collector_async():
    """Test async metrics collection"""
    collector = MetricsCollector(storage_path="data/metrics_test", batch_size=2)
    
    # Queue some metrics
    metrics1 = GameMetrics(
        game_id="test-1",
        player_id="player-1",
        difficulty="simple",
        started_at=time.time()
    )
    
    metrics2 = GameMetrics(
        game_id="test-2",
        player_id="player-2",
        difficulty="medium",
        started_at=time.time()
    )
    
    await collector.save_game_metrics_async(metrics1.to_dict())
    await collector.save_game_metrics_async(metrics2.to_dict())
    
    # Wait for batch writer to process
    await asyncio.sleep(2)
    
    assert collector.get_pending_count() == 0


def test_live_stats_tracker():
    """Test live stats tracking"""
    tracker = LiveStatsTracker()
    
    # Track session start
    tracker.session_started()
    assert tracker.counters['active_sessions'] == 1
    assert tracker.counters['peak_sessions'] == 1
    
    # Track game completion
    metrics = {
        'difficulty': 'simple',
        'landed': True,
        'crashed': False,
        'score': 1500,
        'fuel_used': 250,
        'duration': 45.0
    }
    
    tracker.game_completed(metrics)
    
    stats = tracker.get_stats()
    assert stats['total_games'] == 1
    assert stats['total_landings'] == 1
    assert stats['success_rate'] == 1.0
    assert stats['by_difficulty']['simple']['games'] == 1
    
    # Track session end
    tracker.session_ended()
    assert tracker.counters['active_sessions'] == 0


def test_live_stats_multiple_games():
    """Test live stats with multiple games"""
    tracker = LiveStatsTracker()
    
    # Simulate 10 games
    for i in range(10):
        metrics = {
            'difficulty': 'simple' if i < 5 else 'medium',
            'landed': i % 2 == 0,  # 50% success rate
            'crashed': i % 2 == 1,
            'score': 1000 + i * 100,
            'fuel_used': 200 + i * 10,
            'duration': 30.0 + i
        }
        tracker.game_completed(metrics)
    
    stats = tracker.get_stats()
    assert stats['total_games'] == 10
    assert stats['total_landings'] == 5
    assert stats['total_crashes'] == 5
    assert stats['success_rate'] == 0.5
    assert stats['by_difficulty']['simple']['games'] == 5
    assert stats['by_difficulty']['medium']['games'] == 5


def test_recent_events_tracking():
    """Test recent events circular buffer"""
    tracker = LiveStatsTracker()
    
    # Add some recent events
    for i in range(5):
        metrics = {
            'difficulty': 'simple',
            'landed': True,
            'crashed': False,
            'score': 1000,
            'fuel_used': 200,
            'duration': 30.0
        }
        tracker.game_completed(metrics)
    
    # Check recent landings via get_stats
    stats = tracker.get_stats()
    assert stats['landings_last_minute'] == 5

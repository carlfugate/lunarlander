import pytest
from game.session import GameSession
from game.physics import Lander
from unittest.mock import AsyncMock, MagicMock

def test_calculate_score_crashed():
    """Crashed games should score 0"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = True
    session.lander.landed = False
    
    score = session.calculate_score(30.0)
    assert score == 0

def test_calculate_score_not_landed():
    """Games that didn't land should score 0"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = False
    session.lander.landed = False
    
    score = session.calculate_score(30.0)
    assert score == 0

def test_calculate_score_perfect_easy():
    """Perfect landing on easy difficulty"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 1000  # Full fuel
    
    score = session.calculate_score(20.0)  # Fast time
    
    # Base: 1000, Fuel: 500, Time: 300, Multiplier: 1.0
    assert score == 1800

def test_calculate_score_perfect_medium():
    """Perfect landing on medium difficulty"""
    session = GameSession("test", AsyncMock(), "medium")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 1000
    
    score = session.calculate_score(20.0)
    
    # Base: 1000, Fuel: 500, Time: 300, Multiplier: 1.5
    assert score == 2700

def test_calculate_score_perfect_hard():
    """Perfect landing on hard difficulty"""
    session = GameSession("test", AsyncMock(), "hard")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 1000
    
    score = session.calculate_score(20.0)
    
    # Base: 1000, Fuel: 500, Time: 300, Multiplier: 2.0
    assert score == 3600

def test_calculate_score_half_fuel():
    """Landing with half fuel remaining"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 500  # Half fuel
    
    score = session.calculate_score(20.0)
    
    # Base: 1000, Fuel: 250, Time: 300, Multiplier: 1.0
    assert score == 1550

def test_calculate_score_slow_landing():
    """Slow landing (60 seconds)"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 1000
    
    score = session.calculate_score(60.0)
    
    # Base: 1000, Fuel: 500, Time: 100, Multiplier: 1.0
    assert score == 1600

def test_calculate_score_very_slow_landing():
    """Very slow landing (80+ seconds) - no time bonus"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 1000
    
    score = session.calculate_score(80.0)
    
    # Base: 1000, Fuel: 500, Time: 0, Multiplier: 1.0
    assert score == 1500

def test_calculate_score_no_fuel():
    """Landing with no fuel remaining"""
    session = GameSession("test", AsyncMock(), "simple")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 0
    
    score = session.calculate_score(20.0)
    
    # Base: 1000, Fuel: 0, Time: 300, Multiplier: 1.0
    assert score == 1300

def test_calculate_score_realistic_landing():
    """Realistic landing scenario"""
    session = GameSession("test", AsyncMock(), "medium")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 300  # 30% fuel
    
    score = session.calculate_score(35.0)  # 35 seconds
    
    # Base: 1000, Fuel: 150, Time: 225, Multiplier: 1.5
    # (1000 + 150 + 225) * 1.5 = 2062.5 -> 2062
    assert score == 2062

def test_calculate_score_invalid_difficulty():
    """Invalid difficulty defaults to 1.0 multiplier"""
    session = GameSession("test", AsyncMock(), "invalid")
    session.lander.crashed = False
    session.lander.landed = True
    session.lander.fuel = 1000
    
    score = session.calculate_score(20.0)
    
    # Should use 1.0 multiplier as fallback
    assert score == 1800

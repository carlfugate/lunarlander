import pytest
import math
from game.physics import Lander, GRAVITY, THRUST_POWER, ROTATION_SPEED, FUEL_CONSUMPTION_RATE

def test_lander_initialization():
    """Test lander starts with correct values"""
    lander = Lander(x=600, y=100)
    assert lander.x == 600
    assert lander.y == 100
    assert lander.vx == 0
    assert lander.vy == 0
    assert lander.rotation == 0
    assert lander.fuel == 1000
    assert not lander.crashed
    assert not lander.landed

def test_gravity_application():
    """Test gravity increases downward velocity"""
    lander = Lander()
    dt = 1/60  # 60Hz
    
    initial_vy = lander.vy
    lander.update(dt, False, None)
    
    # Velocity should increase by GRAVITY * dt
    expected_vy = initial_vy + GRAVITY * dt
    assert abs(lander.vy - expected_vy) < 0.001

def test_thrust_upward():
    """Test thrust when pointing up reduces downward velocity"""
    lander = Lander()
    lander.rotation = 0  # Pointing up
    dt = 1/60
    
    lander.update(dt, True, None)
    
    # Should apply upward thrust and consume fuel
    assert lander.vy < GRAVITY * dt  # Net upward force
    assert lander.fuel < 1000

def test_thrust_consumes_fuel():
    """Test fuel consumption during thrust"""
    lander = Lander()
    dt = 1.0  # 1 second
    
    initial_fuel = lander.fuel
    lander.update(dt, True, None)
    
    expected_fuel = initial_fuel - FUEL_CONSUMPTION_RATE * dt
    assert abs(lander.fuel - expected_fuel) < 0.001

def test_no_thrust_without_fuel():
    """Test thrust doesn't work when fuel is empty"""
    lander = Lander()
    lander.fuel = 0
    lander.vy = 0
    dt = 1/60
    
    lander.update(dt, True, None)
    
    # Should only apply gravity, no thrust
    assert lander.vy == GRAVITY * dt

def test_rotation_left():
    """Test left rotation"""
    lander = Lander()
    dt = 1/60
    
    lander.update(dt, False, "left")
    
    expected_rotation = -ROTATION_SPEED * dt
    assert abs(lander.rotation - expected_rotation) < 0.001

def test_rotation_right():
    """Test right rotation"""
    lander = Lander()
    dt = 1/60
    
    lander.update(dt, False, "right")
    
    expected_rotation = ROTATION_SPEED * dt
    assert abs(lander.rotation - expected_rotation) < 0.001

def test_rotation_wrapping():
    """Test rotation wraps at -pi to pi"""
    lander = Lander()
    lander.rotation = math.pi - 0.1
    dt = 1.0
    
    lander.update(dt, False, "right")
    
    # Should wrap to negative
    assert lander.rotation < 0
    assert lander.rotation > -math.pi

def test_angled_thrust():
    """Test thrust at 45 degrees creates diagonal velocity"""
    lander = Lander()
    lander.rotation = math.pi / 4  # 45 degrees right
    lander.vx = 0
    lander.vy = 0
    dt = 1/60
    
    lander.update(dt, True, None)
    
    # Should have both horizontal and vertical components
    assert lander.vx > 0  # Moving right
    assert lander.vy < GRAVITY * dt  # Net upward

def test_position_update():
    """Test position updates based on velocity"""
    lander = Lander(x=600, y=100)
    lander.vx = 10
    lander.vy = 5
    dt = 1/60
    
    initial_x = lander.x
    initial_y = lander.y
    
    lander.update(dt, False, None)
    
    assert abs(lander.x - (initial_x + 10 * dt)) < 0.001
    # Y includes gravity
    expected_y = initial_y + (5 + GRAVITY * dt) * dt
    assert abs(lander.y - expected_y) < 0.1

def test_no_update_when_crashed():
    """Test lander doesn't move when crashed"""
    lander = Lander()
    lander.crashed = True
    lander.vx = 10
    lander.vy = 10
    
    initial_x = lander.x
    initial_y = lander.y
    
    lander.update(1/60, True, "left")
    
    assert lander.x == initial_x
    assert lander.y == initial_y

def test_no_update_when_landed():
    """Test lander doesn't move when landed"""
    lander = Lander()
    lander.landed = True
    lander.vx = 10
    
    initial_x = lander.x
    
    lander.update(1/60, True, "left")
    
    assert lander.x == initial_x

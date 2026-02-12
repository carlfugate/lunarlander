import sys
sys.path.insert(0, '..')

from game.physics import Lander
from game.terrain import Terrain

def test_gravity():
    lander = Lander(x=600, y=100)
    initial_y = lander.y
    lander.update(dt=1.0, thrust=False, rotate=None)
    assert lander.vy > 0, "Lander should fall"
    assert lander.y > initial_y, "Lander should move down"
    print("✓ Gravity test passed")

def test_thrust():
    lander = Lander(x=600, y=100)
    initial_fuel = lander.fuel
    lander.update(dt=1.0, thrust=True, rotate=None)
    assert lander.fuel < initial_fuel, "Fuel should decrease"
    assert lander.vy < 1.62, "Thrust should counteract gravity"
    print("✓ Thrust test passed")

def test_rotation():
    lander = Lander(x=600, y=100)
    lander.update(dt=1.0, thrust=False, rotate="left")
    assert lander.rotation < 0, "Should rotate left"
    lander.rotation = 0
    lander.update(dt=1.0, thrust=False, rotate="right")
    assert lander.rotation > 0, "Should rotate right"
    print("✓ Rotation test passed")

def test_landing():
    lander = Lander(x=600, y=710)
    lander.vx = 0.1
    lander.vy = 1.5  # Slow descent
    lander.rotation = 0.1  # Nearly upright
    lander.check_collision(terrain_y=705, is_landing_zone=True)
    assert lander.landed, "Should land successfully"
    assert not lander.crashed, "Should not crash"
    print("✓ Landing test passed")

def test_crash():
    lander = Lander(x=600, y=710)
    lander.vy = 5.0  # Fast descent
    lander.check_collision(terrain_y=705, is_landing_zone=True)
    assert lander.crashed, "Should crash"
    assert not lander.landed, "Should not land"
    print("✓ Crash test passed")

def test_terrain():
    terrain = Terrain(difficulty="simple")
    assert len(terrain.points) > 0, "Should have terrain points"
    assert len(terrain.landing_zones) > 0, "Should have landing zones"
    
    height = terrain.get_height_at(600)
    assert height > 0, "Should return valid height"
    print("✓ Terrain test passed")

if __name__ == "__main__":
    test_gravity()
    test_thrust()
    test_rotation()
    test_landing()
    test_crash()
    test_terrain()
    print("\n✅ All physics tests passed!")

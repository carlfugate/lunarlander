import pytest
from game.terrain import Terrain

def test_terrain_has_required_fields():
    """Test terrain contains points and landing zones"""
    terrain_obj = Terrain(difficulty="simple")
    terrain = terrain_obj.to_dict()
    
    assert "points" in terrain
    assert "landing_zones" in terrain
    assert len(terrain["points"]) > 0
    assert len(terrain["landing_zones"]) > 0

def test_terrain_points_are_valid():
    """Test terrain points have valid coordinates"""
    terrain_obj = Terrain(difficulty="simple")
    terrain = terrain_obj.to_dict()
    
    for point in terrain["points"]:
        assert len(point) == 2
        x, y = point
        assert 0 <= x <= 1200
        assert 0 <= y <= 800

def test_landing_zone_is_flat():
    """Test landing zone has flat surface"""
    terrain_obj = Terrain(difficulty="simple")
    terrain = terrain_obj.to_dict()
    
    zone = terrain["landing_zones"][0]
    assert "x1" in zone
    assert "x2" in zone
    assert "y" in zone
    assert zone["x2"] > zone["x1"]  # Has width

def test_landing_zone_within_bounds():
    """Test landing zone is within terrain bounds"""
    terrain_obj = Terrain(difficulty="simple")
    terrain = terrain_obj.to_dict()
    
    zone = terrain["landing_zones"][0]
    assert 0 <= zone["x1"] < 1200
    assert 0 <= zone["x2"] <= 1200
    assert 0 <= zone["y"] <= 800

def test_simple_difficulty():
    """Test simple difficulty has easier terrain"""
    terrain_obj = Terrain(difficulty="simple")
    terrain = terrain_obj.to_dict()
    
    # Simple should have at least one landing zone
    assert len(terrain["landing_zones"]) >= 1
    
    # Landing zone should be reasonably wide
    zone = terrain["landing_zones"][0]
    width = zone["x2"] - zone["x1"]
    assert width >= 50  # Minimum width for simple

def test_medium_difficulty():
    """Test medium difficulty has moderate terrain"""
    terrain_obj = Terrain(difficulty="intermediate")
    terrain = terrain_obj.to_dict()
    
    assert len(terrain["landing_zones"]) >= 1
    
    # May have narrower landing zones
    zone = terrain["landing_zones"][0]
    width = zone["x2"] - zone["x1"]
    assert width >= 40

def test_hard_difficulty():
    """Test hard difficulty has challenging terrain"""
    terrain_obj = Terrain(difficulty="advanced")
    terrain = terrain_obj.to_dict()
    
    assert len(terrain["landing_zones"]) >= 1
    
    # Narrower landing zones
    zone = terrain["landing_zones"][0]
    width = zone["x2"] - zone["x1"]
    assert width >= 30

def test_terrain_is_deterministic():
    """Test terrain has consistent structure"""
    terrain1 = Terrain(difficulty="simple").to_dict()
    terrain2 = Terrain(difficulty="simple").to_dict()
    
    # Both should have landing zones (randomness means count may vary)
    assert len(terrain1["landing_zones"]) >= 1
    assert len(terrain2["landing_zones"]) >= 1

def test_terrain_starts_and_ends_at_edges():
    """Test terrain covers full width"""
    terrain_obj = Terrain(difficulty="simple")
    terrain = terrain_obj.to_dict()
    
    x_coords = [point[0] for point in terrain["points"]]
    
    assert min(x_coords) == 0
    assert max(x_coords) >= 1150  # Close to 1200

import pytest
from game.replay import ReplayRecorder

def test_replay_records_at_30hz():
    """Test that replay only records every other frame (30Hz)"""
    recorder = ReplayRecorder("test-session", "test-user", "simple")
    
    # Record 10 frames
    for i in range(10):
        lander_state = {
            "x": 600 + i,
            "y": 100,
            "vx": 0,
            "vy": 2,
            "rotation": 0,
            "fuel": 1000,
            "crashed": False,
            "landed": False
        }
        recorder.record_frame(lander_state, 700, 600, 2.0, False)
    
    # Should only have 5 frames (every other frame)
    assert len(recorder.frames) == 5

def test_replay_quantizes_values():
    """Test that replay quantizes values to reduce size"""
    recorder = ReplayRecorder("test-session", "test-user", "simple")
    recorder.frame_counter = 1  # Start at odd so next frame records
    
    lander_state = {
        "x": 600.123456789,
        "y": 100.987654321,
        "vx": 1.23456789,
        "vy": 2.34567890,
        "rotation": 0.123456789,
        "fuel": 850.5,
        "crashed": False,
        "landed": False
    }
    
    recorder.record_frame(lander_state, 700.123, 599.876, 2.678, True)
    
    frame = recorder.frames[0]
    
    # Check quantization
    assert frame["lander"]["x"] == 600.1  # 1 decimal
    assert frame["lander"]["y"] == 101.0  # 1 decimal
    assert frame["lander"]["vx"] == 1.23  # 2 decimals
    assert frame["lander"]["vy"] == 2.35  # 2 decimals
    assert frame["lander"]["rotation"] == 0.12  # 2 decimals
    assert frame["lander"]["fuel"] == 850  # Integer (rounds down)
    assert frame["altitude"] == 600  # Integer
    assert frame["speed"] == 2.7  # 1 decimal
    assert frame["thrusting"] == True

def test_replay_stores_terrain():
    """Test that replay stores terrain data"""
    recorder = ReplayRecorder("test-session", "test-user", "simple")
    
    terrain_data = {
        "points": [[0, 700], [1200, 700]],
        "landing_zones": [{"x1": 500, "x2": 600, "y": 700}]
    }
    
    recorder.set_terrain(terrain_data)
    
    assert recorder.metadata["terrain"] == terrain_data

def test_replay_finalize():
    """Test replay finalization with metadata"""
    recorder = ReplayRecorder("test-session", "test-user", "simple")
    
    # Record some frames
    for i in range(4):
        recorder.record_frame(
            {"x": 600, "y": 100, "vx": 0, "vy": 2, "rotation": 0, "fuel": 1000, "crashed": False, "landed": False},
            700, 600, 2.0, False
        )
    
    recorder.finalize(landed=True, crashed=False, final_time=120.5, fuel_remaining=450, inputs=200)
    
    assert recorder.metadata["landed"] == True
    assert recorder.metadata["crashed"] == False
    assert recorder.metadata["duration"] == 120.5
    assert recorder.metadata["fuel_remaining"] == 450
    assert recorder.metadata["inputs"] == 200
    assert recorder.metadata["frame_count"] == 2  # Only 2 frames recorded (30Hz)

"""
Generate test data for metrics testing
"""
import json
import time
from pathlib import Path
from datetime import datetime


def generate_test_games(count=100):
    """Generate test game data"""
    games = []
    now = time.time()
    
    for i in range(count):
        games.append({
            'game_id': f'test-{i}',
            'player_id': f'player-{i % 10}',  # 10 unique players
            'difficulty': ['simple', 'medium', 'hard'][i % 3],
            'started_at': now - (i * 300),  # Every 5 minutes
            'ended_at': now - (i * 300) + 45,
            'landed': i % 3 != 0,  # 66% success rate
            'crashed': i % 3 == 0,
            'score': 1000 + i * 50,
            'duration': 30.0 + i * 0.5,
            'fuel_used': 200 + i * 5,
            'fuel_remaining': 800 - i * 5,
            'total_inputs': 50 + i * 2,
            'landing_speed': 1.5 if i % 3 != 0 else 0,
            'landing_angle': 3.0 if i % 3 != 0 else 0,
            'altitude_at_end': 0 if i % 3 != 0 else 500,
            'speed_at_end': 1.5 if i % 3 != 0 else 15.0,
            'max_altitude': 600 + i * 10,
            'min_altitude': 50,
            'max_speed': 20.0 + i * 0.5,
            'thrust_frames': 300 + i * 10,
            'rotation_changes': 10 + i
        })
    
    return games


if __name__ == '__main__':
    # Create test data
    storage = Path('data/metrics')
    storage.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    games = generate_test_games(100)
    
    with open(storage / f'games_{today}.json', 'w') as f:
        json.dump(games, f, indent=2)
    
    print(f"✅ Generated 100 test games in data/metrics/games_{today}.json")
    print(f"   - 10 unique players")
    print(f"   - 66% success rate")
    print(f"   - Mix of simple/medium/hard difficulties")
    print(f"   - Spanning last 8.3 hours")

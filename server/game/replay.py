import json
import gzip
import time

class ReplayRecorder:
    def __init__(self, session_id, user_id, difficulty):
        self.session_id = session_id
        self.user_id = user_id
        self.difficulty = difficulty
        self.frames = []
        self.metadata = {
            "session_id": session_id,
            "user_id": user_id,
            "difficulty": difficulty,
            "start_time": time.time(),
            "terrain": None
        }
    
    def set_terrain(self, terrain_data):
        """Store terrain data for replay"""
        self.metadata["terrain"] = terrain_data
        
    def record_frame(self, lander_state, terrain_height, altitude, speed, thrusting):
        """Record a single frame of game state"""
        self.frames.append({
            "lander": lander_state,
            "terrain_height": terrain_height,
            "altitude": altitude,
            "speed": speed,
            "thrusting": thrusting,
            "timestamp": time.time()
        })
        
    def finalize(self, landed, crashed, final_time, fuel_remaining, inputs):
        """Finalize replay with game result"""
        self.metadata.update({
            "end_time": time.time(),
            "duration": final_time,
            "landed": landed,
            "crashed": crashed,
            "fuel_remaining": fuel_remaining,
            "inputs": inputs,
            "frame_count": len(self.frames)
        })
        
    def to_dict(self):
        """Convert replay to dictionary"""
        return {
            "metadata": self.metadata,
            "frames": self.frames
        }
        
    def to_json(self):
        """Convert replay to JSON string"""
        return json.dumps(self.to_dict())
        
    def to_compressed(self):
        """Convert replay to compressed JSON"""
        json_str = self.to_json()
        return gzip.compress(json_str.encode('utf-8'))
        
    @staticmethod
    def from_json(json_str):
        """Load replay from JSON string"""
        data = json.loads(json_str)
        return data
        
    @staticmethod
    def from_compressed(compressed_data):
        """Load replay from compressed data"""
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        return ReplayRecorder.from_json(json_str)

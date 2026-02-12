import random

class Terrain:
    def __init__(self, width=1200, height=800, difficulty="simple"):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.points = self._generate(difficulty)
        self.landing_zones = self._find_landing_zones()
        
    def _generate(self, difficulty):
        points = []
        
        if difficulty == "simple":
            # Mostly flat with gentle slopes
            y_base = self.height - 100
            for x in range(0, self.width + 1, 50):
                y = y_base + random.randint(-20, 20)
                points.append((x, y))
        elif difficulty == "medium":
            # Rolling hills
            y = self.height - 150
            for x in range(0, self.width + 1, 40):
                y += random.randint(-30, 30)
                y = max(self.height - 300, min(self.height - 50, y))
                points.append((x, y))
        else:  # hard
            # Steep mountains
            y = self.height - 200
            for x in range(0, self.width + 1, 30):
                y += random.randint(-50, 50)
                y = max(self.height - 500, min(self.height - 50, y))
                points.append((x, y))
                
        return points
        
    def _find_landing_zones(self):
        zones = []
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            # Flat enough to land
            if abs(y2 - y1) < 5:
                width = x2 - x1
                if (self.difficulty == "simple" and width >= 50) or \
                   (self.difficulty == "medium" and width >= 40) or \
                   (self.difficulty == "hard" and width >= 30):
                    zones.append({
                        "x1": x1,
                        "x2": x2,
                        "y": y1,
                        "multiplier": 1.0 if self.difficulty == "simple" else 
                                     1.5 if self.difficulty == "medium" else 2.0
                    })
        return zones
        
    def get_height_at(self, x):
        # Linear interpolation between points
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1)
                return y1 + (y2 - y1) * t
        return self.height
        
    def is_landing_zone(self, x):
        for zone in self.landing_zones:
            if zone["x1"] <= x <= zone["x2"]:
                return True, zone["multiplier"]
        return False, 1.0
        
    def to_dict(self):
        return {
            "points": self.points,
            "landing_zones": self.landing_zones,
            "width": self.width,
            "height": self.height
        }

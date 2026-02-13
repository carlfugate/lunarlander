import random

class Terrain:
    def __init__(self, width=1200, height=800, difficulty="simple"):
        self.width = width
        self.height = height
        # Normalize difficulty names (handle test aliases)
        if difficulty == "intermediate":
            difficulty = "medium"
        elif difficulty == "advanced":
            difficulty = "hard"
        self.difficulty = difficulty
        self.points = self._generate(difficulty)
        self.landing_zones = self._find_landing_zones()
        
    def _generate(self, difficulty):
        points = []
        
        # Determine step size based on difficulty
        if difficulty == "simple":
            step = 50
            y_base = self.height - 100
            landing_y = self.height - 100
            landing_width = 100
            variation = 20
        elif difficulty == "medium":
            step = 40
            y_base = self.height - 150
            landing_y = self.height - 150
            landing_width = 80
            variation = 30
        else:  # hard
            step = 30
            y_base = self.height - 200
            landing_y = self.height - 200
            landing_width = 60
            variation = 50
        
        # Determine landing zone position (aligned to step)
        landing_x_start = random.randint(400 // step, 700 // step) * step
        landing_x_end = landing_x_start + landing_width
        
        if difficulty == "simple":
            # Mostly flat with gentle slopes, one flat landing zone
            prev_y = y_base
            for x in range(0, self.width + 1, step):
                if landing_x_start <= x <= landing_x_end:
                    y = landing_y
                else:
                    # Ensure variation to prevent accidental flat zones
                    y = prev_y + random.randint(-variation, variation)
                    # Force at least 10 units difference from landing zone height
                    if abs(y - landing_y) < 10:
                        y = landing_y + (15 if random.random() > 0.5 else -15)
                points.append((x, y))
                prev_y = y
        elif difficulty == "medium":
            # Rolling hills with one flat landing zone
            y = y_base
            for x in range(0, self.width + 1, step):
                if landing_x_start <= x <= landing_x_end:
                    y = landing_y
                else:
                    y += random.randint(-variation, variation)
                    y = max(self.height - 300, min(self.height - 50, y))
                    # Force at least 10 units difference from landing zone height
                    if abs(y - landing_y) < 10:
                        y = landing_y + (15 if random.random() > 0.5 else -15)
                points.append((x, y))
        else:  # hard
            # Steep mountains with one flat landing zone
            y = y_base
            for x in range(0, self.width + 1, step):
                if landing_x_start <= x <= landing_x_end:
                    y = landing_y
                else:
                    y += random.randint(-variation, variation)
                    y = max(self.height - 500, min(self.height - 50, y))
                    # Force at least 10 units difference from landing zone height
                    if abs(y - landing_y) < 10:
                        y = landing_y + (15 if random.random() > 0.5 else -15)
                points.append((x, y))
                
        return points
        
    def _find_landing_zones(self):
        # Find consecutive flat segments and merge them
        zones = []
        i = 0
        while i < len(self.points) - 1:
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            # Start of a flat segment
            if abs(y2 - y1) < 5:
                zone_start_x = x1
                zone_y = y1
                j = i
                
                # Find end of consecutive flat segments
                while j < len(self.points) - 1:
                    xj1, yj1 = self.points[j]
                    xj2, yj2 = self.points[j + 1]
                    if abs(yj2 - yj1) < 5 and abs(yj1 - zone_y) < 5:
                        j += 1
                    else:
                        break
                
                zone_end_x = self.points[j][0]
                width = zone_end_x - zone_start_x
                
                # Check if wide enough
                if (self.difficulty == "simple" and width >= 50) or \
                   (self.difficulty == "medium" and width >= 40) or \
                   (self.difficulty == "hard" and width >= 30):
                    zones.append({
                        "x1": zone_start_x,
                        "x2": zone_end_x,
                        "y": zone_y,
                        "multiplier": 1.0 if self.difficulty == "simple" else 
                                     1.5 if self.difficulty == "medium" else 2.0
                    })
                
                i = j + 1
            else:
                i += 1
        
        # Return only the widest zone (the one we intentionally created)
        if zones:
            return [max(zones, key=lambda z: z['x2'] - z['x1'])]
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

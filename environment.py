import numpy as np
import random

# Constants for Terrain Types
EMPTY = 0      # Sand (Cost 1)
OBSTACLE = 1   # Wall (Impassable)
ICE = 2        # Blue Resource
START = 3      # Base
ROUGH = 4      # Mud (Cost 10)
IRON = 5       # Magenta Resource 

class Environment:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.start_pos = (0, 0)
        self.generate_map()

    def generate_map(self):
        """Generates a map with Obstacles, Mud, Ice, and Iron."""
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.grid[0, 0] = START

        for r in range(self.height):
            for c in range(self.width):
                if (r, c) == self.start_pos: continue

                prob = random.random()
                if prob < 0.15:
                    self.grid[r, c] = OBSTACLE
                elif prob < 0.30:
                    self.grid[r, c] = ROUGH
                elif prob > 0.96:
                    # 50/50 Chance for Ice or Iron
                    if random.random() < 0.5:
                        self.grid[r, c] = ICE
                    else:
                        self.grid[r, c] = IRON

    def get_grid(self):
        return self.grid

    def collect_resource(self, r, c):
        """Removes resource and returns its type (ICE or IRON)."""
        val = self.grid[r, c]
        if val == ICE or val == IRON:
            self.grid[r, c] = EMPTY
            return val # Return what we collected
        return None
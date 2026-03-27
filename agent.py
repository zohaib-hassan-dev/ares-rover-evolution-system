import collections
import heapq
from environment import OBSTACLE, ICE, IRON, EMPTY, START, ROUGH

class Rover:
    def __init__(self, start_pos=(0,0)):
        self.row, self.col = start_pos
        # BATTERY 200 TO MATCH EVOLUTION & LONG PATHS
        self.battery = 200
        self.max_battery = 200
        self.ice_collected = 0
        self.iron_collected = 0
        self.path = []

        # CSP: Inventory Management
        self.inventory = []

        # GENETICS: Default to "All-Terrain" (0.5) until GA runs
        self.genome = 0.5

    def set_genome(self, gene):
        """Updates the rover's tire type based on evolution."""
        self.genome = round(gene * 20) / 20.0
        print(f"Rover upgraded! New Gene: {self.genome} ({self.get_tire_name()})")

    def get_tire_name(self):
        gene = self.genome
        if gene < 0.125: return "Hyper-Slicks"
        elif gene < 0.25: return "Racing Slicks"
        elif gene < 0.375: return "Street Perf."
        elif gene < 0.5: return "Gravel Treads"
        elif gene < 0.625: return "All-Terrain"
        elif gene < 0.75: return "Off-Road"
        elif gene < 0.875: return "Mud-Terrain"
        else: return "Super Swampers"

    def get_tire_color(self):
        """Returns (R, G, B) color for the tires."""
        gene = self.genome
        # 8 Distinct Colors for visualization
        if gene < 0.125: return (0, 255, 255)    # Cyan
        elif gene < 0.25: return (0, 100, 255)   # Blue
        elif gene < 0.375: return (100, 0, 255)  # Purple
        elif gene < 0.5: return (255, 0, 255)    # Magenta
        elif gene < 0.625: return (255, 0, 0)    # Red
        elif gene < 0.75: return (255, 100, 0)   # Orange
        elif gene < 0.875: return (255, 255, 0)  # Yellow
        else: return (0, 255, 0)                 # Green

    def calculate_move_cost(self, tile_type):
        """Calculates cost based on tires."""
        sand_cost = 1.0
        mud_cost = 10.0

        tire_factor = self.genome

        # Slicks (0.0) = Cheap Sand, Expensive Mud
        # Offroad (1.0) = Expensive Sand, Cheap Mud
        real_sand_cost = sand_cost + (tire_factor * 2.0)
        real_mud_cost = mud_cost - (tire_factor * 8.0)

        if tile_type == ROUGH:
            return real_mud_cost
        else:
            return real_sand_cost

    def estimate_path_cost(self, path, grid):
        """Predicts battery cost for a full path."""
        total_cost = 0
        for (r, c) in path:
            tile_type = grid[r, c]
            total_cost += self.calculate_move_cost(tile_type)
        return total_cost

    def move_step(self, grid):
        if self.path:
            next_pos = self.path[0] # Peek
            nr, nc = next_pos
            tile_type = grid[nr, nc]

            cost = self.calculate_move_cost(tile_type)

            if self.battery >= cost:
                self.battery -= cost
                self.row, self.col = self.path.pop(0)
                return True
            else:
                return False # Battery dead!
        return False

    def get_pos(self):
        return (self.row, self.col)

    # --- CSP MODULE ---
    def check_cargo_constraint(self, new_resource_type):
        if not self.inventory: return True
        current_type = self.inventory[0]
        if current_type == new_resource_type: return True
        return False

    def add_to_inventory(self, resource_type):
        self.inventory.append(resource_type)

    def unload_cargo(self):
        self.inventory = []

        # --- NEW LOGIC: Partial Recharge ---
        # Only add 20% (40 units) when at base.
        # This ensures battery slowly drains over time, eventually triggering
        # the Solar Panel event in the field.
        charge_amount = 40

        if self.battery >= 180:
            self.battery = self.max_battery
        else:
            self.battery += charge_amount
            # Cap at max
            if self.battery > self.max_battery:
                self.battery = self.max_battery

        print(f"Cargo Unloaded. Battery Recharged (+{charge_amount}) to {int(self.battery)}")

    # --- ALGORITHMS ---
    def run_bfs(self, grid, grid_width, grid_height):
        start = (self.row, self.col)
        queue = collections.deque([start])
        visited = set()
        visited.add(start)
        came_from = {start: None}
        found_target = None

        while queue:
            current = queue.popleft()
            r, c = current

            if grid[r, c] == ICE or grid[r, c] == IRON:
                found_target = current
                break

            neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
            for nr, nc in neighbors:
                if 0 <= nr < grid_height and 0 <= nc < grid_width:
                    if grid[nr, nc] != OBSTACLE and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
                        came_from[(nr, nc)] = current

        if found_target:
            self.reconstruct_path(came_from, start, found_target)
            return True
        return False

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def run_astar(self, grid, grid_width, grid_height, target_pos=(0,0)):
        start = (self.row, self.col)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {start: None}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == target_pos:
                self.reconstruct_path(came_from, start, target_pos)
                return True

            r, c = current
            neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
            for nr, nc in neighbors:
                if 0 <= nr < grid_height and 0 <= nc < grid_width:
                    if grid[nr, nc] != OBSTACLE:
                        new_g_score = g_score[current] + 1
                        if (nr, nc) not in g_score or new_g_score < g_score[(nr, nc)]:
                            came_from[(nr, nc)] = current
                            g_score[(nr, nc)] = new_g_score
                            f_score = new_g_score + self.heuristic((nr, nc), target_pos)
                            heapq.heappush(open_set, (f_score, (nr, nc)))
        return False

    def run_ucs(self, grid, grid_width, grid_height, target_pos=(0,0)):
        start = (self.row, self.col)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while open_set:
            current_cost, current = heapq.heappop(open_set)

            if current == target_pos:
                self.reconstruct_path(came_from, start, target_pos)
                return True

            r, c = current
            neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
            for nr, nc in neighbors:
                if 0 <= nr < grid_height and 0 <= nc < grid_width:
                    if grid[nr, nc] != OBSTACLE:
                        # Use actual tire costs for UCS!
                        move_cost = self.calculate_move_cost(grid[nr, nc])

                        new_cost = cost_so_far[current] + move_cost
                        if (nr, nc) not in cost_so_far or new_cost < cost_so_far[(nr, nc)]:
                            cost_so_far[(nr, nc)] = new_cost
                            heapq.heappush(open_set, (new_cost, (nr, nc)))
                            came_from[(nr, nc)] = current
        return False

    def reconstruct_path(self, came_from, start, end):
        self.path = []
        curr = end
        while curr != start:
            self.path.append(curr)
            curr = came_from[curr]
        self.path.reverse()
import pygame
import sys
import time
from environment import Environment, OBSTACLE, ICE, IRON, START, ROUGH
from agent import Rover
import evolution # Import our GA module

# Configuration
TILE_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)




def draw_rover(screen, rover, tile_size):
    """Draws a detailed 2D Rover with 4 tires."""
    r, c = rover.get_pos()
    x = c * tile_size
    y = r * tile_size

    # 1. Draw Body (Grey Chassis)
    body_margin = tile_size // 4
    body_rect = pygame.Rect(x + body_margin, y + body_margin,
                            tile_size - body_margin*2, tile_size - body_margin*2)
    pygame.draw.rect(screen, (200, 200, 200), body_rect)

    # 2. Draw 4 Tires
    tire_color = rover.get_tire_color() # Get color based on GENE
    tire_w = tile_size // 5
    tire_h = tile_size // 3

    # Positions relative to tile
    tl = (x + 2, y + 2)
    tr = (x + tile_size - tire_w - 2, y + 2)
    bl = (x + 2, y + tile_size - tire_h - 2)
    br = (x + tile_size - tire_w - 2, y + tile_size - tire_h - 2)

    for tx, ty in [tl, tr, bl, br]:
        pygame.draw.rect(screen, tire_color, (tx, ty, tire_w, tire_h))
        pygame.draw.rect(screen, BLACK, (tx, ty, tire_w, tire_h), 1) # Outline

    # 3. Draw Center (Sensor)
    pygame.draw.circle(screen, RED, body_rect.center, 4)

def show_charging_screen(screen, font):
    """Pauses everything for 5 seconds to simulate solar charging."""
    start_ticks = pygame.time.get_ticks()
    while True:
        elapsed = pygame.time.get_ticks() - start_ticks
        if elapsed > 5000: # 5 seconds
            break

        screen.fill((0, 0, 0)) # Black screen

        text1 = font.render("BATTERY CRITICAL!", True, RED)
        text2 = font.render("DEPLOYING SOLAR PANELS...", True, YELLOW)
        text3 = font.render(f"Recharging... {5 - int(elapsed/1000)}s", True, GREEN)

        screen.blit(text1, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 40))
        screen.blit(text2, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
        screen.blit(text3, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 40))

        pygame.display.flip()

        # Keep window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ARES: 'G'=Evolve Tires | 'B'=Hunt | 'R'=Reset")
    font = pygame.font.Font(None, 30)

    env = Environment(GRID_WIDTH, GRID_HEIGHT)
    rover = Rover(env.start_pos)

    # Ensure counters exist on the rover (if agent.py hasn't been updated)
    if not hasattr(rover, "ice_collected"):
        rover.ice_collected = 0
    if not hasattr(rover, "iron_collected"):
        rover.iron_collected = 0

    clock = pygame.time.Clock()
    last_move_time = 0
    MOVE_DELAY = 400

    mode = "IDLE"

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    env.generate_map()
                    rover.path = []
                    rover.row, rover.col = env.start_pos
                    rover.battery = rover.max_battery
                    mode = "IDLE"
                    # reset counters when map is regenerated
                    rover.ice_collected = 0
                    rover.iron_collected = 0

                # --- GENETIC ALGORITHM BUTTON ---
                if event.key == pygame.K_g:
                    print("Activating Evolution Engine...")
                    # Run the GA on the CURRENT map
                    best_gene = evolution.evolve_best_rover(env.get_grid(), env.start_pos)
                    # Apply best gene to our visible rover
                    rover.set_genome(best_gene)
                    print("Evolution Complete. Tires Updated.")

                if event.key == pygame.K_b:
                    mode = "HUNT"
                    rover.run_bfs(env.get_grid(), GRID_WIDTH, GRID_HEIGHT)

                if event.key == pygame.K_a:
                    mode = "RETURN"
                    rover.run_astar(env.get_grid(), GRID_WIDTH, GRID_HEIGHT, target_pos=(0,0))

                if event.key == pygame.K_u:
                    mode = "RETURN"
                    rover.run_ucs(env.get_grid(), GRID_WIDTH, GRID_HEIGHT, target_pos=(0,0))

        # --- AI LOGIC ---
        if rover.path:
            # 1. SAFETY CHECK: Do we have enough battery to reach target + return home?
            cost_to_target = rover.estimate_path_cost(rover.path, env.get_grid())
            dist_to_home = abs(rover.row) + abs(rover.col)
            cost_to_home = dist_to_home * 2

            total_needed = cost_to_target + cost_to_home

            if rover.battery < total_needed:
                # FIX: Prevent Infinite Loop if we are ALREADY full
                if rover.battery >= rover.max_battery:
                    print(f"WARNING: Path requires {total_needed}, max is {rover.max_battery}. Proceeding at risk.")
                    # Force move (don't charge again)
                else:
                    print(f"Low Battery! Needed: {total_needed}, Has: {rover.battery}")
                    show_charging_screen(screen, font)
                    rover.battery = rover.max_battery # Refilled!
                    print("Battery Refilled. Resuming.")
                    last_move_time = current_time + 1000

            # 2. MOVE
            if current_time - last_move_time > MOVE_DELAY:
                success = rover.move_step(env.get_grid())
                last_move_time = current_time
                if not success:
                    print("CRITICAL FAILURE: Battery Died.")
                    mode = "IDLE"
        else:
            # No path: handle mode behaviour (HUNT / RETURN / IDLE)
            if mode == "HUNT":
                r, c = rover.get_pos()
                tile = env.get_grid()[r, c]

                if tile == ICE or tile == IRON:
                    if rover.check_cargo_constraint(tile):
                        env.collect_resource(r, c)
                        rover.add_to_inventory(tile)

                        # --- NEW COUNTERS ---
                        if tile == ICE:
                            rover.ice_collected += 1
                        elif tile == IRON:
                            rover.iron_collected += 1
                        # ---------------------

                        # Continue hunting
                        found = rover.run_bfs(env.get_grid(), GRID_WIDTH, GRID_HEIGHT)
                        if not found:
                            mode = "RETURN"
                            rover.run_astar(env.get_grid(), GRID_WIDTH, GRID_HEIGHT, target_pos=(0,0))
                    else:
                        mode = "RETURN"
                        rover.run_astar(env.get_grid(), GRID_WIDTH, GRID_HEIGHT, target_pos=(0,0))
                else:
                    found = rover.run_bfs(env.get_grid(), GRID_WIDTH, GRID_HEIGHT)
                    if not found:
                        mode = "IDLE"

            elif mode == "RETURN":
                if rover.get_pos() == (0,0):
                    rover.unload_cargo()
                    mode = "HUNT"
                    rover.run_bfs(env.get_grid(), GRID_WIDTH, GRID_HEIGHT)

        # --- Drawing ---
        screen.fill(WHITE)
        grid = env.get_grid()

        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if grid[r, c] == OBSTACLE:
                    pygame.draw.rect(screen, GRAY, rect)
                elif grid[r, c] == ROUGH:
                    pygame.draw.rect(screen, BROWN, rect)
                elif grid[r, c] == ICE:
                    pygame.draw.rect(screen, BLUE, rect)
                elif grid[r, c] == IRON:
                    pygame.draw.rect(screen, MAGENTA, rect)
                elif grid[r, c] == START:
                    pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        for (pr, pc) in rover.path:
            pygame.draw.circle(screen, YELLOW,
                               (pc * TILE_SIZE + TILE_SIZE//2, pr * TILE_SIZE + TILE_SIZE//2), 4)

        # DRAW THE DETAILED ROVER
        draw_rover(screen, rover, TILE_SIZE)

        # GUI Overlay
        tire_text = font.render(f"Tires: {rover.get_tire_name()}", True, BLACK)
        batt_text = font.render(f"Battery: {int(rover.battery)}%", True, RED if rover.battery < 30 else GREEN)
        screen.blit(tire_text, (10, SCREEN_HEIGHT - 60))
        screen.blit(batt_text, (10, SCREEN_HEIGHT - 30))

        # Resource counters display (ICE and IRON collected)
        counter_text = font.render(
            f"ICE: {rover.ice_collected}   IRON: {rover.iron_collected}",
            True, ORANGE 
        )
        # Position it above the other overlay text
        screen.blit(counter_text, (10, SCREEN_HEIGHT - 90))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

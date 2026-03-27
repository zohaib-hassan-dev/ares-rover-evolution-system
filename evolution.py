import random
import copy
import numpy as np
from environment import Environment, OBSTACLE, ICE, IRON, ROUGH, EMPTY
from agent import Rover

# --- CONFIGURATION ---
POPULATION_SIZE = 10
GENERATIONS = 5
BATTERY_START = 200      

# We use the Rover class from agent.py directly ,
# but we need a wrapper to run the headless simulation.

def run_simulation(genome, grid, start_pos):
    """
    Runs a simulation on a SPECIFIC grid.
    """
    rover = Rover(start_pos)
    rover.set_genome(genome)
    rover.battery = BATTERY_START

    # We need a temporary copy of the grid so the sim doesn't eat the real resources
    temp_grid = copy.deepcopy(grid)
    width = len(temp_grid[0])
    height = len(temp_grid)

    steps = 0
    score = 0
    max_steps = 100

    while rover.battery > 0 and steps < max_steps:
        r, c = rover.get_pos()
        if temp_grid[r, c] in [ICE, IRON]:
            temp_grid[r, c] = EMPTY # Consume
            score += 1

        found = rover.run_bfs(temp_grid, width, height)
        if not found: break

        if rover.path:
            # Move one step
            rover.move_step(temp_grid)
            steps += 1

    return score

# --- GENETIC ALGORITHM FUNCTIONS ---

def create_initial_population(size):
    return [random.random() for _ in range(size)]

def crossover(parent1, parent2):
    child_gene = (parent1 + parent2) / 2.0
    return child_gene

def mutate(genome):
    if random.random() < 0.3:
        mutation = random.uniform(-0.1, 0.1)
        genome += mutation
        genome = max(0.0, min(1.0, genome))
    return genome

def evolve_best_rover(grid, start_pos):
    """
    Called by Main.py.
    Runs a quick evolution on the CURRENT MAP to find the best tire.
    """
    print("--- RUNNING GENETIC OPTIMIZATION FOR THIS MAP ---")
    population = create_initial_population(POPULATION_SIZE)

    for gen in range(GENERATIONS):
        scores = []
        for gene in population:
            fitness = run_simulation(gene, grid, start_pos)
            scores.append((fitness, gene))

        scores.sort(key=lambda x: x[0], reverse=True)
        best_gene = scores[0][1]

        # Evolution step
        next_gen = [best_gene] # Elitism
        while len(next_gen) < POPULATION_SIZE:
            parent1 = scores[random.randint(0, len(scores)//2)][1]
            parent2 = scores[random.randint(0, len(scores)//2)][1]
            child = mutate(crossover(parent1, parent2))
            next_gen.append(child)
        population = next_gen

    print(f"--- OPTIMIZATION COMPLETE. BEST GENE: {best_gene:.2f} ---")
    return best_gene
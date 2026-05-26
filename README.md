# ARES: Adaptive Rover Evolution System 🚀

This project is a simulation of a Mars rover that navigates a grid-based environment, collects resources, and adapts its behavior based on terrain conditions.

The goal of this project was to combine multiple AI concepts like search algorithms and genetic algorithms into one system and understand how they interact in a dynamic environment.

---

## 💡 What the Rover Does

* Moves across a randomly generated terrain
* Collects resources like Ice and Iron
* Avoids obstacles and handles rough terrain
* Manages battery and returns to base when needed
* Adapts movement using different tire types

---

## 🧠 AI Concepts Used

* **BFS (Breadth First Search)** → Finds the nearest resource
* **A*** → Efficiently returns the rover to base
* **UCS (Uniform Cost Search)** → Considers terrain cost while moving
* **Genetic Algorithm** → Evolves the best tire configuration for terrain

The genetic algorithm is the core idea behind this project. It allows the rover to adapt its behavior depending on the environment, making the system more intelligent over time.

---

## 🎮 Controls

* `G` → Run genetic algorithm (optimize tires)
* `B` → Start searching for resources
* `A` → Return to base using A*
* `U` → Return using UCS
* `R` → Reset environment

---

## 🛠 Technologies Used

* Python
* Pygame
* NumPy

---

## ▶️ How to Run

### 1. Install dependencies

```
pip install pygame numpy
```

### 2. Run the simulation

```
python main.py
```

---

## 📂 Project Structure

* `main.py` → Runs the simulation and visualization
* `agent.py` → Contains rover logic and behavior
* `environment.py` → Handles terrain generation
* `evolution.py` → Implements genetic algorithm

---

## 🚀 Why I Built This

I wanted to build something more meaningful than basic projects by combining different AI techniques into one system. This project helped me understand how search algorithms and optimization methods can work together in a real-world scenario.

---

## 🔮 Future Improvements

* Add better visualizations
* Integrate reinforcement learning
* Improve decision-making strategies
* Add more complex terrain types

---

<!-- gitpulse:contribution index="1" timestamp="2026-05-26" -->
<!-- gitpulse:contribution index="2" timestamp="2026-05-26" -->
<!-- gitpulse:contribution index="3" timestamp="2026-05-26" -->
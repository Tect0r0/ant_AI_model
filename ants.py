from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from random import randint

# Ant agent definition
class Ant(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.has_found_food = False

    def step(self):
        # Check if food is found
        if self.pos in self.model.food_positions:
            self.has_found_food = True
            self.model.place_pheromone(self.pos)
            return

        # Get neighboring cells
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)

        # Prioritize pheromone or random move
        next_moves = [cell for cell in neighbors if cell in self.model.pheromone_positions]
        if not next_moves:
            next_moves = [cell for cell in neighbors if self.model.grid.is_cell_empty(cell)]

        if next_moves:
            new_position = self.random.choice(next_moves)
            self.model.grid.move_agent(self, new_position)
            self.model.place_pheromone(new_position)

# AntModel definition
class AntModel(Model):
    def __init__(self, num_ants=5, width=25, height=25):
        super().__init__()  # Explicitly call the parent class's __init__ method
        self.num_agents = num_ants
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Dictionaries to store positions of static objects
        self.food_positions = {}
        self.obstacle_positions = {}
        self.pheromone_positions = {}

        # Place agents and environment
        self.place_agents()
        self.place_food()
        self.place_obstacles()

    def place_agents(self):
        for i in range(self.num_agents):
            ant = Ant(i, self)
            self.schedule.add(ant)
            self.grid.place_agent(ant, (randint(0, self.grid.width - 1), randint(0, self.grid.width - 1)))

    def place_food(self):
        self.food_positions[(1, 1)] = 'C'  # Food location

    def place_obstacles(self):
        obstacles = [(10, 14), (11, 14), (10, 15), (11, 15)]
        for pos in obstacles:
            self.obstacle_positions[pos] = 'O'

    def place_pheromone(self, pos):
        if pos not in self.pheromone_positions:
            self.pheromone_positions[pos] = 'F'

    def step(self):
        self.schedule.step()

# Visualization
def agent_portrayal(agent):
    if isinstance(agent, Ant):
        return {"Shape": "circle", "Color": "red", "r": 0.8, "Layer": 1}
    return {}

def portrayal_method(cell, model):
    portrayal = {}
    if not isinstance(cell, list):
        cell = [cell]
    for obj in cell:
        portrayal.update(agent_portrayal(obj))
    for pos, obj in model.food_positions.items():
        if pos == cell:
            portrayal.update({"Shape": "rect", "Color": "green", "w": 0.9, "h": 0.9, "Layer": 0})
    for pos, obj in model.obstacle_positions.items():
        if pos == cell:
            portrayal.update({"Shape": "rect", "Color": "black", "w": 0.9, "h": 0.9, "Layer": 0})
    for pos, obj in model.pheromone_positions.items():
        if pos == cell:
            portrayal.update({"Shape": "circle", "Color": "blue", "r": 0.4, "Layer": 0})
    return portrayal

# Update the CanvasGrid initialization
def portrayal_method_with_model(model):
    return lambda cell: portrayal_method(cell, model)

model = AntModel()
grid = CanvasGrid(portrayal_method_with_model(model), 25, 25, 500, 500)

server = ModularServer(AntModel, [grid], "Ant Search Model", {"num_ants": 5})
server.port = 8521  # Default Mesa port
server.launch()
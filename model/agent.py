from mesa import Agent
import networkx as nx
import matplotlib.pyplot as plt
import random


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, goal, init_model, pos, patience = 5):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.goal = goal # The goal position of the car
        self.pos = pos # The current position of the car initialized where the car is spawned
        self.patience = random.randint(patience, patience * 2) # The patience of the car
        self.map = init_model # The map of the city in order to calculate the shortest path
        self.path = [] # The path that the car will follow
        self.dir = " " # The direction of the car
    
        self.calculate_A_star(self.pos, self.goal) # Shortest path from spwawn to goal
                
    def calculate_A_star(self, pos, dest): 
        """ 
        Calculate the shortest path from pos to dest using A* algorithm
        """       
        try:            
            path = nx.shortest_path(self.map, pos, dest, weight='weight') # Calculate the shortest path
            path = path[::-1] #reverse the path
            # path.pop() # Remove the first element of the path
            self.path = path # Set the path
            
            return []
        except nx.NodeNotFound:
            print("Either the source or the destination node does not exist in the graph.")
            return []
        
    def check_diagonal(self):
        """
        Checks if the car can move diagonally
        """
        if self.dir == " ": # If the car is not moving
            return False
        
        dict = {"Up": (1, 0), "Down": (-1, 0), "Right": (0, -1), "Left": (0, 1)} # Dictionary to get the "right" if the car
        
        all_neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False) # Get all the neighbors of the car
        
        for neighbor in all_neighbors: # For each neighbor
            if self.pos[0] + dict[self.dir][0] == neighbor.pos[0] and self.pos[1] + dict[self.dir][1] == neighbor.pos[1]:
                if isinstance(neighbor, Car) and self.path[-1][0] != self.pos[0] and self.path[-1][1] != self.pos[1]: # If the neighbor is a car and the car is not moving
                    self.patience -= 1
                    return True
        
        else:
            return False
        
    def move(self): 
        """ 
        Determines if the agent can move in the direction that was chosen
        """      
        if self.path == []: # If the path is empty
            return 
        
        neighbors = self.model.grid.get_cell_list_contents(self.path[-1]) # Get the neighbors of the car
        
        for agent in neighbors:
            if isinstance(agent, Car) and self.unique_id != agent.unique_id: # If the neighbor is a car and the car is not moving
                self.patience -= 1 # Decrease the patience
                return #do not move
            elif isinstance(agent, Traffic_Light): # If the neighbor is a traffic light
                if not agent.state:                    
                    return #do not move
            # elif (self.check_diagonal()):
            #     return
            elif isinstance(agent, Destination): # If the neighbor is a destination
                self.model.schedule.remove(self) # Remove the car from the schedule
                self.model.grid.remove_agent(self) # Remove the car from the grid
                self.model.car_count -= 1         
                self.model.arrived_cars += 1       
                return
            elif isinstance(agent, Road): # If the neighbor is a road
                self.dir = agent.direction
                 
        self.model.grid.move_agent(self, self.path[-1]) # Move the car to the next position
        self.path.pop() # Remove the last element of the path
        
    def out_of_patience(self): 
        edges = nx.edges(self.map, [self.pos]) # Get the edges of the current position of the car
        for edge in edges:         
            if edge[1] == self.path[-1]: # If the edge is the same as the next position of the car
                self.map.edges[edge]['weight'] += 5 # Increase the weight of the edge
                self.patience = random.randint(5, 10) # Reset the patience
        
        self.calculate_A_star(self.pos, self.goal) # Calculate a new path
        

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        if self.patience <= 0: # If the patience is 0
            self.out_of_patience() # Call the out_of_patience function
        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state # False = Red, True = Green
        self.timeToChange = timeToChange # After how many steps should the traffic light change color

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0: # If the time to change is reached
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

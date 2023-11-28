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
    def __init__(self, unique_id, model, goal, init_model, pos, mode = False):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.start = self.pos # The starting position of the car
        self.goal = goal # The goal position of the car
        self.pos = pos # The current position of the car initialized where the car is spawned
        self.patience = random.randint(5, 10) # The patience of the car
        self.map = init_model # The map of the city in order to calculate the shortest path
        self.mode = mode # A tester mode if true it means that the car is in the tester mode and it will not move
        self.path = [] # The path that the car will follow
        
        self.calculate_A_star(self.pos, self.goal) # Shortest path from spwawn to goal
                
    def calculate_A_star(self, pos, dest): 
        """ 
        Calculate the shortest path from pos to dest using A* algorithm
        """       
        try:            
            path = nx.shortest_path(self.map, pos, dest, weight='weight') # Calculate the shortest path
            path = path[::-1] #reverse the path
            self.path = path # Set the path
            return []
        except nx.NodeNotFound:
            print("Either the source or the destination node does not exist in the graph.")
            return []
        
    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """       
        if self.path == []:
            return
        
        neighbors = self.model.grid.get_cell_list_contents(self.path[-1])
        for agent in neighbors:
            if isinstance(agent, Car): 
                if agent.unique_id == self.unique_id:
                    # print("Same car")
                    continue
                else:
                    self.patience = 0
                    return
            if isinstance(agent, Destination):
                self.model.schedule.remove(self)
                self.model.grid.remove_agent(self)
                self.model.car_count -= 1         
                self.model.arrived_cars += 1       
                return
            if isinstance(agent, Traffic_Light):
                if not agent.state:                    
                    return
                else:
                    # print("Green light")
                    break
        
        self.model.grid.move_agent(self, self.path[-1])
        # self.patience += 1
        self.path.pop()
        
    def plot_graph(self, graph):
        pos = {node: (node[0], -node[1]) for node in graph.nodes}  # Flip y-axis for visualization
        nx.draw(graph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_color='black')
        labels = nx.get_edge_attributes(graph,'weight')
        nx.draw_networkx_edge_labels(graph,pos,edge_labels=labels)
        plt.show()
        
    def out_of_patience(self):
        edges = nx.edges(self.map, [self.pos])        
        for edge in edges:
            if edge[0][1] == edge[1][1] or edge[0][0] == edge[1][0]:                
                content = self.model.grid.get_cell_list_contents(edge)  
                if not any(isinstance(x, Car) for x in content):  # if the agent is a random agent                
                    self.map.edges[edge]['weight'] += 5
                    self.patience = random.randint(5, 10)
                # self.plot_graph(self.map)
        
        self.calculate_A_star(self.pos, self.goal)
        

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        if self.mode:
            return
        if self.patience <= 0:
            self.out_of_patience()
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
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
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

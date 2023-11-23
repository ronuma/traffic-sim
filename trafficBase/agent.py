from mesa import Agent
import networkx as nx

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, goal, init_model, pos):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.start = self.pos
        self.goal = goal
        self.pos = pos
        #reverse the path
        self.map = init_model
        self.path = self.calculate_A_star()
                
    def calculate_A_star(self):        
        try:
            print("Calculating path from", self.pos, "to", self.goal)
            path = nx.shortest_path(self.map, self.pos, self.goal)            
            path = path[::-1] #reverse the path
            return path
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
                    # print("Car in front")
                    return
            if isinstance(agent, Destination):
                self.model.schedule.remove(self)
                self.model.grid.remove_agent(self)
                print("Car arrived")
                return
            if isinstance(agent, Traffic_Light):
                if not agent.state:
                    # print("Red light")
                    return
                else:
                    # print("Green light")
                    break
        
        self.model.grid.move_agent(self, self.path[-1])
        self.path.pop()
        

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
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
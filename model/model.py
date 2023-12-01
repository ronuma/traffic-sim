from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import Car, Road, Traffic_Light, Obstacle, Destination
import json
import random
import networkx as nx
import matplotlib.pyplot as plt

class CityModel(Model):
    """ 
    Creates a model based on a city map with one-way streets.
    Args:
        N: Number of agents in the simulation (assuming 1 for a single car)
    """
    def __init__(self, diagonales = 1.5, paciencia = 1, semaforos = 5):
        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
            self.dataDictionary = json.load(open("city_files/mapDictionary.json"))
            self.map = 0 # The map of the city
            self.destinations = [] # The list of destinations
            self.step_count = 0 # The number of steps that have passed
            self.car_count = 0 # The number of cars that have been created
            self.total_cars = 0 # The total number of cars that have been created
            self.arrived_cars = 0 # The number of cars that have arrived at their destination 
            #variables for sliders
            self.diagonales = diagonales # parameter for the weight of the diagonals by slider
            self.paciencia = paciencia # parameter for the patience of the cars by slider
            self.semaforos = semaforos # parameter for the weight of the traffic lights by slider
            
            self.traffic_lights = []
            graph = nx.DiGraph()  # Change to directed graph     

            # Load the map file. The map file is a text file where each character represents an agent.
            with open('city_files/2023_base.txt') as baseFile:
                lines = baseFile.readlines() # Read the lines of the file
                self.width = len(lines[0]) - 1 # The width of the map
                self.height = len(lines) # The height of the map
                
                # The spawn points of the cars
                self.spawn_points = [(0, 0), (self.width - 1, 0), (0,self.height - 1), (self.width - 1, self.height - 1)]
                
                self.grid = MultiGrid(self.width, self.height, torus=False) # The grid where the agents are placed
                self.schedule = RandomActivation(self) # The schedule of the agents
                
                self.map = self._init_Graph(graph, lines, self.dataDictionary)
                
                self.running = True
                
                self.add_cars()

                # Goes through each character in the map file and creates the corresponding agent.
        
    def _init_Graph(self, graph, lines, dataDictionary):
            for r, row in enumerate(lines): # r = row, c = column
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]: # If the character is a road
                        agent = Road(f"r_{r * self.width + c}", self, dataDictionary[col]) # Create a new road agent
                        self.grid.place_agent(agent, (c, self.height - r - 1)) # Place the agent in the grid
                        graph.add_node((c, self.height - r - 1), direction=col)  # Add direction as an attribute

                    elif col in ["S", "s"]: # If the character is a traffic light
                        agent = Traffic_Light(f"tl_{r * self.width + c}", self, False if col == "S" else True, int(dataDictionary[col])) # Create a new traffic light agent
                        self.grid.place_agent(agent, (c, self.height - r - 1))  # Place the agent in the grid
                        self.schedule.add(agent) # Add the agent to the schedule
                        self.traffic_lights.append(agent)
                        # Add an attribute to mark "S" as "long" and "s" as "short"
                        graph.add_node((c, self.height - r - 1), direction=None, signal_type="long" if col == "S" else "short")
                        # print("signal_type: ", graph.nodes[(c, self.height - r - 1)]['signal_type'])

                    elif col == "#": # If the character is an obstacle
                        agent = Obstacle(f"ob_{r * self.width + c}", self) # Create a new obstacle agent
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D": # If the character is a destination
                        agent = Destination(f"d_{r * self.width + c}", self) # Create a new destination agent
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        graph.add_node((c, self.height - r - 1), direction=None)  # No direction for destination
                        self.destinations.append((c, self.height - r - 1)) # Add destination pos to the list
                        
            for node in graph.nodes:                
                x, y = node                
                
                if graph.nodes[node]['direction'] == "^":
                    self.adding_edges(graph, node, x, y, 0, 1, [(x - 1, y + 1), (x + 1, y + 1), (x, y + 1), (x - 1 , y), (x + 1, y)], [">", "<"])
                    #adding_edges(graph, node, x, y, direccionY, direccionY, neighbors a conectar, caracteres especiales)
                
                if graph.nodes[node]['direction'] == "v":
                    self.adding_edges(graph, node, x, y, 0, -1, [(x + 1, y - 1), (x - 1, y - 1),(x, y - 1), (x + 1, y), (x - 1, y)], ["<", ">"])
                
                if graph.nodes[node]['direction'] == "<":
                    self.adding_edges(graph, node, x, y, -1, 0, [(x - 1, y - 1), (x - 1, y + 1), (x - 1, y), (x, y - 1), (x, y + 1)], ["^", "v"])
                      
                if graph.nodes[node]['direction'] == ">":
                    self.adding_edges(graph, node, x, y, 1, 0, [(x + 1, y - 1), (x + 1, y + 1), (x + 1, y), (x, y - 1), (x, y + 1)], ["^", "v"])
                
            return graph     
    
    def adding_edges(self, graph, node, x, y, xVal, yVal, neighbors, chars):
        for neighbor in neighbors: 
                if neighbor in graph.nodes: # If the neighbor is in the graph
                    if graph.nodes[neighbor]['direction'] in chars and ( neighbor == neighbors[0] or neighbor == neighbors[1]):
                        # If the neighbor is a diagonal and is one of the special characters do not add an edge
                        print("")                        
                    elif (neighbor == neighbors[3] and graph.nodes[neighbor]['direction'] == chars[1]) or (neighbor == neighbors[4] and graph.nodes[neighbor]['direction'] == chars[0]):
                        # If the neighbor is a cross and is one of the special characters add an edge
                        graph.add_edge(node, neighbor, weight=1)
                    elif neighbor == neighbors[2]: 
                        # If the neighbor is not a diagonal add an edge                                
                        graph.add_edge(node, neighbor, weight=1)
                    elif neighbor != neighbors[3] and neighbor != neighbors[4]:
                        # If the neighbor is a diagonal and is not one of the special characters add an edge
                        graph.add_edge(node, neighbor, weight=self.diagonales)
        
        # Add edges to the traffic lights depending in which direction they are facing
        if (x + xVal, y + yVal) in graph.nodes and 'signal_type' in graph.nodes[(x + xVal, y + yVal)] and graph.nodes[(x + xVal, y + yVal)]['signal_type'] in ["long", "short"]:
            graph.add_edge((x + xVal, y + yVal), (x + (xVal * 2), y + (yVal * 2)), weight=self.semaforos * 5)
        
        
        
    def add_cars(self):
        isBlocked = True
        for car in range(len(self.spawn_points)):
                    dest = random.choice(self.destinations) #choose a random destination
                    new_map = self.map.copy() #copy the map              
                    agent = Car(f"c_{self.total_cars}", self, dest, new_map, self.spawn_points[car], self.paciencia) #create a new car
                    content = self.grid.get_cell_list_contents(self.spawn_points[car])
                    if any(isinstance(x, Car) for x in content):  # if there is alreade a agent in the cell do not add a new one                          
                        break
                    else:
                        self.grid.place_agent(agent, self.spawn_points[car]) #place the agent in the grid
                        self.schedule.add(agent)  # Add the agent to the schedule
                        self.car_count += 1 
                        self.total_cars += 1
                        isBlocked = False
        
        if isBlocked: #if there is no space for a new car
            self.running = False #stop the simulation
        
        

    def plot_graph(self, graph):
        pos = {node: (node[0], -node[1]) for node in graph.nodes}  # Flip y-axis for visualization
        nx.draw(graph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_color='black')
        labels = nx.get_edge_attributes(graph,'weight')
        nx.draw_networkx_edge_labels(graph,pos,edge_labels=labels)
        plt.show()

    def step(self):
        if self.step_count%3 == 0 and self.step_count != 0: #every n steps add a new car
            self.add_cars()
        self.step_count += 1
        self.schedule.step()  
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
    def __init__(self):
        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
            self.dataDictionary = json.load(open("city_files/mapDictionary.json"))
            self.map = 0
            self.destinations = []
            self.step_count = 0
            self.car_count = 0
            self.traffic_lights = []
            graph = nx.DiGraph()  # Change to directed graph                                    

            # Load the map file. The map file is a text file where each character represents an agent.
            with open('city_files/2022_base.txt') as baseFile:
                lines = baseFile.readlines()
                self.width = len(lines[0]) - 1
                self.height = len(lines)
                
                self.spawn_points = [(0,0)]

                self.grid = MultiGrid(self.width, self.height, torus=False)
                self.schedule = RandomActivation(self)
                
                self.map = self._init_Graph(graph, lines, self.dataDictionary)
                
                self.running = True
                
                self.add_cars()

                # Goes through each character in the map file and creates the corresponding agent.
        
    def _init_Graph(self, graph, lines, dataDictionary):
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r * self.width + c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        graph.add_node((c, self.height - r - 1), direction=col)  # Add direction as an attribute

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r * self.width + c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)
                        # Add an attribute to mark "S" as "long" and "s" as "short"
                        graph.add_node((c, self.height - r - 1), direction=None, signal_type="long" if col == "S" else "short")
                        # print("signal_type: ", graph.nodes[(c, self.height - r - 1)]['signal_type'])

                    elif col == "#":
                        agent = Obstacle(f"ob_{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r * self.width + c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        graph.add_node((c, self.height - r - 1), direction=None)  # No direction for destination
                        self.destinations.append((c, self.height - r - 1)) # Add destination pos to the list

        
            for node in graph.nodes:
                x, y = node
                # x1,y1 = neighbor_node

                # UP
                if graph.nodes[node]['direction'] == "^":
                    if (x, y + 1) in graph.nodes and 'signal_type' in graph.nodes[(x, y + 1)]:
                        if graph.nodes[(x, y + 1)]['signal_type'] == "long" or graph.nodes[(x, y + 1)]['signal_type'] == "short":
                            neighbors = [
                                (x + 1, y + 1),
                                (x - 1, y + 1),
                                (x, y + 1)
                            ]
                            for neighbor in neighbors:
                                if neighbor in graph.nodes:
                                    direction = graph.nodes[node]['direction']
                                    graph.add_edge(node, neighbor, weight=direction)
                                    # graph.add_edge(neighbor, (x, y - 2), weight=direction)
                            graph.add_edge((x, y + 1), (x, y + 2), weight=direction)
                    else:
                        neighbors = [
                            (x + 1, y + 1),
                            (x - 1, y + 1),
                            (x, y + 1)
                        ]
                        for neighbor in neighbors:
                            if neighbor in graph.nodes:
                                direction = graph.nodes[node]['direction']
                                graph.add_edge(node, neighbor, weight=direction)
                
                #DOWN
                if graph.nodes[node]['direction'] == "v":
                    if (x, y - 1) in graph.nodes and 'signal_type' in graph.nodes[(x, y -1)]:
                        if graph.nodes[(x, y - 1)]['signal_type'] == "long" or graph.nodes[(x, y - 1)]['signal_type'] == "short":
                            neighbors = [
                                (x + 1, y - 1),
                                (x - 1, y - 1),
                                (x, y - 1)
                            ]
                            for neighbor in neighbors:
                                if neighbor in graph.nodes:
                                    direction = graph.nodes[node]['direction']
                                    graph.add_edge(node, neighbor, weight=direction)
                                    #add next edge to S node
                                    # graph.add_edge(neighbor, (x, y + 2), weight=direction)
                            graph.add_edge((x, y - 1), (x, y - 2), weight=direction)
                                
                    else:
                        neighbors = [
                            (x + 1, y - 1),
                            (x - 1, y - 1),
                            (x, y - 1)
                        ]
                        for neighbor in neighbors:
                            if neighbor in graph.nodes:
                                direction = graph.nodes[node]['direction']
                                graph.add_edge(node, neighbor, weight=direction)
                
                #LEFT
                if graph.nodes[node]['direction'] == "<":
                    if (x - 1, y) in graph.nodes and 'signal_type' in graph.nodes[(x - 1, y)]:
                        if graph.nodes[(x - 1, y)]['signal_type'] == "long" or graph.nodes[(x - 1, y)]['signal_type'] == "short":
                            neighbors = [
                                (x - 1, y + 1),
                                (x - 1, y - 1),
                                (x - 1, y)
                            ]
                            for neighbor in neighbors:
                                if neighbor in graph.nodes:
                                    direction = graph.nodes[node]['direction']
                                    graph.add_edge(node, neighbor, weight=direction)
                                    # graph.add_edge(neighbor, (x + 2, y), weight=direction)
                            graph.add_edge((x - 1, y), (x - 2, y), weight=direction)
                    else:
                        neighbors = [
                            (x - 1, y + 1),
                            (x - 1, y - 1),
                            (x - 1, y)
                        ]
                        for neighbor in neighbors:
                            if neighbor in graph.nodes:
                                direction = graph.nodes[node]['direction']
                                graph.add_edge(node, neighbor, weight=direction)
                #Right
                if graph.nodes[node]['direction'] == ">":
                    if (x + 1, y) in graph.nodes and 'signal_type' in graph.nodes[(x + 1, y)]:
                        if graph.nodes[(x + 1, y)]['signal_type'] == "long" or graph.nodes[(x + 1, y)]['signal_type'] == "short":
                            neighbors = [
                                (x + 1, y + 1),
                                (x + 1, y - 1),
                                (x + 1, y)
                            ]
                            for neighbor in neighbors:
                                if neighbor in graph.nodes:
                                    direction = graph.nodes[node]['direction']
                                    graph.add_edge(node, neighbor, weight=direction)
                                    # graph.add_edge(neighbor, (x - 2, y), weight=direction)
                            graph.add_edge((x + 1, y), (x + 2, y), weight=direction)
                    else:
                        neighbors = [
                            (x + 1, y + 1),
                            (x + 1, y - 1),
                            (x + 1, y)
                        ]
                        for neighbor in neighbors:
                            if neighbor in graph.nodes:
                                direction = graph.nodes[node]['direction']
                                graph.add_edge(node, neighbor, weight=direction)
                                
            self.plot_graph(graph)
            return graph          
        
    def add_cars(self):
        for car in range(len(self.spawn_points)):                           
                    dest = random.choice(self.destinations) #choose a random destination
                    agent = Car(f"c_{self.car_count}", self, dest, self.map, self.spawn_points[car])
                    self.grid.place_agent(agent, self.spawn_points[car])
                    self.schedule.add(agent)      
                    self.car_count += 1 


    def plot_graph(self, graph):
        pos = {node: (node[0], -node[1]) for node in graph.nodes}  # Flip y-axis for visualization
        nx.draw(graph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_color='black')
        # plt.show()

    def step(self):
        # if self.step_count%20 == 0 and self.step_count != 0:
        #     self.add_cars()
            
        self.step_count += 1
        self.schedule.step()
from agent import *
from model import CityModel
from mesa.visualization import CanvasGrid, BarChartModule
from mesa.visualization import ModularServer
from mesa.visualization.modules import TextElement

from mesa.visualization import Slider


def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1
                 }

    if (isinstance(agent, Road)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
        
    if (isinstance(agent, Car)):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 1
    
    if (isinstance(agent, Destination)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    return portrayal

width = 0
height = 0

with open('./city_files/2023_base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {
    "diagonales": Slider("Respetuosos", 1.5, 0.5, 5.0, 0.1),
    "paciencia": Slider("Pascientes", 1.0, 1.0, 10.0, 1.0),
    "semaforos": Slider("Energicos", 1.0, 1.0, 40.0, 5.0),
}


print(width, height)
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

class CurrentCars(TextElement):
    def render(self, model):
        return "Cars on scene: " + str(model.car_count) + " "
    
class ArrivedCars(TextElement):
    def render(self, model):
        return "Arrived cars: " + str(model.arrived_cars) + " "

server = ModularServer(CityModel, [grid, CurrentCars(), ArrivedCars()], "Traffic Base", model_params)
                       
server.port = 8521 # The default
server.launch()
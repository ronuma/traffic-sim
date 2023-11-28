# Python flask server to interact with Unity. Based on the code provided by Octavio Navarro.
# Rodrigo Nunez. November 2023

from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light

app = Flask("Traffic simulation")

model = None
current_step = 0

@app.route('/init', methods=['GET', 'POST'])
def initModel():
    global model, current_step
    if request.method == 'GET':
        current_step = 0
        model = CityModel()
        return jsonify({"message":"Model initiated."})

    
@app.route('/getAgents', methods=['GET'])
def getAgents():
    global model
    if request.method == 'GET':
        agent_positions = [{"id": a.unique_id, "x": a.pos[0], "y":0, "z":a.pos[1]}
                          for a in model.schedule.agents
                          if isinstance(a, Car)]
        traffic_lights = [{"id": a.unique_id, "x": a.pos[0], "y":0, "z":a.pos[1], "state":a.state}
                          for a in model.schedule.agents
                          if isinstance(a, Traffic_Light)]
        return jsonify({'positions':agent_positions},
                       {'traffic_lights':traffic_lights})

@app.route("/update", methods=['GET'])
def updateModel():
    global current_step, model
    if request.method == 'GET':
        model.step()
        current_step += 1
        return jsonify({'message':f'Model updated to step {current_step}.', 'current_step':current_step})
    
if __name__ == '__main__':
    app.run(debug=True, port = 8585, host = "localhost")
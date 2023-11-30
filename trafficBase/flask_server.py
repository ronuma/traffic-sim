# Python flask server to interact with Unity. Based on the code provided by Octavio Navarro.
# Rodrigo Nunez. November 2023

from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light
import requests
import json

app = Flask("Traffic simulation")

send_car_count_endpoint = "http://52.1.3.19:8585/api/validate_attempt"

model = None
current_step = 0

@app.route('/init', methods=['GET'])
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
        traffic_lights = [{"id": a.unique_id, "x": a.pos[0], "y":0, "z":a.pos[1], "isGreen":a.state}
                          for a in model.schedule.agents
                          if isinstance(a, Traffic_Light)]
        return jsonify({'positions':agent_positions,
                       'traffic_lights':traffic_lights})

@app.route("/update", methods=['GET'])
def updateModel():
    global current_step, model
    if request.method == 'GET':
        model.step()
        current_step += 1
        if current_step % 100 == 0:
            send_car_count()
        return jsonify({'message':f'Model updated to step {current_step}.', 'current_step':current_step})
    
def send_car_count():
    global model
    data = {
        "year" : 2023,
        "classroom" : 301,
        "name" : "Gabi y Ro",
        "num_cars": model.car_count
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(send_car_count_endpoint, data=json.dumps(data), headers=headers)
    print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
    print("Response:", response.json())
    
if __name__ == '__main__':
    app.run(debug=True, port = 8585, host = "localhost")
# Python flask server to interact with Unity. Based on the code provided by Octavio Navarro.
# Rodrigo Nunez. November 2023

from flask import Flask, request, jsonify

app = Flask("Traffic simulation")

test_positions = [{"id": 1, "x": 0, "y":0, "z":0.3}, {"id": 2, "x": 0, "y":0, "z":0.9}
                  , {"id": 3, "x": 0.4, "y":0, "z":0}, {"id": 4, "x": 0.5, "y":0, "z":0}]

@app.route('/init', methods=['GET', 'POST'])
def initModel():
    if request.method == 'POST':
        print(request.form)
        return jsonify({"message":"Parameters recieved, model initiated."})
    elif request.method == 'GET':
        return jsonify({"message":"Default parameters recieved, model initiated."})
    
@app.route('/getAgents', methods=['GET'])
def getAgents():
    if request.method == 'GET':
        return jsonify({'positions':test_positions})

@app.route("/update", methods=['GET'])
def updateModel():
    if request.method == 'GET':
        # test_positions[0]["x"] += 1
        # test_positions[1]["x"] += 1
        # test_positions[2]["x"] += 1
        # test_positions[3]["x"] += 1
        return jsonify({"message":"Model updated."})
    
if __name__ == '__main__':
    app.run(debug=True, port = 8585, host = "localhost")
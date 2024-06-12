import numpy as np
from flask import Flask, request, jsonify
import json
from datetime import datetime, timezone
import pytz
from flask_httpauth import HTTPBasicAuth

sensoraction = []

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "mathijs": "test"

}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] ==password:
        return username




@app.route('/get-action', methods=["GET"])
@auth.login_required
def returnsensoraction():
    return jsonify(sensoraction)

@app.route("/sensor", methods=["POST"])
@auth.login_required
def addsensoraction():
    data = request.get_json()
    
    if data and "id" in data:
        sensor_id = data["id"]
        amsterdam_tz = pytz.timezone('Europe/Amsterdam')
        timestamp = datetime.now(amsterdam_tz).strftime('%Y-%m-%d %H:%M:%S')
        sensoraction.append({"id": sensor_id, "timestamp": timestamp})
        return jsonify({"message": "Sensor action added", "sensor_id": sensor_id, "timestamp": timestamp}), 201
    else:
        return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)

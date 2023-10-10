from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

app = Flask(__name__)

data_storage = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(f"HyCh/raw_shots/{userdata}")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    
    rw_data = data.get("RW", [])[0]
    rw_values = [int(rw_data[i:i+2], 16) for i in range(0, len(rw_data), 2)]
    data["RW"] = rw_values
    
    timestamp = int(data.get("date", 0))
    formatted_date = datetime.utcfromtimestamp(timestamp).strftime('%d.%m.%y %H:%M')
    data["date"] = formatted_date
    
    formatted_data = json.dumps(data, indent=4)
    data_storage[userdata] = formatted_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    uid = request.json.get('uid')
    if not uid:
        return jsonify({'error': 'UID is empty'})

    client = mqtt.Client(userdata=uid)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mq.emercit.com", 1883, 60)
    client.loop_start()

    for _ in range(100):
        if uid in data_storage:
            break
        time.sleep(0.1)

    client.loop_stop()
    client.disconnect()

    data = data_storage.pop(uid, 'No data received')
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run(debug=True)

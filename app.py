"""
Web interface for configuring "SL20" ultrasonic level meters based on PGA460.

This module provides a Flask-based web application that allows users to interact with 
and configure "SL20" ultrasonic level meters.
"""

import json
import time
from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
from message_handler import MQTTMessageHandler

app = Flask(__name__)

data_storage = {}


def on_connect(client, userdata, _, rc):
    """
    Callback function for when the client successfully connects to the MQTT broker.

    Args:
    - client: The client instance for this callback.
    - userdata: Private user data as set in Client() or userdata_set().
    - rc: Connection result.
    """
    print("Connected with result code "+str(rc))
    client.subscribe(f"HyCh/raw_shots/{userdata}")


def on_message(_, userdata, msg):
    """
    Callback function for when a message is received from the subscribed topic.

    Args:
    - userdata: Private user data as set in Client() or userdata_set().
    - msg: An instance of MQTTMessage. This is a class with members topic, payload, qos, retain.
    """
    handler = MQTTMessageHandler(msg)
    handler.process_message()

    data = {
        "PG": handler.pg,
        "RW_X": handler.rw_x,
        "RW_Y": handler.rw_y,
        "date": handler.date
    }

    formatted_data = json.dumps(data, indent=4)
    data_storage[userdata] = formatted_data


@app.route('/')
def index():
    """Render the main page of the web application."""
    return render_template('index.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    """
    Endpoint to fetch processed MQTT data based on a provided UID.

    Returns:
    - JSON response containing the processed data or an error message.
    """
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

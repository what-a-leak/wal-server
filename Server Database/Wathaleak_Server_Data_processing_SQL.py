import sqlite3
import paho.mqtt.client as mqtt
import json
import time

# Function to save sensor measurement data to database
def save_data(node_id, mesure, status):
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO Data (timestamp, NodeID, MesureCapteur, Status) VALUES (?, ?, ?, ?)",   # Rajouter les timestamps a l'UML apres la presentation
                   (timestamp, node_id, mesure, status))
    conn.commit()
    conn.close()

# Function to classify the measurement value
def classify_value(value):
    if value < 10:
        return "Critical"
    elif value < 20:
        return "Bad"
    else:
        return "Good"

# Function to generate JSON file from Data table
def export_to_json():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Data")
    rows = cursor.fetchall()

    # Create a list of dictionaries for JSON
    data_list = []
    for row in rows:
        data_dict = {
            "timestamp": row[0],
            "NodeID": row[1],
            "MesureCapteur": row[2],
            "Status": row[3]
        }
        data_list.append(data_dict)

    # Save to JSON file
    with open("sensor_data.json", "w") as json_file:
        json.dump(data_list, json_file, indent=4)
    
    conn.close()

# Function triggered for each received MQTT message
def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    node_id = data["node_id"]
    mesure = data["value"]

    # Classification and saving
    status = classify_value(mesure)
    save_data(node_id, mesure, status)

    # Update the JSON file for mobile app
    export_to_json()

# MQTT client setup
client = mqtt.Client()
client.connect("localhost")
client.subscribe("sensors/data")
client.on_message = on_message

# Main loop for listening to MQTT messages
client.loop_forever()

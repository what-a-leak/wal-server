import sqlite3
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# Enregistre les données dans la base
def save_data(node_id, mesure, status, timestamp, batterie, temperature):
    conn = sqlite3.connect("wal_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Data (NodeID, MesureCapteur, Status, TimeStamp, Batterie, Temperature) VALUES (?, ?, ?, ?, ?, ?)", 
                   (node_id, mesure, status, timestamp, batterie, temperature))
    conn.commit()
    conn.close()

    generate_json_db()

# Attribue un statut en fonction de la valeur
def give_status(value):
    if value < 10:
        return "0"
    else:
        return "1"

##### AJOUT JSON TEst

def generate_json_db():
    conn = sqlite3.connect("wal_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Data")
    rows = cursor.fetchall()

    columns = [description[0] for description in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]

    with open("data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    conn.close()


# Réception des messages MQTT
def on_message(client, userdata, message):
    try:
        raw_payload = message.payload.decode()
        data = json.loads(raw_payload)
        node_id = data["node_id"]
        mesure = data["mesure"]
        status = give_status(mesure)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        batterie = data["batterie"]
        temperature = data["temperature"]     

        # Attribue un statut et sauvegarde
        print("New MQTT Message Received:\n"
            "Node ID: %d, Timestamp: %s, Measure: %s, Status: %s, Batterie: %d, Temperature: %d" 
            % (node_id, timestamp, mesure, status, batterie, temperature))
        save_data(node_id, mesure, status, timestamp, batterie, temperature)
    except:
        print("Raw Payload Received:", raw_payload)
        print("Message format invalid.")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to the MQTT Broker successfully!")
    else:
        print(f"Could not connect to the MQTT Broker: Verify configuration. ({rc})")
        exit(rc)

# Configuration MQTT
MQTT_BROKER = "localhost"  
MQTT_PORT = 1883
MQTT_USERNAME = ""  
MQTT_PASSWORD = ""  
MQTT_TOPIC = "sensors/data"

# Client MQTT
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)
client.on_message = on_message
client.on_connect = on_connect

# Boucle pour écouter les messages
print("Listening for MQTT messages...")
client.loop_forever()

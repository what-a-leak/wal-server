import sqlite3
import paho.mqtt.client as mqtt
import json
import time

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
     data = json.loads(message.payload.decode())
     node_id = data["node_id"]
     mesure = data["mesure"]
     status = give_status(mesure)
     timestamp = data["timestamp"]
     batterie = data["batterie"]
     temperature = data["temperature"]     

    # Attribue un statut et sauvegarde
     print("message recu !!!" + timestamp)
     save_data(node_id, mesure, status, timestamp, batterie, temperature)

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

# Boucle pour écouter les messages
print("En attente de messages MQTT...")
client.loop_forever()

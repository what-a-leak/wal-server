import paho.mqtt.client as mqtt
import json

# Configuration
MQTT_BROKER = ""
MQTT_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "sensors/data"

# Exemple de données
sensor_data = {
    "node_id": 1,
    "mesure": 23.5,
    "status": 1,
    "timestamp": "2025-01-08 14:30:00",
    "batterie": 90,
    "temperature": 25
}

# Connexion au serveur MQTT
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT)

# Publication des données
client.publish(MQTT_TOPIC, json.dumps(sensor_data))
print("Données envoyées avec succès.")

client.disconnect()

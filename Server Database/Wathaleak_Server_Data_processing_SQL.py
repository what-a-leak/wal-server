import sqlite3
import paho.mqtt.client as mqtt
import json
import time

# Fonction d'insertion des data dans la table
def save_data(node_id, mesure, status):
    conn = sqlite3.connect("wal_database.db")
    cursor = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO Datas (TimeStamp, NodeID, MesureCapteur, Status) VALUES (?, ?, ?, ?)",   # Rajouter les timestamps a l'UML apres la presentation
                   (timestamp, node_id, mesure, status))
    conn.commit()
    conn.close()

# Fonction donnant un status aux donnees traitees par IA. Elle appellera le script de traitement des donnees 
# L'exemple donne ci dessous sert de remplissage en attendant le remplacement par l'appel au cript.
def give_status(value):
    if value < 10:
        return "Critical"
    elif value < 20:
        return "Bad"
    else:
        return "Good"

# Fonction generant le fichier JSON a partir de la table Datas
def export_to_json():
    conn = sqlite3.connect("wal_database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Datas")
    rows = cursor.fetchall()

    # Cree liste de dictionnaires JSON
    data_list = []
    for row in rows:
        data_dict = {
            "TimeStamp": row[0],
            "NodeID": row[1],
            "MesureCapteur": row[2],
            "Status": row[3]
        }
        data_list.append(data_dict)

    # Save dans fichier JSON
    with open("sensor_data.json", "w") as json_file:
        json.dump(data_list, json_file, indent=4)
    
    conn.close()

# Fonction activant la reception des donnees avec Mosquitto. Voir les cours de MiddleWare
def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    node_id = data["node_id"]
    mesure = data["value"]

    # Don de status et sauvegarde json
    status = give_status(mesure)
    save_data(node_id, mesure, status)

    # Update du fichier JSON pour les app. a revoir et definir selon les besoins
    export_to_json()

# MQTT client setup
client = mqtt.Client()
client.connect("localhost")
client.subscribe("sensors/data")
client.on_message = on_message

# Main loop d ecoute de messages MQTT
client.loop_forever()

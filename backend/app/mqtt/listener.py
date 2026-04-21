import json
import paho.mqtt.client as mqtt
from services.raw_ingest import ingest_raw

BROKER = "localhost"
PORT = 1883
TOPIC = "coldchain/device/+/raw"

def on_connect(client, userdata, flags, rc):
    print("MQTT connected with code", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        ingest_raw(payload)
        print("RAW INGESTED:", payload["device_id"], payload["timestamp"])
    except Exception as e:
        print("MQTT ERROR:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

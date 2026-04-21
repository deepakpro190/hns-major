'''import time
import math
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timezone

# ===============================
# LOAD MODEL PARAMETERS
# ===============================
scaler = pd.read_csv("scaler_params.csv")
weights_df = pd.read_csv("logistic_model_weights.csv")

FEATURES = scaler["feature"].tolist()
MEAN = scaler["mean"].values
STD = scaler["std"].values

# Use HIGH_RISK class for alerting
W = weights_df[weights_df["class"] == "HIGH_RISK"][FEATURES].values[0]
B = weights_df[weights_df["class"] == "HIGH_RISK"]["bias"].values[0]

# ===============================
# SIMULATION CONFIG
# ===============================
DEVICE_ID = "esp32_sim_01"
BACKEND_URL = "http://127.0.0.1:8000/ingest/window"

# TEMP: keep small for testing (change to 300 later)
WINDOW_SECONDS = 1  

temp_buf, hum_buf, door_buf = [], [], []

# ===============================
# SENSOR SIMULATION
# ===============================
def simulate_temperature(t):
    if t < 900:
        return 5 + np.random.normal(0, 0.2)
    elif t < 1500:
        return 9 + np.random.normal(0, 0.4)
    else:
        return 6 + np.random.normal(0, 0.3)

def simulate_humidity():
    return 60 + np.random.normal(0, 2)

def simulate_door():
    return np.random.choice([0, 1], p=[0.97, 0.03])

# ===============================
# FEATURE EXTRACTION (CAST TO PYTHON TYPES)
# ===============================
def extract_features(temp, hum, door):
    temp = np.array(temp)
    hum = np.array(hum)
    door = np.array(door)

    temp_avg = float(temp.mean())
    temp_max = float(temp.max())
    temp_min = float(temp.min())
    temp_rate = float(abs(temp_max - temp_min) / (WINDOW_SECONDS / 60))
    time_outside = int(np.sum((temp < 2) | (temp > 8)))

    humidity_avg = float(hum.mean())
    humidity_variance = float(hum.var())
    humidity_spikes = int(np.sum(np.abs(np.diff(hum)) > 3))

    door_open_count = int(np.sum((door[1:] == 1) & (door[:-1] == 0)))
    door_open_duration = int(door.sum())

    max_open = 0
    current = 0
    for d in door:
        if d == 1:
            current += 1
            max_open = max(max_open, current)
        else:
            current = 0

    return [
        temp_avg,
        temp_max,
        temp_min,
        temp_rate,
        time_outside,
        humidity_avg,
        humidity_variance,
        humidity_spikes,
        door_open_count,
        door_open_duration,
        int(max_open)
    ]

# ===============================
# TINYML INFERENCE
# ===============================
def predict_risk(features):
    x_scaled = (np.array(features) - MEAN) / STD
    z = B + np.dot(W, x_scaled)
    return float(1 / (1 + math.exp(-z)))

# ===============================
# MAIN LOOP
# ===============================
t = 0
print("ESP32 SIMULATOR STARTED")

while True:
    temp_buf.append(simulate_temperature(t))
    hum_buf.append(simulate_humidity())
    door_buf.append(simulate_door())

    if len(temp_buf) == WINDOW_SECONDS:
        features = extract_features(temp_buf, hum_buf, door_buf)
        risk_prob = predict_risk(features)

        if risk_prob > 0.7:
            risk_class = "HIGH"
        elif risk_prob > 0.4:
            risk_class = "WARNING"
        else:
            risk_class = "SAFE"

        payload = {
            "device_id": DEVICE_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "features": dict(zip(FEATURES, features)),
            "risk_probability": float(risk_prob),
            "risk_class": risk_class
        }

        print(f"[SIM] {payload['timestamp']} → {risk_class} ({risk_prob:.2f})")
        print("SENDING PAYLOAD:", payload)

        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=5)
            print("BACKEND RESPONSE:", response.status_code, response.text)
        except Exception as e:
            print("POST FAILED:", e)

        temp_buf.clear()
        hum_buf.clear()
        door_buf.clear()

    t += 1
    time.sleep(1)
'''
import time
import json
import numpy as np
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# ===============================
# MQTT CONFIG
# ===============================
BROKER = "localhost"
PORT = 1883
DEVICE_ID = "esp32_sim_01"
TOPIC = f"coldchain/device/{DEVICE_ID}/raw"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# ===============================
# SENSOR SIMULATION
# ===============================
def simulate_temperature(t):
    if t < 900:
        return 5 + np.random.normal(0, 0.2)
    elif t < 1500:
        return 9 + np.random.normal(0, 0.4)
    else:
        return 6 + np.random.normal(0, 0.3)

def simulate_humidity():
    return 60 + np.random.normal(0, 2)

def simulate_door():
    return np.random.choice([0, 1], p=[0.97, 0.03])

# ===============================
# MAIN LOOP (1 SECOND)
# ===============================
t = 0
print("ESP32 MQTT SIMULATOR STARTED")

while True:
    payload = {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": float(simulate_temperature(t)),
        "humidity": float(simulate_humidity()),
        "door": int(simulate_door())
    }

    client.publish(TOPIC, json.dumps(payload), qos=0)
    print("PUBLISHED:", payload)

    t += 1
    time.sleep(1)

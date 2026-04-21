from collections import deque
from datetime import datetime, timezone

live_cache = {}
buffers = {}
WINDOW_SIZE = 30

def update_buffers(device_id, payload):
    if device_id not in buffers:
        buffers[device_id] = deque(maxlen=WINDOW_SIZE)

    buffers[device_id].append(payload)

    if device_id not in live_cache:
        live_cache[device_id] = {}

    live_cache[device_id].update({
        "temperature": payload["temperature"],
        "humidity": payload["humidity"],
        "door": payload["door"],
        "last_seen": payload["timestamp"],
        "device_status": "ONLINE"
    })

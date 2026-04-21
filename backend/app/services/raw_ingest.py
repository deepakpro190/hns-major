from db.database import get_connection
from services.buffer import update_buffers

def ingest_raw(payload: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO raw_sensor_data
        (device_id, timestamp, temperature, humidity, door)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        payload["device_id"],
        payload["timestamp"],
        payload["temperature"],
        payload["humidity"],
        payload["door"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    # update cache + rolling window
    update_buffers(payload["device_id"], payload)

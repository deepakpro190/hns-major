from db.database import get_connection

def ingest_transport(payload: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transport_context
        (device_id, timestamp, latitude, longitude, ambient_temp, traffic_index, speed)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        payload["device_id"],
        payload["timestamp"],
        payload["latitude"],
        payload["longitude"],
        payload["ambient_temp"],
        payload["traffic_index"],
        payload["speed"]
    ))

    conn.commit()
    cur.close()
    conn.close()

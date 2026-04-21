import time
from sqlalchemy import text
from db.database import SessionLocal
from services.models import predict_storage   # 🔥 H5 model

DEVICE_ID = "esp32_cc_01"

def start_aggregation_loop():
    while True:
        db = SessionLocal()

        try:
            # 🔍 Fetch last 30 sec data
            rows = db.execute(text("""
            SELECT temperature, humidity, door
            FROM raw_sensor_data
            WHERE device_id = :device_id
            ORDER BY timestamp DESC
            LIMIT 50
        """), {"device_id": DEVICE_ID}).fetchall()

            if len(rows) > 0:
                temps = [r[0] for r in rows]
                hums = [r[1] for r in rows]
                doors = [r[2] for r in rows]

                # 📊 FEATURES
                temp_avg = sum(temps) / len(temps)
                temp_max = max(temps)
                temp_min = min(temps)
                temp_var = (temp_max - temp_min) / 2

                temp_drift = temps[-1] - temps[0]

                humidity_avg = sum(hums) / len(hums)
                humidity_variance = (max(hums) - min(hums)) / 2

                door_open_count = sum(
                    1 for i in range(1, len(doors))
                    if doors[i] == 1 and doors[i - 1] == 0
                )

                excursion_time = sum(1 for t in temps if t > 8 or t < 2)
                thermal_stress = sum((t - 8) for t in temps if t > 8)

                # 🔥 STORE FEATURES
                db.execute(text("""
                    INSERT INTO window_features (
                        device_id, temp_avg, temp_max, temp_min, temp_variance,
                        humidity_avg, door_open_count, excursion_time, thermal_stress, timestamp
                    )
                    VALUES (
                        :device_id, :temp_avg, :temp_max, :temp_min, :temp_var,
                        :humidity_avg, :door_open_count, :excursion_time, :thermal_stress, NOW()
                    )
                """), {
                    "device_id": DEVICE_ID,
                    "temp_avg": temp_avg,
                    "temp_max": temp_max,
                    "temp_min": temp_min,
                    "temp_var": temp_var,
                    "humidity_avg": humidity_avg,
                    "door_open_count": door_open_count,
                    "excursion_time": excursion_time,
                    "thermal_stress": thermal_stress
                })

                # 🔥 MODEL PREDICTION (H5)
                features = [[
                    temp_avg,
                    temp_max,
                    temp_min,
                    temp_var,
                    temp_drift,
                    humidity_avg,
                    humidity_variance,
                    door_open_count,
                    excursion_time,
                    thermal_stress
                ]]

                risk = predict_storage(features)

                # 🎯 STATUS
                status = (
                    "CRITICAL" if risk > 0.7 else
                    "WARNING" if risk > 0.4 else
                    "SAFE"
                )

                # 🔥 STORE PREDICTION
                db.execute(text("""
                    INSERT INTO predictions (
                        device_id, xgb_risk, final_risk, status
                    )
                    VALUES (:device_id, :risk, :risk, :status)
                """), {
                    "device_id": DEVICE_ID,
                    "risk": risk,
                    "status": status
                })

            db.commit()    

        except Exception as e:
            print("Scheduler Error:", e)

        finally:
            db.close()

        time.sleep(30)
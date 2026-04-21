CREATE TABLE window_features (
    id SERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,

    temp_avg REAL,
    temp_max REAL,
    temp_min REAL,
    temp_rate REAL,
    time_outside_range_sec INTEGER,

    humidity_avg REAL,
    humidity_variance REAL,
    humidity_spike_count INTEGER,

    door_open_count INTEGER,
    door_open_duration_sec INTEGER,
    max_door_open_time_sec INTEGER,

    risk_probability REAL,
    risk_class TEXT
);

CREATE INDEX idx_window_time ON window_features(timestamp);
CREATE INDEX idx_device_time ON window_features(device_id, timestamp);

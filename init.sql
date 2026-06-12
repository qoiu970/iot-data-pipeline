CREATE TABLE IF NOT EXISTS sensor_data (
    timestamp TIMESTAMPTZ NOT NULL,
    sensor_name VARCHAR(255) NOT NULL,
    value NUMERIC NOT NULL,
    PRIMARY KEY (timestamp, sensor_name)
);
CREATE INDEX IF NOT EXISTS idx_sensor_name ON sensor_data(sensor_name);
CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp);
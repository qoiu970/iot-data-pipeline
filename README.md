# IoT Sensor Data Processing Pipeline

A robust, dockerized data pipeline designed to parse, validate, and ingest large volumes of IoT sensor data (CSV format) into a PostgreSQL database.

##  Features
* **Parallel Processing**: Utilizes Python's `ProcessPoolExecutor` to process multiple large CSV files concurrently, bypassing the GIL for CPU-bound tasks.
* **Data Validation & Cleansing**: Uses `pandas` to gracefully handle and filter out invalid data (e.g., non-ISO8601 timestamps, string values in numeric columns, corrupted characters).
* **Idempotency & Deduplication**: Database schema enforces unique constraints `(timestamp, sensor_name)`. Uses PostgreSQL's `ON CONFLICT DO NOTHING` for seamless bulk inserts without duplication errors.
* **Memory Efficient**: Implements chunk-based reading (`chunksize`) to ensure files larger than system memory (e.g., > 8GB) can be processed safely.

##  Tech Stack
* **Language**: Python 3.10
* **Database**: PostgreSQL 15
* **Libraries**: `pandas`, `psycopg2-binary`
* **Infrastructure**: Docker & Docker Compose

##  Project Structure
* `main.py`: Core pipeline logic (Parallel execution, Pandas data cleansing, DB bulk insert).
* `generate_chaos_data.py`: A mock data generator to create edge-case scenarios (e.g., corrupted timestamps, emoji sensor names, duplicated rows) for testing pipeline resilience.
* `init.sql`: Automated DB schema initialization.
* `docker-compose.yml`: One-click infrastructure setup.
* `data/`: Target directory for incoming CSV files.

##  Quick Start

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/qoiu970/iot-data-pipeline.git](https://github.com/qoiu970/iot-data-pipeline.git)
   cd iot-data-pipeline
   
##  (Optional) Generate Chaos Mock Data for testing:
```bash
pip install pandas numpy
python generate_chaos_data.py
```
Run the pipeline:
Ensure Docker Desktop is running, then execute:
```bash
docker compose up --build
```
The database will initialize automatically, and the Python workers will begin processing all .csv files located in the ./data directory.




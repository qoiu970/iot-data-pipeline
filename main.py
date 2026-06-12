import os
import glob
import logging
import pandas as pd
import psycopg2
import psycopg2.extras
from concurrent.futures import ProcessPoolExecutor, as_completed

# logging processing status
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DB config
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iot_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
TARGET_DIR = os.getenv("TARGET_DIR", "./data")

CHUNK_SIZE = 100000  
#CHUNK_SIZE = 10000 

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def process_file(file_path):
    """Parses a CSV file, cleans data, and bulk inserts into PostgreSQL."""
    logging.info(f"Worker started processing: {file_path}")
    conn = get_db_connection()
    cursor = conn.cursor()

    # handles duplicate records
    insert_query = """
        INSERT INTO sensor_data (timestamp, sensor_name, value)
        VALUES %s
        ON CONFLICT (timestamp, sensor_name) DO NOTHING;
    """

    try:
        # files > 8GB, streaming in parts
        for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
            
            # Data validation and cleansing
            chunk['timestamp'] = pd.to_datetime(chunk['timestamp'], format='ISO8601', errors='coerce', utc=True)
            chunk['value'] = pd.to_numeric(chunk['value'], errors='coerce')
            
            # Drop invalid rows
            clean_chunk = chunk.dropna(subset=['timestamp', 'sensorName', 'value'])

            if clean_chunk.empty:
                continue

            data_tuples = [
                (row.timestamp, row.sensorName, row.value) 
                for row in clean_chunk.itertuples(index=False)
            ]

            psycopg2.extras.execute_values(cursor, insert_query, data_tuples, page_size=10000)
            conn.commit() # Commit per chunk to free up DB transaction logs

        logging.info(f"Successfully processed: {file_path}")
        
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    csv_files = glob.glob(os.path.join(TARGET_DIR, "*.csv"))
    if not csv_files:
        logging.warning(f"No CSV files found in {TARGET_DIR}.")
        return

    logging.info(f"Found {len(csv_files)} files. Starting parallel processing...")

    # ProcessPool bypass Python GIL
    max_workers = min(os.cpu_count(), len(csv_files)) 
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, file): file for file in csv_files}
        
        for future in as_completed(futures):
            file = futures[future]
            try:
                future.result() 
            except Exception as e:
                logging.error(f"Fatal error in worker for file {file}: {e}")

    logging.info("Pipeline execution finished!")

if __name__ == "__main__":
    main()
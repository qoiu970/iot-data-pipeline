import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, timezone

def generate_mock_data(filename="data/file-chaos.csv", num_rows=10000):
    print(f"Starting to generate {num_rows} rows of mock data...")

    # Gen base normal data
    base_time = datetime(2023, 10, 1, tzinfo=timezone.utc)
    
    # Gen timestamps
    timestamps = [(base_time + timedelta(seconds=i)).isoformat() for i in range(num_rows)]
    sensors = [f"Sensor_{random.choice(['A', 'B', 'C', 'D'])}" for _ in range(num_rows)]
    
    # Random values between 0 and 100
    values = [round(random.uniform(0, 100), 2) for _ in range(num_rows)]

    df = pd.DataFrame({
        'timestamp': timestamps, 
        'sensorName': sensors, 
        'value': values
    })

    df = df.astype(object)

    # Inject edge cases (dirty data)
    chaos_ratio = 0.1  # 10% dirty data
    chaos_indices = random.sample(range(num_rows), int(num_rows * chaos_ratio))
    
    # print(f"DEBUG: Injecting bad data into {len(chaos_indices)} rows")
    
    for i in chaos_indices:
        issue_type = random.choice(['bad_time', 'bad_sensor', 'bad_value', 'multi_decimal', 'long_decimal'])
        
        if issue_type == 'bad_time':
            df.at[i, 'timestamp'] = random.choice(['invalid_time_string', '2023-99-99', 'not_a_date', '???'])
        elif issue_type == 'bad_sensor':
            # add CJK chars, emojis, special chars to test encoding
            df.at[i, 'sensorName'] = random.choice(['感測器甲', 'センサー_1', '센서_A', '🔥Sensor', 'sénsor#@!'])
        elif issue_type == 'bad_value':
            df.at[i, 'value'] = random.choice(['not_a_number', 'ABC', 'ERR_VALUE'])
        elif issue_type == 'multi_decimal':
            df.at[i, 'value'] = '10.5.2.1' 
        elif issue_type == 'long_decimal':
            df.at[i, 'value'] = '3.1415926535897932384' 

    #duplicate some rows to test DB deduplicat
    dup_count = int(num_rows * 0.05) # duplicate 5%
    df = pd.concat([df, df.sample(dup_count)]) 
    # df = df.drop_duplicates()

    df.to_csv(filename, index=False)
    print(f"Done! Generated {filename} with {len(df)} total rows (includes duplicates & bad data).")

if __name__ == "__main__":
    generate_mock_data("data/file-chaos.csv", 10000)
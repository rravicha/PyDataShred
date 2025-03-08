from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime
import random
import json
import os

# Define the directory to store the output file
OUTPUT_DIR = "/tmp/weather_data"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the start date
start_date = datetime.datetime(2023, 11, 3)

# Create the DAG
dag = DAG(
    'weather_data_pipeline',
    schedule=datetime.timedelta(days=1),
    start_date=start_date,
    catchup=False,  # Avoid backfilling for this example
)

def extract_weather_data():
    """Simulates fetching weather data from an API."""
    city = "ExampleCity"
    temperature = random.randint(10, 35)  # Random temperature between 10 and 35
    humidity = random.randint(30, 90)     # Random humidity between 30 and 90
    weather_data = {
        "city": city,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.datetime.now().isoformat()
    }
    return weather_data

def load_weather_data(ti):
    """Loads weather data into a local file."""
    weather_data = ti.xcom_pull(task_ids='extract_data_task', dag_id='weather_data_pipeline')
    if weather_data:
        filename = os.path.join(OUTPUT_DIR, f"weather_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(filename, 'w') as f:
            json.dump(weather_data, f, indent=4)
        print(f"Weather data written to {filename}")
    else:
        print("No weather data found.")

# Define the tasks
extract_data_task = PythonOperator(
    task_id='extract_data_task',
    python_callable=extract_weather_data,
    dag=dag,
    do_xcom_push=True,  # Push the weather data to XCom
)

load_data_task = PythonOperator(
    task_id='load_data_task',
    python_callable=load_weather_data,
    dag=dag,
)

# Set task dependencies
extract_data_task >> load_data_task
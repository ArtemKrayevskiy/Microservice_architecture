from celery_app import celery_app
import joblib
import re
from datetime import datetime, timezone
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-token")
influx_org = os.getenv("INFLUXDB_ORG", "my-org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "logs")
ALERTS_DIR = os.getenv("ALERTS_DIR", "/app/error_reports")

os.makedirs(ALERTS_DIR, exist_ok=True)

def create_alert(alert_type: str, description: str):
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{alert_type}_{timestamp}.txt"
        filepath = os.path.join(ALERTS_DIR, filename)
        with open(filepath, "w") as f:
            f.write(f"Time: {timestamp}\nType: {alert_type}\nDescription: {description}\n")
    except Exception as e:
        print(f"Alert creation failed: {e}")


@celery_app.task(name="process_text_task")
def process_text_task(input_text: str):
    if not isinstance(input_text, str):
        create_alert("invalid_input_type", "Incorrect input type")
        return {"error": "Invalid input type"}

    if not input_text.strip():
        create_alert("invalid_input", "Empty input received.")
        return {"error": "Empty input"}

    if re.search(r"\b(?:\d{3}[-.\s]?){2}\d{4}\b", input_text):
        create_alert("personal_data", f"Phone number in: '{input_text}'")
        return {"error": "Phone number provided"}

    if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", input_text):
        create_alert("personal_data", f"Email in: '{input_text}'")
        return {"error": "Email provided"}

    if re.search(r"\b(?:\d[ -]*?){13,16}\b", input_text):
        create_alert("fraud_attempt", f"Credit card in: '{input_text}'")
        return {"error": "Credit card info provided"}

    input_vectorized = vectorizer.transform([input_text])
    prediction = model.predict(input_vectorized)[0]
    result = "Spam" if prediction == 1 else "Not Spam"

    with InfluxDBClient(url=influx_url, token=influx_token, org=influx_org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("interaction")
            .tag("service", "worker")
            .tag("result", result)
            .field("input_text", input_text[:100])
            .time(time.time_ns())
        )
        write_api.write(bucket=influx_bucket, org=influx_org, record=point)
    
    return {"result": result}

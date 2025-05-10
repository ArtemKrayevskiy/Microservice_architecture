from fastapi import FastAPI, HTTPException
import time
from typing import Optional
import joblib
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from task import process_text_task

app = FastAPI()

model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")



influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
influx_token = os.getenv("INFLUXDB_TOKEN", "my-super-token")
influx_org = os.getenv("INFLUXDB_ORG", "my-org")
influx_bucket = os.getenv("INFLUXDB_BUCKET", "logs")

with InfluxDBClient(url=influx_url, token=influx_token, org=influx_org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

ALERTS_DIR = os.getenv("ALERTS_DIR", "/data/error_reports")

os.makedirs(ALERTS_DIR, exist_ok=True)

def log_event(endpoint: str, status: str, message: str = ""):
    point = (
        Point("interaction")
        .tag("service", "web")
        .tag("endpoint", endpoint)
        .tag("status", status)
        .field("message", message[:100])
        .time(time.time_ns())
    )
    write_api.write(bucket=influx_bucket, org=influx_org, record=point)

def create_alert(alert_type: str, description: str):
    try:
        os.makedirs(ALERTS_DIR, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{alert_type}_{timestamp}.txt"
        filepath = os.path.join(ALERTS_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(f"Time: {timestamp}\n")
            f.write(f"Type: {alert_type}\n")
            f.write(f"Description: {description}\n")
        
        return True
    except Exception as e:
        print(f"Error creating alert: {str(e)}", flush=True)
        print(f"Attempted to write to: {ALERTS_DIR}", flush=True)
        return False


@app.get("/")
def read_root():
    log_event(endpoint="/", status="success", message="Root accessed")
    return {"description": "Business Logic Service - handles data processing tasks"}

@app.get("/health")
def health_check():
    log_event(endpoint="/health", status="success", message="Health check OK")
    return {"status": "ok"}

@app.post("/process")
async def process_data(data: dict):
    input_text = data.get("input", "")
    task = process_text_task.delay(input_text)
    return {
        "message": "Task submitted",
        "task_id": task.id
    }
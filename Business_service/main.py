from fastapi import FastAPI
import time
from typing import Optional
import joblib

app = FastAPI()

model = joblib.load("spam_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")


@app.get("/")
def read_root():
    return {"description": "Business Logic Service - handles data processing tasks"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/process")
async def process_data(data: dict):
    time.sleep(3)
    
    input_text = data.get("input", "")
    input_vectorized = vectorizer.transform([input_text])
    
    prediction = model.predict(input_vectorized)[0]
    result = "Spam" if prediction == 1 else "Not Spam"

    return {
        "original": data,
        "processed": True,
        "result": result
    }
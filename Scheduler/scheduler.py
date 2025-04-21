from fastapi import FastAPI
import requests
import os
import asyncio
import random
from contextlib import asynccontextmanager

TARGET_URL = os.getenv("TARGET_URL", "http://web:8000/process")

sample_texts = [
    "Congratulations! You have won a free iPhone!",
    "Hi, are we still on for coffee later?",
    "URGENT! Your account has been compromised.",
    "Reminder: Your appointment is scheduled for tomorrow.",
    "You have been selected for a $1000 gift card.",
    "Hey! Just checking in on the project deadline.",
    "Act now to claim your free reward.",
    "Hello, can we reschedule our meeting?",
    "Earn money from home with this simple trick!",
    "Looking forward to our catch-up call later!"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def task():
        while True:
            try:
                text = random.choice(sample_texts)
                print(f"[Scheduler] Sending: {text}", flush=True)
                response = requests.post(
                    TARGET_URL,
                    json={"input": text}
                )
                print("[Scheduler] Response:", response.json(), flush=True)
            except Exception as e:
                print("[Scheduler] Error:", e)
            await asyncio.sleep(10)

    asyncio.create_task(task()) 
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def root():
    return {"status": "scheduler running"}

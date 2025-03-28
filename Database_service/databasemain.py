from fastapi import FastAPI
from typing import Dict, Any
from pydantic import BaseModel

app = FastAPI()

db_store: Dict[int, Any] = {}

class WriteRequest(BaseModel):
    data: dict

@app.get("/")
def read_root():
    return {"description": "Database Service - handles data storage and retrieval"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/write")
def write_data(request: WriteRequest):
    key = (len(db_store) + 1)
    db_store[key] = request.data
    return {"status": "success", "key": key}

@app.get("/read")
def read_data(key: int):
    if key not in db_store:
        return {"status": "error", "message": "Key not found"}
    return {"status": "success", "data": db_store[key]}
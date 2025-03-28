from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import requests
import os

app = FastAPI()

BUSINESS_LOGIC_URL = "http://localhost:8000"  
DATABASE_URL = "http://localhost:8001"              
APP_TOKEN = os.getenv("APP_TOKEN", "YourSuperSecretToken")  

class TextRequest(BaseModel):
    text: str

class ClassificationResult(BaseModel):
    original_text: str
    result: str
    processed: bool

def verify_token(authorization: str = Header(None)):
    if authorization != f"Bearer {APP_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
def read_root():
    return {"description": "Client Service - Orchestrates calls to Database and Business Logic services"}

@app.get("/health")
def health_check():
    try:
        db_health = requests.get(f"{DATABASE_URL}/health").json()
        bl_health = requests.get(f"{BUSINESS_LOGIC_URL}/health").json()
        
        return {
            "status": "ok",
            "dependencies": {
                "database": db_health,
                "business_logic": bl_health
            }
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "partial",
            "error": str(e),
            "message": "One or more dependencies unavailable"
        }

@app.post("/classify")
async def classify_text(request: TextRequest,authorization: str = Header(None)) -> ClassificationResult:
    
    verify_token(authorization)

    try:
        process_response = requests.post(
            f"{BUSINESS_LOGIC_URL}/process",
            json={"input": request.text},
        )
        process_response.raise_for_status()
        classification = process_response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Business Logic Service unavailable: {str(e)}"
        )

    requests.post(
        f"{DATABASE_URL}/write",
        json={"data": classification}
    )

    return ClassificationResult(
        original_text=request.text,
        result=classification.get("result", "Unknown"),
        processed=True
    )

@app.get("/results/{key}")
async def get_results(key: int,authorization: str = Header(None)):
    verify_token(authorization)
    try:
        response = requests.get(f"{DATABASE_URL}/read?key={key}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=404,
            detail=f"Data not found or service unavailable: {str(e)}"
        )
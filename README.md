# README: FastAPI Microservices for Text Classification

## Overview
This project consists of three FastAPI-based microservices:
1. **Client Service**: Orchestrates requests between the user, Business Logic Service, and Database Service.
2. **Business Logic Service**: Processes text data using a pre-trained model to classify it as spam or not spam.
3. **Database Service**: Stores and retrieves classification results.

## How to Run the Services
### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn
- Requests
- Joblib (for loading the trained model)
- A trained model file (`spam_model.pkl`) and vectorizer (`vectorizer.pkl`)

### Start All Services
1. **Start the Business Logic Service** (port `8000`):
   ```bash
   uvicorn Business_service.main:app --port 8000
   ```
2. **Start the Database Service** (port `8001`):
   ```bash
   uvicorn Database_service.databasemain:app --port 8001
   ```
3. **Start the Client Service** (port `8002`):
   ```bash
   uvicorn Client_service.clienmain:app --port 8002
   ```

## Token-Based Authentication (Client Service)
- The **Client Service** requires authentication for requests to `/classify` and `/results/{key}`.
- Authentication uses a **Bearer Token**, which is checked in the `Authorization` header.
- The expected token is stored in the environment variable `APP_TOKEN`.
- If the provided token is incorrect or missing, the request is rejected with `401 Unauthorized`.

### Example Request with Token
```bash
curl -X POST "http://localhost:8002/classify" \
     -H "Authorization: Bearer YourSuperSecretToken" \
     -H "Content-Type: application/json" \
     -d '{"text": "Free money!!! Click here now!"}'
```

## Request Flow
1. **Client sends a request** to classify text (`/classify`).
2. **Client Service validates the token** and forwards the request to the Business Logic Service (`/process`).
3. **Business Logic Service processes the request** using the spam classifier and returns the result.
4. **Client Service forwards the result** to the Database Service (`/write`) for storage.
5. **Client Service returns the classification result** to the client.
6. **Client retrieves past results** using `/results/{key}` which fetches data from the Database Service (`/read`).

## Endpoints Summary
### Business Logic Service (Port `8000`)
- `GET /health` → Check service health
- `POST /process` → Process text classification

### Database Service (Port `8001`)
- `GET /health` → Check service health
- `POST /write` → Store classification results
- `GET /read?key={key}` → Retrieve stored results

### Client Service (Port `8002`)
- `GET /health` → Check service health
- `POST /classify` → Classify text (requires token)
- `GET /results/{key}` → Fetch classification result (requires token)

## Example of usage 

<img width="647" alt="Знімок екрана 2025-03-28 о 13 30 40" src="https://github.com/user-attachments/assets/ca613765-1990-4562-866a-565dea948956" />

Here we see that we post to classify endpoint text, this returns us the result that given text is spam, now we would like to see if this was saved to our database:

<img width="603" alt="Знімок екрана 2025-03-28 о 13 32 52" src="https://github.com/user-attachments/assets/6d4c2d66-2461-4c61-852b-b76447210ba2" />

We see that exactly the same was saved into our database.

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
   uvicorn business_logic:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Start the Database Service** (port `8001`):
   ```bash
   uvicorn database:app --host 0.0.0.0 --port 8001 --reload
   ```
3. **Start the Client Service** (port `8002`):
   ```bash
   uvicorn client:app --host 0.0.0.0 --port 8002 --reload
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

# Multi-container setup with podman

I have decided to containerize the business logic and add scheduler. 

In order to start everything you jsut simply have to run the following command(make sure that you don't have the containers running)

```bash
podman-compose up --build
```

This will start the apps and in the terminal after 10 seconds you will see something like this:

<img width="546" alt="Знімок екрана 2025-04-21 о 13 50 05" src="https://github.com/user-attachments/assets/2f33986f-c815-4e22-bd95-64fea20eb480" />


We can see that each 10 seconds scheduelr sends one of the random phrases to our business_logic service and gets a response

# Logging/Alerting and Celery

## Data Components

### Redis

   Role: Celery message broker/backend
   Port: 6379
   Handles: All task queueing between Web ↔ Worker
### InfluxDB

   Port: 8086
   Data:
   interaction measurements:
   Web access logs (sync)
   Processing results (async)
   Tags: service, endpoint, status, result



# Logging/Alerting and Celery

## Data Components

### Redis

   - Role: Celery message broker/backend
   - Port: 6379
   - Handles: All task queueing between Web ↔ Worker
### InfluxDB

   - Port: 8086
   - Data:
   - Web access logs (sync)
   - Processing results (async)

## Alert Generation

### Trigger Conditions:
- Invalid input types (sync validation)
- Personal data detection (async)
- Fraud patterns (async)
### Mechanism:
- Files written to mounted volume (./error_reports)
- Format: [type]_[timestamp].txt
- Contents: Timestamp, alert type, description

## Celery Worker - Asynchronous

### Queue: processing
### Concurrency: 2 workers
### Tasks:
- process_text_task:
   - Spam classification
   - Personal data detection
   - Alert generation
   - Result logging to InfluxDB

On the diagram below you can see the general architecrure of the app:

<img src="https://github.com/user-attachments/assets/7d61f94b-8a92-441d-93c4-46603e1f9ee0" width="50%" />


# Task 4: Resource Scaling Estimation

## 10 Simultaneous Connections
- At this scale, the current configuration is sufficient:
- Web Service can handle these with its default worker setup.
- Celery Worker with 2 concurrent workers can process tasks in the background without noticeable delay.
- Redis and InfluxDB usage remains minimal.

## 50 Simultaneous Connections
- Web Service should be scaled to 2–4 worker processes to handle incoming HTTP requests without latency.
- Celery Worker concurrency should be increased to 4–6 workers to keep up with background tasks.
- Redis may require tuning to handle increased message throughput.
- InfluxDB write load increases, but remains manageable.

## 100 and more simultaneous Connections
- Web Service should scale horizontally (for example, these might be some orchestration tools like Kubernetes) to multiple instances behind a load balancer.
- Celery Workers need to scale vertically (higher concurrency) or horizontally (more containers).
- Redis should be monitored for memory and connection limits.
- InfluxDB might be changed to some more powerful DB.

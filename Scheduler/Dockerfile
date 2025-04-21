FROM python:3.10-slim

WORKDIR /app

COPY ./scheduler.py .

RUN pip install fastapi uvicorn requests

CMD ["uvicorn", "scheduler:app", "--host", "0.0.0.0", "--port", "8001"]

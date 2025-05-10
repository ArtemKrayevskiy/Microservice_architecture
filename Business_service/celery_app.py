from celery import Celery
import os

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_BACKEND_URL", "redis://redis:6379/1"),
    include=["task"]
)

celery_app.conf.task_routes = {
    "process_text_task": {"queue": "processing"},
}

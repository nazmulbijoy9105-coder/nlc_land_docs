from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "nlc_land",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_expires=86400,
    timezone="Asia/Dhaka",
    task_track_started=True,
)

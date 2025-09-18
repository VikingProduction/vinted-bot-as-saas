from celery import Celery
from ..config import get_settings

settings = get_settings()
celery_app = Celery(
    "vinted_bot",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.beat_schedule = {
    "run-scraping-every-minute": {
        "task": "backend.app.tasks.scraping_task.run_all_filters",
        "schedule": 60.0,
    }
}

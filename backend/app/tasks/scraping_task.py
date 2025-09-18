from .celery_app import celery_app
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..scraping.vinted_client import check_filters_and_notify

@celery_app.task(name="backend.app.tasks.scraping_task.run_all_filters", ignore_result=True)
def run_all_filters():
    db: Session = SessionLocal()
    try:
        # récupère les filtres actifs (à créer dans ta table filters) et lance les checks
        check_filters_and_notify(db)
    finally:
        db.close()

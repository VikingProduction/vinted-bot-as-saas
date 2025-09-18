"""
Application Celery pour les tâches asynchrones
"""
from celery import Celery
from celery.schedules import crontab
import os

from ..config import settings, logger

# Configuration Celery avec Redis
celery_app = Celery(
    "vinted_bot_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        'app.tasks.scraping_tasks',
        'app.tasks.notification_tasks',
        'app.tasks.maintenance_tasks'
    ]
)

# Configuration Celery
celery_app.conf.update(
    # Timezone
    timezone='Europe/Paris',
    enable_utc=True,
    
    # Résultats
    result_expires=3600,  # 1 heure
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Sérialisation
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Routing
    task_routes={
        'app.tasks.scraping_tasks.*': {'queue': 'scraping'},
        'app.tasks.notification_tasks.*': {'queue': 'notifications'},
        'app.tasks.maintenance_tasks.*': {'queue': 'maintenance'},
    },
    
    # Workers
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Rate limiting
    task_annotations={
        'app.tasks.scraping_tasks.scrape_vinted_filters': {
            'rate_limit': '10/m'  # 10 tâches par minute max
        },
        'app.tasks.notification_tasks.send_email_alert': {
            'rate_limit': '100/m'  # 100 emails par minute max
        }
    }
)

# Tâches périodiques (Celery Beat)
celery_app.conf.beat_schedule = {
    # Scraping des filtres actifs toutes les 5 minutes
    'scrape-active-filters': {
        'task': 'app.tasks.scraping_tasks.scrape_all_active_filters',
        'schedule': crontab(minute='*/5'),  # Toutes les 5 minutes
        'options': {'queue': 'scraping'}
    },
    
    # Nettoyage des anciennes alertes tous les jours à 2h
    'cleanup-old-alerts': {
        'task': 'app.tasks.maintenance_tasks.cleanup_old_alerts',
        'schedule': crontab(hour=2, minute=0),  # 2h00 chaque jour
        'options': {'queue': 'maintenance'}
    },
    
    # Statistiques quotidiennes à 1h
    'daily-stats': {
        'task': 'app.tasks.maintenance_tasks.generate_daily_stats',
        'schedule': crontab(hour=1, minute=0),  # 1h00 chaque jour
        'options': {'queue': 'maintenance'}
    },
    
    # Vérification santé proxies toutes les heures
    'check-proxy-health': {
        'task': 'app.tasks.maintenance_tasks.check_proxy_health',
        'schedule': crontab(minute=0),  # Toutes les heures
        'options': {'queue': 'maintenance'}
    },
    
    # Sync abonnements Stripe toutes les 30 minutes
    'sync-stripe-subscriptions': {
        'task': 'app.tasks.maintenance_tasks.sync_stripe_subscriptions',
        'schedule': crontab(minute='*/30'),  # Toutes les 30 minutes
        'options': {'queue': 'maintenance'}
    }
}

# Logging Celery
@celery_app.task(bind=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    logger.info(f'Request: {self.request!r}')

# Hooks pour logging
@celery_app.task(bind=True)
def log_task_start(self, task_name: str, **kwargs):
    """Log le démarrage d'une tâche"""
    logger.info(
        "🚀 Tâche démarrée",
        task_id=self.request.id,
        task_name=task_name,
        kwargs=kwargs
    )

@celery_app.task(bind=True)
def log_task_success(self, task_name: str, result=None):
    """Log le succès d'une tâche"""
    logger.info(
        "✅ Tâche terminée avec succès",
        task_id=self.request.id,
        task_name=task_name,
        result=result
    )

@celery_app.task(bind=True)
def log_task_failure(self, task_name: str, exc, traceback):
    """Log l'échec d'une tâche"""
    logger.error(
        "❌ Tâche échouée",
        task_id=self.request.id,
        task_name=task_name,
        error=str(exc),
        traceback=traceback
    )

# Handlers d'événements Celery
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def robust_task(self, *args, **kwargs):
    """Template pour tâche robuste avec retry automatique"""
    try:
        # Votre logique ici
        pass
    except Exception as exc:
        logger.warning(
            f"⚠️ Tentative {self.request.retries + 1}/3 échouée",
            task_id=self.request.id,
            error=str(exc)
        )
        raise self.retry(exc=exc, countdown=60)

if __name__ == '__main__':
    celery_app.start()

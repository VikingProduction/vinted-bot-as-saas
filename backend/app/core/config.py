import os
import structlog
from functools import lru_cache

# Configuration du logger
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("vinted_bot")

class Settings:
    database_url: str = os.getenv("DATABASE_URL", "mysql://vinted_user:pass@localhost:3306/vinted_bot")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0") 
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_me")
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = ENVIRONMENT == "development"

    SMARTPROXY_USERNAME: str = os.getenv("SMARTPROXY_USERNAME", "")
    SMARTPROXY_PASSWORD: str = os.getenv("SMARTPROXY_PASSWORD", "")
    
    # Ajout des attributs manquants pour scraping
    scraping_delay_min: float = 2.0
    scraping_delay_max: float = 5.0
    snipping_enabled: bool = True

    # quotas par plan
    PLAN_LIMITS = {
        "free": {"filters": 1, "checks_per_min": 1},
        "basic": {"filters": 5, "checks_per_min": 2},
        "pro": {"filters": 20, "checks_per_min": 5},
        "elite": {"filters": 100, "checks_per_min": 10},
    }

@lru_cache
def get_settings() -> Settings:
    return Settings()

# Instance globale pour compatibilité
settings = get_settings()

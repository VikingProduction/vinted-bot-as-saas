import os
from functools import lru_cache

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql://vinted_user:pass@localhost:3306/vinted_bot")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_me")
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    SMARTPROXY_USERNAME: str = os.getenv("SMARTPROXY_USERNAME", "")
    SMARTPROXY_PASSWORD: str = os.getenv("SMARTPROXY_PASSWORD", "")

    # quotas par plan (exemple)
    PLAN_LIMITS = {
        "free": {"filters": 1, "checks_per_min": 1},
        "basic": {"filters": 5, "checks_per_min": 2},
        "pro": {"filters": 20, "checks_per_min": 5},
        "elite": {"filters": 100, "checks_per_min": 10},
    }

@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
Configuration principale de l'application FastAPI
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Vinted Bot SAAS"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Base de données
    database_url: str
    redis_url: str
    redis_password: str = ""
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # SmartProxy
    smartproxy_username: str
    smartproxy_password: str
    smartproxy_endpoint: str = "gate.smartproxy.com:7000"
    
    # Stripe
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str
    stripe_plan_starter: str = ""
    stripe_plan_pro: str = ""
    stripe_plan_business: str = ""
    
    # Email
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""
    sendgrid_from_name: str = "Vinted Bot SAAS"
    email_enabled: bool = True
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    # Scraping
    scraping_delay_min: int = 2
    scraping_delay_max: int = 5
    max_concurrent_scrapers: int = 10
    retry_attempts: int = 3
    
    # Features
    snipping_enabled: bool = True
    analytics_enabled: bool = True
    api_access_enabled: bool = True
    
    # Security
    bcrypt_rounds: int = 12
    session_timeout_hours: int = 24
    
    # Monitoring
    sentry_dsn: str = ""
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instance globale des settings
settings = Settings()

# Configuration des logs
import logging
import structlog

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=getattr(logging, settings.log_level.upper()),
)

# Configuration structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configuration Sentry (optionnel)
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.environment,
    )
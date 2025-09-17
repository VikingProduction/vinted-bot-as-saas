"""
Application FastAPI principale
"""
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time

from .config import settings, logger
from .database import engine, Base
from .auth.jwt_handler import JWTBearer
from .routers import auth, users, filters, alerts, subscriptions
from .scraping.engine import ScrapingEngine
from .tasks.celery_app import celery_app

# Création des tables
Base.metadata.create_all(bind=engine)

# Initialisation FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API pour bot Vinted automatisé avec système d'abonnement",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware Trusted Host (sécurité)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Middleware pour logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "Request processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )
    
    return response

# Inclusion des routers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"],
    dependencies=[Depends(JWTBearer())]
)

app.include_router(
    filters.router,
    prefix="/api/filters",
    tags=["Filters"],
    dependencies=[Depends(JWTBearer())]
)

app.include_router(
    alerts.router,
    prefix="/api/alerts",
    tags=["Alerts"],
    dependencies=[Depends(JWTBearer())]
)

app.include_router(
    subscriptions.router,
    prefix="/api/subscriptions",
    tags=["Subscriptions"]
)

# Instance du moteur de scraping
scraping_engine = None

@app.on_event("startup")
async def startup_event():
    """Démarrage des services en arrière-plan"""
    global scraping_engine
    
    logger.info("🚀 Démarrage de l'application Vinted Bot SAAS")
    
    # Initialisation du moteur de scraping
    scraping_engine = ScrapingEngine()
    await scraping_engine.start()
    
    # Test de la base de données
    try:
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Connexion base de données OK")
    except Exception as e:
        logger.error("❌ Erreur connexion base de données", error=str(e))
    
    # Test Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        logger.info("✅ Connexion Redis OK")
    except Exception as e:
        logger.error("❌ Erreur connexion Redis", error=str(e))
    
    logger.info("🎯 Application prête à recevoir des requêtes")

@app.on_event("shutdown")
async def shutdown_event():
    """Arrêt propre des services"""
    global scraping_engine
    
    logger.info("🛑 Arrêt de l'application...")
    
    if scraping_engine:
        await scraping_engine.stop()
    
    logger.info("✅ Arrêt terminé")

# Routes principales
@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": f"Bienvenue sur {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "Documentation disponible en mode debug"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    global scraping_engine
    
    # Vérification base de données
    db_status = "ok"
    try:
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Vérification Redis
    redis_status = "ok"
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    # Vérification moteur de scraping
    scraping_status = "running" if scraping_engine and scraping_engine.is_running() else "stopped"
    
    # Vérification Celery
    celery_status = "ok"
    try:
        inspect = celery_app.control.inspect()
        if not inspect.active():
            celery_status = "no workers"
    except Exception as e:
        celery_status = f"error: {str(e)}"
    
    health_data = {
        "status": "healthy" if all([
            db_status == "ok",
            redis_status == "ok",
            scraping_status == "running"
        ]) else "unhealthy",
        "timestamp": time.time(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "scraping_engine": scraping_status,
            "celery": celery_status
        },
        "version": settings.app_version
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JSONResponse(content=health_data, status_code=status_code)

@app.get("/stats")
async def get_stats(token: str = Depends(JWTBearer())):
    """Statistiques générales de l'application (admin seulement)"""
    # TODO: Vérifier si l'utilisateur est admin
    
    from .database import SessionLocal
    from .models.user import User
    from .models.filter import VintedFilter
    from .models.alert import Alert
    
    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        filters_count = db.query(VintedFilter).count()
        alerts_count = db.query(Alert).count()
        
        return {
            "users": users_count,
            "filters": filters_count,
            "alerts": alerts_count,
            "scraping_engine_status": scraping_engine.is_running() if scraping_engine else False
        }
    finally:
        db.close()

# Gestion des erreurs globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(
        "HTTP Exception",
        url=str(request.url),
        method=request.method,
        status_code=exc.status_code,
        detail=exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled Exception",
        url=str(request.url),
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur", "error": True}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
# backend/app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import time
import os

from .monitoring.health import router as health_router
from .auth.controllers import router as auth_router
from .billing.controllers import router as billing_router
from .routers.api import router as api_router
from .monitoring.metrics import metrics_app

# Env/Settings simples (pas de dépendance externe)
ENV = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
]
TRUSTED_HOSTS = [
    h.strip() for h in os.getenv("TRUSTED_HOSTS", "*").split(",")
]

app = FastAPI(
    title="Vinted Bot SaaS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1024)

# CORS piloté par env (par défaut permissif comme chez toi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts (en prod: mets ton domaine, ex: "vintedbot.example.com")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=TRUSTED_HOSTS if TRUSTED_HOSTS != ["*"] else ["*"],
)

# Sécurité basique: quelques headers par défaut
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    # CSP light en exemple; adapte selon ton frontend
    # response.headers.setdefault("Content-Security-Policy", "default-src 'self'; img-src * data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
    return response

# Access log minimal avec temps de réponse (utile en prod natif)
@app.middleware("http")
async def access_log(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        dur_ms = (time.perf_counter() - start) * 1000
        # remplace par un logger structuré si tu veux
        path = request.url.path
        method = request.method
        status = getattr(locals().get('response', None), "status_code", 500)
        print(f"{method} {path} -> {status} in {dur_ms:.1f}ms")

# Handlers erreurs propres
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail},
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": True, "detail": exc.errors()},
    )

# Routes existantes
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(billing_router, prefix="/api", tags=["billing"])
app.include_router(api_router, prefix="/api", tags=["api"])

# Metrics Prometheus
app.mount("/metrics", metrics_app)

# Redirect racine vers /docs (pratique en dev)
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Événements lifecycle (log simple)
@app.on_event("startup")
async def on_startup():
    print(f"[startup] ENV={ENV} CORS_ALLOW_ORIGINS={ALLOWED_ORIGINS} TRUSTED_HOSTS={TRUSTED_HOSTS}")

@app.on_event("shutdown")
async def on_shutdown():
    print("[shutdown] bye")

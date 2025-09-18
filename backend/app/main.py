from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .monitoring.health import router as health_router
from .auth.controllers import router as auth_router
from .billing.controllers import router as billing_router
from .routers.api import router as api_router
from .monitoring.metrics import metrics_app

app = FastAPI(title="Vinted Bot SaaS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(billing_router, prefix="/api", tags=["billing"])
app.include_router(api_router, prefix="/api", tags=["api"])

# exposer /metrics pour Prometheus
app.mount("/metrics", metrics_app)

"""FlakyGuard-AI Core FastAPI Application."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from prometheus_client import make_asgi_app

from app.config import settings
from app.api.health import router as health_router
from app.api.rag import router as rag_router
from app.api.incidents import router as incidents_router
from app.api.alerts import router as alerts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Developer Tools & AI-DevOps Platform for Flaky Test Remediation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(rag_router)
app.include_router(incidents_router)
app.include_router(alerts_router)

# Mount Prometheus metrics endpoint
if settings.PROMETHEUS_METRICS_ENABLED:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Mount static files for FlakyGuard Web Console
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "FlakyGuard Web Console static files not found"}

    @app.get("/presentation", include_in_schema=False)
    async def serve_presentation():
        pres_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "presentation", "slides.html")
        if os.path.exists(pres_path):
            return FileResponse(pres_path)
        return {"message": "Presentation slides not found"}
else:
    @app.get("/", include_in_schema=False)
    async def serve_root():
        return {
            "app": settings.APP_NAME,
            "status": "online",
            "docs_url": "/docs",
            "health_url": "/health",
        }

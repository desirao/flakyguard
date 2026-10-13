"""Health check and diagnostic endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Basic health check endpoint for container probes and load balancers."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/v1/health")
def get_detailed_health():
    """Detailed diagnostic endpoint checking configuration and subsystem status."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "features": {
            "sourcegraph_enabled": bool(settings.SOURCEGRAPH_URL),
            "sourcegraph_fallback_git": settings.SOURCEGRAPH_FALLBACK_GIT,
            "metrics_enabled": settings.PROMETHEUS_METRICS_ENABLED,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

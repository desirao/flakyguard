"""Test health check and metrics endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_basic_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "FlakyGuard-AI"
    assert "timestamp" in data


def test_detailed_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "features" in data
    assert "sourcegraph_enabled" in data["features"]


def test_metrics_endpoint_mounted():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "python_gc_objects_collected_total" in response.text or "process_cpu_seconds_total" in response.text or "# HELP" in response.text


def test_serve_console_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "FlakyGuard" in response.text
    assert "WCAG" in response.text or "skip-link" in response.text

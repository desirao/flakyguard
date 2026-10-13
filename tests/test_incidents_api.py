"""Unit tests for FastAPI Incident and Alert API endpoints."""

import json
from fastapi.testclient import TestClient
from app.main import app
from security.hmac_auth import generate_hmac_signature, DEFAULT_SECRET

client = TestClient(app)


def test_investigate_incident_endpoint():
    payload = {
        "incident_id": "INC-API-001",
        "repo": "desirao/flakyguard",
        "commit_sha": "c8f2a17",
        "log_text": "FAILED tests/test_payment.py::test_charge_card\nAttributeError: 'NoneType' object has no attribute 'customer_id'",
    }
    response = client.post("/api/v1/incidents/investigate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "INC-API-001"
    assert data["status"] == "awaiting_approval"
    assert data["category"] == "sre"


def test_investigate_incident_with_valid_hmac():
    payload = {
        "incident_id": "INC-API-002",
        "repo": "desirao/flakyguard",
        "commit_sha": "c8f2a17",
        "log_text": "AttributeError in checkout",
    }
    raw_bytes = json.dumps(payload).encode("utf-8")
    sig = generate_hmac_signature(raw_bytes, DEFAULT_SECRET)

    response = client.post(
        "/api/v1/incidents/investigate",
        data=raw_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert response.status_code == 200


def test_investigate_incident_with_invalid_hmac_fails():
    payload = {"incident_id": "INC-FAKE"}
    raw_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/api/v1/incidents/investigate",
        data=raw_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": "sha256=invalid"},
    )
    assert response.status_code == 401


def test_get_incident_and_approval_workflow():
    # First create
    create_payload = {
        "incident_id": "INC-API-APPROVAL",
        "repo": "desirao/flakyguard",
        "commit_sha": "c8f2a17",
        "log_text": "TimeoutError in lock",
    }
    client.post("/api/v1/incidents/investigate", json=create_payload)

    # Get incident
    get_res = client.get("/api/v1/incidents/INC-API-APPROVAL")
    assert get_res.status_code == 200
    assert get_res.json()["incident_id"] == "INC-API-APPROVAL"

    # Approve
    approve_res = client.post(
        "/api/v1/approvals/INC-API-APPROVAL",
        json={"action": "approve", "reviewer_notes": "Looks solid"},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"
    assert approve_res.json()["pr_url"] is not None


def test_get_nonexistent_incident_returns_404():
    res = client.get("/api/v1/incidents/INC-DOES-NOT-EXIST")
    assert res.status_code == 404


def test_ingest_prometheus_alert():
    alert_payload = {
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "FlakyTestDetected",
                    "repo": "desirao/flakyguard",
                    "commit_sha": "c8f2a17",
                },
                "annotations": {
                    "summary": "High rate of test flakiness in CI",
                },
            }
        ],
    }
    res = client.post("/api/v1/alerts/prometheus", json=alert_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ingested"
    assert "incident_id" in data

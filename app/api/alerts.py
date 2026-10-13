"""Prometheus Alertmanager Webhook Ingestion Endpoint."""

from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel

from agents.workflow import run_incident_workflow

router = APIRouter(prefix="/api/v1", tags=["Prometheus Alerts"])


class PrometheusAlert(BaseModel):
    status: str
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}


class PrometheusWebhookPayload(BaseModel):
    version: str = "4"
    groupKey: str = ""
    status: str
    receiver: str = "flakyguard-webhook"
    alerts: List[PrometheusAlert] = []


@router.post("/alerts/prometheus")
def ingest_prometheus_alert(payload: PrometheusWebhookPayload):
    """Ingest firing alert from Prometheus and trigger LangGraph incident triage."""
    alert_count = len(payload.alerts)
    if not payload.alerts:
        return {"status": "ignored", "message": "No firing alerts in payload"}

    first_alert = payload.alerts[0]
    alert_name = first_alert.labels.get("alertname", "UnknownAlert")
    summary = first_alert.annotations.get("summary", "Prometheus alert triggered")

    log_text = f"PROMETHEUS ALERT: {alert_name}\nStatus: {first_alert.status}\nSummary: {summary}\nLabels: {first_alert.labels}"

    incident_payload = {
        "source": "prometheus",
        "repo": first_alert.labels.get("repo", "desirao/flakyguard"),
        "commit_sha": first_alert.labels.get("commit_sha", "HEAD"),
        "log_text": log_text,
    }

    final_state = run_incident_workflow(incident_payload)
    return {
        "status": "ingested",
        "incident_id": final_state["incident_id"],
        "category": final_state["category"],
        "state_status": final_state["status"],
    }

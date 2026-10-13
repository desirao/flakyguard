"""Incident Ingestion, Triage, and Human Approval Gate API Endpoints."""

from typing import Any, Dict, Literal, Optional
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from agents.workflow import (
    INCIDENT_STORE,
    apply_approval_decision,
    run_incident_workflow,
)
from security.hmac_auth import verify_hmac_signature

router = APIRouter(prefix="/api/v1", tags=["Incidents & Remediation"])


class IncidentInvestigateRequest(BaseModel):
    incident_id: Optional[str] = Field(None, description="Unique incident identifier")
    source: Literal["github_actions", "prometheus", "manual"] = "github_actions"
    repo: str = Field("desirao/flakyguard", description="Repository name")
    commit_sha: str = Field("c8f2a17", description="Head commit SHA")
    log_text: Optional[str] = Field(None, description="Plaintext CI failure trace")
    log_base64: Optional[str] = Field(None, description="Base64 encoded CI failure log")


class ApprovalRequest(BaseModel):
    action: Literal["approve", "quarantine", "reject"] = Field(
        ..., description="Human reviewer gate decision"
    )
    reviewer_notes: Optional[str] = Field("", description="Optional justification note")


@router.post("/incidents/investigate")
async def investigate_incident(
    request: Request,
    body: IncidentInvestigateRequest,
    x_hub_signature_256: Optional[str] = Header(None),
):
    """Ingest CI failure or alert and trigger LangGraph ReAct investigation."""
    payload_dict = body.model_dump()

    # If signature is present, verify HMAC
    if x_hub_signature_256:
        raw_bytes = await request.body()
        is_valid = verify_hmac_signature(raw_bytes, x_hub_signature_256)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid HMAC-SHA256 signature.")

    # Execute LangGraph Multi-Agent Workflow
    final_state = run_incident_workflow(payload_dict)
    return final_state


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Retrieve full blackboard state of an ongoing or completed incident."""
    state = INCIDENT_STORE.get(incident_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return state


@router.post("/approvals/{incident_id}")
def approve_incident(incident_id: str, body: ApprovalRequest):
    """Human-in-the-loop review gate: Approve PR opening, quarantine test, or reject patch."""
    updated_state = apply_approval_decision(incident_id, body.action)
    if not updated_state:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return updated_state

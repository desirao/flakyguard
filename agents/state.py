"""Blackboard State Schema (IncidentState) for LangGraph Multi-Agent Workflow."""

from typing import Any, Dict, List, Literal, Optional, TypedDict


class CommitAttribution(TypedDict):
    sha: str
    author: str
    files_changed: List[str]
    score: float
    explanation: str


class ReactTraceItem(TypedDict):
    iteration: int
    thought: str
    action: str
    observation: str


class IncidentState(TypedDict):
    incident_id: str
    source: Literal["github_actions", "prometheus", "manual"]
    received_at: str
    raw_payload: Dict[str, Any]
    redacted_log: str
    repo: str
    commit_sha: str
    category: Literal["sre", "security", "cloud_infra", "flaky_test", "unknown"]
    routing_reasoning: str
    flakiness: Dict[str, Any]                 # {is_flaky: bool, pass_rate: float, recommendation: str}
    suspect_commits: List[Dict[str, Any]]     # [{sha, author, files_changed, score, explanation}]
    code_hits: List[Dict[str, Any]]           # Sourcegraph symbol and reference matches
    similar_incidents: List[Dict[str, Any]]   # RAG hits with similarity scores and runbook citations
    react_trace: List[Dict[str, Any]]         # [{iteration, thought, action, observation}]
    root_cause: str
    patch_diff: str
    patch_applies: bool
    pr_url: Optional[str]
    generated_test: str
    test_validation: Dict[str, Any]           # {fails_before: bool, passes_after: bool, runs_stable: bool, coverage_delta: float}
    audit: Dict[str, Any]                     # {confidence: int, hallucination_flags: list, risk_level: str}
    status: Literal["investigating", "awaiting_approval", "approved", "rejected", "failed", "quarantined"]
    timings_ms: Dict[str, float]

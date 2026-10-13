"""Unit tests for Responsible AI Auditor: Factual verification, hallucination checks, and risk scoring."""

from agents.responsible_ai import ResponsibleAIAuditor


def test_audit_valid_real_workspace_artifacts():
    auditor = ResponsibleAIAuditor()
    report = auditor.audit_investigation(
        incident_id="INC-AUDIT-1",
        culprit_file="app/config.py",
        culprit_symbol="Settings",
        suspect_commit_sha="HEAD",
        patch_diff="--- a/app/config.py\n+++ b/app/config.py\n@@ -1,1 +1,1 @@",
        patch_applies=True,
    )
    assert report.is_grounded is True
    assert len(report.hallucination_flags) == 0
    assert report.confidence >= 4
    assert report.risk_level == "LOW"


def test_audit_flags_hallucinated_file_and_symbol():
    auditor = ResponsibleAIAuditor()
    report = auditor.audit_investigation(
        incident_id="INC-AUDIT-2",
        culprit_file="nonexistent/phantom_service.py",
        culprit_symbol="MagicUnicornClass",
        suspect_commit_sha="nonexistent123",
        patch_diff=None,
        patch_applies=False,
    )
    assert report.is_grounded is False
    assert len(report.hallucination_flags) >= 2
    assert any("phantom_service.py" in f for f in report.hallucination_flags)
    assert any("MagicUnicornClass" in f for f in report.hallucination_flags)
    assert report.confidence <= 2
    assert report.risk_level == "HIGH"


def test_audit_flags_failing_patch():
    auditor = ResponsibleAIAuditor()
    report = auditor.audit_investigation(
        incident_id="INC-AUDIT-3",
        culprit_file="app/config.py",
        culprit_symbol="Settings",
        suspect_commit_sha="c8f2a17",
        patch_diff="malformed patch diff",
        patch_applies=False,
    )
    assert any("Patch failed" in f for f in report.hallucination_flags)
    assert report.risk_level in ["MEDIUM", "HIGH"]

# Incident Runbook: INC-103 — Async Lock Contention & Flaky Test Timeout

## Symptom:
Intermittent CI test failures with `TimeoutError: Request timed out after 5000ms waiting for lock` in test fixtures. Passes on re-run with 80% probability.

## Root Cause:
Test executions share asynchronous event loops or database connection pools across parallel pytest workers (`pytest-xdist`). Lock acquisition timeout is too aggressive for heavily loaded CI runners.

## Remediation Steps:
1. Isolate test fixtures with `scope="function"` rather than `scope="module"`.
2. Apply FlakyGuard quarantine tag `@pytest.mark.flaky(reruns=3)` or quarantine into non-blocking suite.
3. Compute commit-level variance using `agents/flakiness.py` to differentiate flaky tests from true regressions.

# Incident Runbook: INC-101 — Socket Timeout in External Service Calls

## Symptom:
CI builds or worker tasks fail with `TimeoutError`, `urllib3.exceptions.ConnectTimeoutError`, or `requests.exceptions.ReadTimeout`.

## Root Cause:
Synchronous network HTTP calls executed without explicit connect and read timeouts hang when the destination endpoint experiences packet loss or gateway latency spikes.

## Remediation Steps:
1. Wrap all client invocations with explicit `timeout=(3.05, 10.0)` tuples.
2. Install a resilient `HTTPAdapter` configured with `urllib3.util.Retry(total=3, backoff_factor=0.5)`.
3. Never use raw `requests.get()` without bounded socket parameters.
4. If testing under mock environments, use `unittest.mock.patch` to avoid real socket calls.

"""Prometheus Metrics Instrumentation for FlakyGuard-AI Platform."""

try:
    from prometheus_client import Counter, Histogram, Gauge
except ImportError:
    # Fallback dummy objects if prometheus_client is not installed
    class DummyMetric:
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def dec(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass

    Counter = Histogram = Gauge = lambda *args, **kwargs: DummyMetric()  # type: ignore


# Prometheus Metric Definitions
INCIDENT_TOTAL = Counter(
    "flakyguard_incidents_total",
    "Total incidents triaged by FlakyGuard-AI",
    ["category", "source"],
)

INCIDENT_INVESTIGATION_SECONDS = Histogram(
    "flakyguard_incident_investigation_seconds",
    "Latency of multi-agent LangGraph incident investigation in seconds",
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

FLAKY_TESTS_TOTAL = Counter(
    "flakyguard_flaky_tests_total",
    "Total tests identified as flaky and recommended for quarantine",
)

PATCH_ATTEMPTS_TOTAL = Counter(
    "flakyguard_patch_attempts_total",
    "Total unified git patches synthesized",
    ["status"],
)

TESTS_GENERATED_TOTAL = Counter(
    "flakyguard_tests_generated_total",
    "Total regression tests synthesized",
    ["gate_status"],
)

APPROVAL_DECISIONS_TOTAL = Counter(
    "flakyguard_approval_decisions_total",
    "Human reviewer gate decisions",
    ["decision"],
)

HALLUCINATION_FLAGS_TOTAL = Counter(
    "flakyguard_hallucination_flags_total",
    "Total hallucinated file paths or symbols caught by Responsible AI audit",
)

ACTIVE_INCIDENTS = Gauge(
    "flakyguard_active_incidents",
    "Current active incidents in the blackboard store",
)


def record_incident_metrics(category: str, source: str, latency_seconds: float, is_flaky: bool = False):
    """Record metrics for an analyzed incident."""
    INCIDENT_TOTAL.labels(category=category, source=source).inc()
    INCIDENT_INVESTIGATION_SECONDS.observe(latency_seconds)
    if is_flaky:
        FLAKY_TESTS_TOTAL.inc()


def record_patch_metrics(applies: bool):
    """Record patch application status."""
    status = "success" if applies else "failed"
    PATCH_ATTEMPTS_TOTAL.labels(status=status).inc()


def record_testgen_metrics(passed_gates: bool):
    """Record test validation gate outcome."""
    status = "passed" if passed_gates else "rejected"
    TESTS_GENERATED_TOTAL.labels(gate_status=status).inc()


def record_approval_metric(decision: str):
    """Record human approval gate decision."""
    APPROVAL_DECISIONS_TOTAL.labels(decision=decision).inc()

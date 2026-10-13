"""Unit tests for Flakiness Analyzer and quarantine recommendation engine."""

from agents.flakiness import FlakinessAnalyzer, TestRunRecord


def test_consistent_passing_test_is_not_flaky():
    analyzer = FlakinessAnalyzer(flaky_threshold=0.2)
    records = [
        TestRunRecord("run-1", "sha123", "passed", 1.2, "2026-10-13T10:00:00Z"),
        TestRunRecord("run-2", "sha123", "passed", 1.1, "2026-10-13T10:05:00Z"),
        TestRunRecord("run-3", "sha123", "passed", 1.3, "2026-10-13T10:10:00Z"),
    ]
    report = analyzer.analyze_test_history("tests/test_api.py::test_ok", records, "sha123")
    assert report.is_flaky is False
    assert report.pass_rate == 1.0
    assert report.recommendation in ["keep_active", "stable"]


def test_intermittent_failures_on_same_commit_triggers_quarantine():
    analyzer = FlakinessAnalyzer(flaky_threshold=0.2)
    records = [
        TestRunRecord("run-1", "sha123", "passed", 1.2, "2026-10-13T10:00:00Z"),
        TestRunRecord("run-2", "sha123", "failed", 5.0, "2026-10-13T10:05:00Z"),
        TestRunRecord("run-3", "sha123", "passed", 1.1, "2026-10-13T10:10:00Z"),
        TestRunRecord("run-4", "sha123", "failed", 4.9, "2026-10-13T10:15:00Z"),
    ]
    report = analyzer.analyze_test_history("tests/test_race.py::test_lock", records, "sha123")
    assert report.is_flaky is True
    assert report.pass_rate == 0.5
    assert report.recommendation == "quarantine"
    assert "inconsistent outcomes" in report.rationale


def test_consistent_failure_recommends_patch():
    analyzer = FlakinessAnalyzer(flaky_threshold=0.2)
    records = [
        TestRunRecord("run-1", "sha123", "failed", 1.2, "2026-10-13T10:00:00Z"),
        TestRunRecord("run-2", "sha123", "failed", 1.1, "2026-10-13T10:05:00Z"),
    ]
    report = analyzer.analyze_test_history("tests/test_bug.py::test_broken", records, "sha123")
    assert report.is_flaky is False
    assert report.pass_rate == 0.0
    assert report.recommendation == "patch"


def test_report_serialization():
    analyzer = FlakinessAnalyzer()
    records = [
        TestRunRecord("run-1", "c8f2a17", "passed", 2.0, "2026-10-13T10:00:00Z"),
        TestRunRecord("run-2", "c8f2a17", "failed", 2.1, "2026-10-13T10:05:00Z"),
    ]
    report = analyzer.analyze_test_history("tests/test_flaky.py::test_net", records, "c8f2a17")
    d = report.to_dict()
    assert d["test_identifier"] == "tests/test_flaky.py::test_net"
    assert "pass_rate" in d
    assert "variance" in d
    assert "recommendation" in d

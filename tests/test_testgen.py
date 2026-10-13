"""Test doc-aware test synthesis and 4-tier validation gates."""

from tools.testgen import TestGenerator, TestValidationReport


def test_synthesize_test_doc_aware():
    gen = TestGenerator()
    test_code = gen.synthesize_test(
        incident_id="INC-102",
        error_trace="AttributeError: 'NoneType' object has no attribute 'customer_id'",
        patch_diff="+ if not cart or not cart.user: raise ValueError('Invalid')",
        target_symbol="process_cart",
        docstring="Process customer cart checkout.",
    )
    assert "def test_regression_inc_102_process_cart():" in test_code
    assert "pytest" in test_code
    assert "cart" in test_code


def test_evaluate_validation_gates_success():
    gen = TestGenerator()
    test_code = (
        "import pytest\n"
        "def test_simple_assertion():\n"
        "    assert 1 + 1 == 2\n"
    )
    report = gen.evaluate_validation_gates(
        test_code=test_code,
        target_symbol="simple_operation",
        unpatched_runner=lambda: False,  # fails before
        patched_runner=lambda: True,     # passes after
    )
    assert isinstance(report, TestValidationReport)
    assert report.fails_before is True
    assert report.passes_after is True
    assert report.runs_stable_10x is True
    assert report.coverage_delta > 0
    assert report.overall_pass is True
    assert "PASSED" in report.to_summary()


def test_evaluate_validation_gates_flaky_failure():
    gen = TestGenerator()
    # Test that fails inside isolation
    failing_test_code = (
        "import pytest\n"
        "def test_failing_case():\n"
        "    assert 1 == 2\n"
    )
    report = gen.evaluate_validation_gates(
        test_code=failing_test_code,
        target_symbol="broken_symbol",
    )
    assert report.passes_after is False
    assert report.overall_pass is False

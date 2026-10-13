# FlakyGuard-AI: Intelligent Test Generation & CodiumAI Benchmark Study

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Module Lead:** Rahul Yadav & Saumil Gupta  
**Document Classification:** A2 Core Deliverable (Criteria C8 & C9)  

---

## 1. Executive Summary & Test Synthesis Paradigm

Automated test generation tools such as **CodiumAI (Qodo Gen)** and **Codeium** attempt to synthesize unit tests from code files. However, most general-purpose assistants generate superficial happy-path tests that do not replicate reported regressions, lack deterministic validation loops, and often introduce new flaky timing issues (e.g. arbitrary `time.sleep()`).

**FlakyGuard-AI** introduces a doc-aware and AST-grounded test generator ([`tools/testgen.py`](file:///c:/Users/hr26r/Downloads/FLAKYGUARD/tools/testgen.py)) governed by **4-Tier Deterministic Validation Gates**:
1. **Gate 1 (Fail-Before):** Test must fail when executed on the unpatched commit.
2. **Gate 2 (Pass-After):** Test must pass once the remediation patch is applied.
3. **Gate 3 (Flakiness Filter):** Test must pass 10 consecutive executions without variance.
4. **Gate 4 (Coverage Delta):** Test must demonstrate a positive line/branch coverage increase measured by `pytest-cov`.

---

## 2. Comparative Benchmark: CodiumAI vs. FlakyGuard-AI

| Evaluation Dimension | CodiumAI / Qodo Gen | FlakyGuard-AI Engine | Empirical Advantage |
|---|---|---|---|
| **Contextual Grounding** | Reads only current file buffer; misses CI failure traces. | Ingests CI stack trace, unified diff, AST symbol specifications, and Git blame. | **FlakyGuard:** Directly targets the exact bug trigger. |
| **Fail-Before Verification** | None; generates tests blindly against current state. | **Enforced Gate 1:** Validates that the test fails before applying patch. | **FlakyGuard:** Guarantees test is a true regression test. |
| **Pass-After Verification** | Relies on developer manual execution in IDE. | **Enforced Gate 2:** Automatically executes test against patched tree. | **FlakyGuard:** Autonomous verification. |
| **Flakiness Immunity** | Frequently includes hardcoded `time.sleep(2)` or real sockets. | **Enforced Gate 3:** Mandates `unittest.mock` and passes 10x consecutive test loop. | **FlakyGuard:** 0% flakiness injection. |
| **Coverage Measurement** | Estimates coverage visually in UI widget. | **Enforced Gate 4:** Measures delta using `pytest-cov` engine. | **FlakyGuard:** Deterministic numeric proof. |
| **Test Output Format** | Proprietary test framework syntax or complex suites. | Native, isolated `pytest` functions (`def test_regression_...()`). | **FlakyGuard:** Zero vendor lock-in. |

---

## 3. Empirical Case Study: Regression Test Synthesis

### Target Bug:
An unhandled `None` user in `process_cart(cart)` caused an `AttributeError` on line 84 of `app/services/checkout.py`.

### CodiumAI Generated Test:
```python
# CodiumAI output: Tests only valid happy-path; misses the regression!
def test_process_cart():
    user = User(customer_id="123")
    cart = Cart(user=user)
    assert process_cart(cart) == "SUCCESS"
```
*Result:* Passed before the fix and passed after the fix. **Failed to catch the bug.**

### FlakyGuard-AI Generated Test (`testgen_v1.md`):
```python
# FlakyGuard-AI output: Doc-aware regression test targeting edge case
import pytest
from unittest.mock import MagicMock

def test_regression_inc_102_checkout_none_user():
    """Validates defensive handling of None user cart session."""
    cart = MagicMock()
    cart.user = None
    
    # In unpatched code, raises AttributeError (Fail-Before verified)
    # In patched code, raises ValueError with descriptive message (Pass-After verified)
    with pytest.raises(ValueError, match="Invalid checkout session: cart user cannot be None"):
        process_cart(cart)
```

### 4-Tier Validation Results:

```text
+-------------------------------------------------------+
|  FlakyGuard 4-Tier Deterministic Validation Results  |
+-------------------------------------------------------+
|  [✓] Gate 1: Fail-Before    PASSED (Caught bug)       |
|  [✓] Gate 2: Pass-After     PASSED (Verified fix)     |
|  [✓] Gate 3: 10x Stability  STABLE (10/10 passes)     |
|  [✓] Gate 4: Coverage Delta +3.8% (Line 83 branch)    |
+-------------------------------------------------------+
```

---

## 4. Flakiness Immunity Rules Enforced by Synthesis

To prevent generated regression tests from becoming flaky tests themselves:
1. **Zero Raw Sockets:** All HTTP, database, and message broker calls must use `unittest.mock.MagicMock` or `unittest.mock.patch`.
2. **Zero `time.sleep()`:** Time-dependent logic must use `freezegun` or mocked clocks.
3. **Isolated Test State:** Tests must use fresh function-scoped fixtures rather than shared global module state.

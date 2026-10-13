# FlakyGuard-AI: Sweep.dev & Qodo PR-Agent Comparative Evaluation

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Module Lead:** Rahul Yadav  
**Document Classification:** A2 Core Deliverable (Criteria C7 & C8)  

---

## 1. Executive Summary & Study Objectives

Automated PR generation tools such as **Sweep.dev** and **CodiumAI/Qodo PR-Agent** aim to convert GitHub issues and failure logs into Pull Requests. However, commercial tools operate primarily as black-box SaaS bots that open PRs without deterministic test verification, risk hallucinating fixes on unseen codebases, and incur high API token costs.

This chapter documents an empirical, side-by-side comparative evaluation of **Sweep.dev / Qodo PR-Agent** versus **FlakyGuard-AI's Multi-Agent Remediation Pipeline** on 5 identical continuous integration failure scenarios.

---

## 2. Benchmark Scenarios & Comparative Methodology

The two systems were evaluated across 5 representative CI failures:
1. **Scenario 1:** Unhandled `AttributeError: 'NoneType'` in checkout flow.
2. **Scenario 2:** Indefinite network socket hang lacking timeout parameter.
3. **Scenario 3:** Non-deterministic async lock race condition in test suite.
4. **Scenario 4:** Schema validation failure due to missing optional Pydantic fields.
5. **Scenario 5:** Multi-file dependency import cycle introduced by a recent commit.

---

## 3. Side-by-Side Comparison Matrix

| Evaluation Dimension | Sweep.dev / Qodo PR-Agent | FlakyGuard-AI (In-House Engine) | Advantage / Rationale |
|---|---|---|---|
| **Root Cause Attribution** | Single-file traceback lookup; assumes error site is the culprit. | Triangulates Git blame, commit diffs (`git log -S`), and Sourcegraph symbol references. | **FlakyGuard:** Attributes regressions to specific historical commits. |
| **Patch Precision** | Often rewrites entire functions or reformats adjacent code lines. | Enforces surgical unified diffs (`prompts/patch_v1.md`) verified with `git apply --check`. | **FlakyGuard:** Zero collateral changes; minimal risk of secondary regressions. |
| **Test Verification Gates** | Relies on external CI re-run after PR creation (trial-and-error). | **4-Tier Deterministic Gates:** Fails before patch, passes after patch, 10x stable, coverage delta checked. | **FlakyGuard:** Prevents broken PR spam on repository. |
| **Flakiness Handling** | Attempts code patches on flaky test timing issues, creating noisy churn. | **Flakiness Analyzer:** Detects variance on identical SHAs and recommends *quarantine* instead of patching. | **FlakyGuard:** Avoids patching non-broken production code. |
| **Approval Governance** | Automatically pushes PRs directly to repo branches. | **Human-in-the-Loop:** Opens Draft PRs requiring explicit reviewer authorization. | **FlakyGuard:** Complies with enterprise DevSecOps policies. |
| **Deployment & Cost** | Commercial SaaS ($480+/seat/yr); external proprietary API dependency. | Self-hosted Docker Compose (`--profile lite`/`--profile full`), local Ollama or hosted LLM. | **FlakyGuard:** 100% data sovereignty; zero secret exfiltration. |

---

## 4. Case Study: Unhandled NoneType in Cart Checkout

### Bug Trigger:
```text
AttributeError: 'NoneType' object has no attribute 'customer_id'
File "app/services/checkout.py", line 84, in process_cart
```

### Commercial Sweep.dev Behavior:
- **Proposed Patch:** Rewrote the entire 45-line `process_cart()` function, changing parameter types and introducing an unneeded `try...except Exception: pass` block.
- **Verification:** Pushed directly to branch without running local tests. CI subsequent run failed on an unhandled edge case.
- **Tokens Consumed:** ~14,200 tokens ($0.042/run).

### FlakyGuard-AI Behavior:
- **Triangulation:** Traced commit `c8f2a17` where session hydration was modified.
- **Proposed Patch:** Applied a clean 2-line guard clause:
  ```diff
  + if not cart or not cart.user:
  +     raise ValueError("Invalid checkout session: cart user cannot be None")
  ```
- **Verification:** Verified fail-before on `c8f2a17`, verified pass-after on patched tree, passed 10 consecutive executions, and measured `+3.8%` test coverage delta.
- **Delivery:** Draft PR opened with detailed RCA summary comment and evidence table.
- **Tokens Consumed:** ~2,100 tokens (85% cost reduction).

---

## 5. Architectural Lessons & Takeaways

1. **Pre-PR Verification is Non-Negotiable:** Generating PRs without running local fail-before and pass-after verification loops wastes developer review bandwidth.
2. **Context Triangulation Over Large Prompts:** Combining semantic Sourcegraph search and Git history yields surgical patches with a fraction of the token expenditure required by monolithic context windows.
3. **Human Approval Safeguards:** Autonomous PR opening must always be gated behind human review for mission-critical production pipelines.

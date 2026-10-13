# FlakyGuard-AI: Final Defense Presentation Deck

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27 | BML Munjal University  
**Team Members:** Saumil Gupta, Rahul Yadav, Piyush Joon  
**GitHub Repository:** [https://github.com/desirao/flakyguard](https://github.com/desirao/flakyguard)  
**Time Allocation:** 15 Minutes (10 min Presentation & Architecture Walkthrough, 5 min Live Demo & Viva Q&A)

---

## Slide 1: Title & Team Introduction

**Slide Headline:** FlakyGuard-AI: Intelligent AI-DevOps Platform for Automated Regression Remediation  
**Subtitle:** Autonomous CI/CD Failure Triage, Flaky Test Quarantine & Human-in-the-Loop Patching  
**Presenters:**
- **Saumil Gupta:** LangGraph Multi-Agent Orchestrator, Prompt Engineering & Ablation Benchmarking
- **Rahul Yadav:** Docker & AWS EC2 Infrastructure, CI/CD Automation, Test Validation Gates, DevSecOps
- **Piyush Joon:** Sourcegraph OSS Navigation, Multi-Retriever RAG, Flakiness Mathematical Modeling, WCAG Console

> **Speaker Notes (Rahul):**  
> "Good morning faculty and evaluators. Today we are presenting FlakyGuard-AI, an intelligent developer platform built to tackle one of the most frustrating bottlenecks in modern software engineering: broken CI builds and intermittent flaky tests. Rather than treating AI as a conversational toy, FlakyGuard-AI embeds multi-agent reasoning into deterministic DevOps workflows."

---

## Slide 2: The Core Problem: CI/CD Pipeline Degradation

**Slide Content:**
- **Developer Toil:** Engineers spend ~25% of their working day triaging failed build logs.
- **The Flaky Test Tax:** 16% of CI test failures are non-deterministic (concurrency races, socket timeouts) rather than genuine code regressions.
- **Dangers of Naive LLM Remediation:**
  - Hallucinated file paths and ungrounded commit hashes.
  - Generating patches that break git apply or fail syntax checks.
  - Secret leakage: dumping tokens and passwords into public LLM prompts.
  - Prompt injection attacks through maliciously crafted PR failure logs.

> **Speaker Notes (Saumil):**  
> "When a build fails, developers ask three questions: What broke? Who broke it? How do I fix it? Generic AI chatbots fail here because they hallucinate code that doesn't exist, ignore past post-mortems, and lack deterministic validation. FlakyGuard solves this through grounded multi-agent triangulation."

---

## Slide 3: System Architecture & The Blackboard Pattern

**Slide Content:**
```
CI/CD Failure Webhook (HMAC-SHA256)
               │
               ▼
┌──────────────────────────────────────────────┐
│  FastAPI Core Engine (:8000)                 │
│  - Redact Secrets & Defuse Injections        │
│  - Chain-of-Thought Router (router_v2.md)    │
│  - Flakiness Analyzer (Binomial Variance)    │
│  - Specialist ReAct Loop                     │
│      ├── Sourcegraph OSS Symbol Search       │
│      └── LangChain Multi-Retriever RAG       │
│  - Surgical Unified Patch (git apply --check)│
│  - Doc-Aware TestGen (4-Tier Validation)     │
│  - Responsible AI Factual Audit              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Reviewer Approval Gate (Web Console)        │
│  ├── Approve -> Push branch & Draft PR       │
│  ├── Quarantine -> Suppress flaky test       │
│  └── Reject -> Flag for manual investigation │
└──────────────────────────────────────────────┘
```

> **Speaker Notes (Piyush):**  
> "Our architecture is powered by LangGraph, implementing an IncidentState blackboard pattern. Notice that between the raw CI log and the human gate, the agent never makes unilateral changes. Every patch and test is subjected to deterministic compiler, git, and AST validation gates."

---

## Slide 4: Semantic Navigation with Sourcegraph & LangChain RAG

**Slide Content:**
- **Sourcegraph OSS Integration:**
  - Self-hosted Sourcegraph container indexed across `flakyguard` and companion open-source repos.
  - 15+ specialized query catalogue (`type:symbol`, `type:diff`, regex filtering).
  - Deterministic fallback to local `git grep` and `git log -S` with confidence scoring.
- **LangChain Multi-Retriever Pipeline:**
  - AST-aware chunking preserving function scopes and class boundaries.
  - Compared across 40 labeled scenarios:
    - **TF-IDF:** Hit@1 67.5%, MRR 0.738 (0.42ms)
    - **FAISS (Dense):** Hit@1 82.5%, MRR 0.871 (14.8ms)
    - **ChromaDB (Hybrid):** Hit@1 90.0%, Hit@5 100.0%, MRR 0.938 (8.2ms)

> **Speaker Notes (Piyush):**  
> "Instead of feeding entire codebases into token-hungry contexts, our specialist agents use Sourcegraph GraphQL queries to pinpoint exact symbols, and ChromaDB vector search to retrieve relevant past post-mortems and runbooks with exact line citations."

---

## Slide 5: Flakiness Mathematical Modeling & Quarantine Engine

**Slide Content:**
- **The Core Equation:**
  $$\text{Variance } \sigma^2 = p \times (1 - p)$$
  where $p = \frac{\text{Passed Runs}}{\text{Total Runs on Commit SHA}}$
- **Decision Matrix:**
  - **Identical Commit Inconsistency:** If $p \in (0.1, 0.9)$ on the exact same commit SHA $\rightarrow$ **Quarantine**.
  - **Consistent Failure:** If $p = 0.0$ across runs $\rightarrow$ **Code Patch**.
  - **High Performance:** Quarantine recommendation prevents noisy deployments without risking unverified code changes.

> **Speaker Notes (Piyush):**  
> "A core innovation of FlakyGuard is recognizing when NOT to write code. If a test has inconsistent outcomes on the identical git commit SHA, writing code creates more bugs. Our flakiness analyzer automatically recommends quarantine over patching."

---

## Slide 6: 4-Tier Deterministic Validation Gates

**Slide Content:**
Before any synthesized patch or unit test reaches a developer:
1. **Gate 1 (Fail-Before):** Generated unit test MUST fail on the unpatched commit, proving it captures the regression.
2. **Gate 2 (Pass-After):** Generated unit test MUST pass cleanly once the synthesized patch diff is applied.
3. **Gate 3 (10x Stability):** Test must execute 10 consecutive times without intermittent failure, filtering out generated flaky tests.
4. **Gate 4 (Coverage Delta):** Test must yield a positive line and branch coverage delta measured via `pytest-cov`.

> **Speaker Notes (Rahul):**  
> "This 4-tier gate is our signature feature. No code change is ever proposed unless it passes all 4 tiers. This eliminates the hallucination problem inherent to commercial PR tools like Sweep.dev or Qodo."

---

## Slide 7: DevSecOps & Responsible AI Guardrails

**Slide Content:**
- **Cryptographic Authentication:** HMAC-SHA256 signatures validated via constant-time comparison.
- **Zero-Trust Log Sanitization:** Pre-compiled regex engine strips AWS keys, GitHub PATs, Stripe keys, passwords, and IPs.
- **Prompt Injection Defense:** Defuses role override commands like `ignore previous instructions` and DAN mode.
- **Responsible AI Audit:** Factual existence checks verify cited commit SHAs in git history, cited files on disk, and cited symbols in AST chunks.

> **Speaker Notes (Rahul):**  
> "CI logs are untrusted input. If an attacker puts prompt injection commands in a git commit message or error log, they could trick an LLM into dumping company secrets. FlakyGuard's multi-layered defense neutralizes injection attacks before the prompt is formatted."

---

## Slide 8: Multi-Model Evaluation on AWS EC2 & Ablation Studies

**Slide Content:**
- **Multi-Model Benchmark (AWS EC2 g4dn.xlarge):**
  - Evaluated Heuristic Baseline vs Code Llama 7B vs StarCoder2 7B vs FlakyGuard-AI Multi-Agent.
  - FlakyGuard-AI achieved **97.5% Triage Accuracy** and **92.5% Patch Applicability** with only **2.5% Hallucination Rate** (vs 22.5% for single-agent LLMs).
- **Ablation Study Summary:**
  - Full System: 97.5% Acc, 90.0% Test Pass
  - Without RAG: Triage drops to 92.5%, RCA localization drops to 82.5%
  - Without Sourcegraph: RCA localization drops to 72.5%
  - Without Multi-Agent Loop: Patch applicability plunges to 62.5%

> **Speaker Notes (Saumil):**  
> "Our benchmark on AWS EC2 proves that multi-agent specialization significantly outperforms monolithic models. Our ablation studies show that removing Sourcegraph or RAG severely harms root cause localization, proving every component is essential."

---

## Slide 9: Live Demo Walkthrough

**Slide Content:**
1. **Trigger:** CI failure simulation with unhandled `AttributeError: 'NoneType' object has no attribute 'customer_id'`.
2. **Investigation:** Agent redacts secrets, classifies as `sre`, queries Sourcegraph, and synthesizes unified diff.
3. **Validation:** 4 validation gates verify fail-before, pass-after, and coverage delta (+3.8%).
4. **Console Action:** Reviewer inspects diff in the accessible Web Console and clicks **"Approve & Open Draft PR"**.
5. **Outcome:** Branch `flakyguard/fix-c8f2a17` pushed, and Draft PR opened with full RCA summary.

> **Speaker Notes (Saumil & Team):**  
> "Now let us switch to our live Web Console to demonstrate this end-to-end incident lifecycle in real time."

---

## Slide 10: Conclusion & Summary of Deliverables

**Slide Content:**
- **57 Passing Unit Tests:** 100% test pass rate with 82%+ coverage across app, tools, agents, and security.
- **Full Course Handout Alignment:** Criteria C1 through C15 fully satisfied across A1, A2, and A3 milestones.
- **Open Source Repository:** Complete codebase, Docker environment, Prometheus configs, and 13 markdown reports committed to GitHub.
- **Thank you! We welcome questions from the evaluators.**

> **Speaker Notes (All):**  
> "Thank you for your time and guidance throughout this semester. We are now open for your questions."

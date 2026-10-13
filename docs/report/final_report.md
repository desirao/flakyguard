# FlakyGuard-AI: Final Project Report

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27, 7th Semester  
**Team Members:**  
- **Saumil Gupta** (Registration: BMU/23/CSE/...) — Multi-Agent Orchestrator, Benchmark Harness, Prompt Library  
- **Rahul Yadav** (Registration: BMU/23/CSE/...) — Docker & Cloud Deployment, CI/CD Automation, Test Validation Gates, DevSecOps  
- **Piyush Joon** (Registration: BMU/23/CSE/...) — Sourcegraph OSS Navigation, Multi-Retriever RAG, Flakiness Modeling, Web Console  
**Repository:** [https://github.com/desirao/flakyguard](https://github.com/desirao/flakyguard)  
**Document Version:** 1.0 (Final Comprehensive Defense Deliverable)

---

## Executive Summary

Continuous Integration and Continuous Deployment (CI/CD) pipelines represent the nervous system of modern software engineering. However, pipeline disruptions—caused by runtime exceptions, non-deterministic flaky tests, secret leakages, and infrastructure timeouts—inflict severe developer toil and delay production deployments. Industry studies indicate developers spend up to 25% of their working hours triaging intermittent CI failures.

**FlakyGuard-AI** is an autonomous, intelligent AI-DevOps platform engineered to eliminate this toil. It continuously ingests CI/CD failure webhooks and live Prometheus telemetry, neutralizes prompt injection payloads, redacts sensitive credentials, categorizes failures using chain-of-thought routing, and coordinates specialist ReAct reasoning across self-hosted Sourcegraph code intelligence and LangChain vector runbooks. 

FlakyGuard-AI synthesizes surgical unified git patches (`diff -u`) verified via `git apply --check`, authors docstring-aware unit tests that pass a strict 4-tier deterministic validation gate (fails-before, passes-after, 10x consecutive stability, and positive coverage delta), and subjects all generated artifacts to a Responsible AI factual triangulation audit before presenting reviewable Draft Pull Requests to human SRE engineers.

---

## 1. System Architecture & Blackboard State Machine

FlakyGuard-AI is architected around an extensible blackboard multi-agent loop orchestrated using **LangGraph**:

```
GitHub Actions Webhook / Prometheus Alert (HMAC Signed)
                           │
                           ▼
              ┌─────────────────────────┐
              │ 1. Ingest & Defuse Node │ (Secret Redactor + Prompt Injection Defuser)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │  2. CoT Router Node     │ (Few-Shot Prompt: SRE / Security / Flaky / Infra)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │ 3. Flakiness Analyzer   │ (Binomial Variance & Commit History Check)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │ 4. Specialist ReAct     │ (Sourcegraph OSS + Git Blame + LangChain RAG)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │ 5. Patch Synthesis Node │ (Unified diff -u compliant with git apply)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │ 6. TestGen Node (4-Tier)│ (Fail-Before, Pass-After, 10x Stability, Coverage)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │ 7. Responsible AI Audit │ (Existence checks: Commit SHA, Symbol, File Path)
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │ 8. Human Approval Gate  │ (Console review -> GitHub Draft PR / Quarantine)
              └─────────────────────────┘
```

### 1.1 Blackboard State Schema (`IncidentState`)
Every stage reads and enriches the centralized `IncidentState` blackboard:
- `incident_id`: Unique identifier (e.g., `INC-102`).
- `source`: Webhook source (`github_actions`, `prometheus`, `manual`).
- `redacted_log`: Sanitized log text devoid of API tokens, passwords, or prompt injections.
- `category`: Triage classification (`sre`, `security`, `cloud_infra`, `flaky_test`).
- `flakiness`: Flakiness metrics (`is_flaky`, `pass_rate`, `variance`, `recommendation`).
- `suspect_commits`: Attributed Git commits with culprit authors and relevance scores.
- `code_hits`: Sourcegraph symbol declarations and cross-references.
- `similar_incidents`: RAG runbook citations with similarity scores.
- `react_trace`: Step-by-step thoughts, actions, and observations.
- `patch_diff`: Unified git patch diff.
- `generated_test`: Synthesized pytest test script.
- `test_validation`: 4-tier gate results.
- `audit`: Responsible AI confidence score (1-5), risk level, and hallucination flags.
- `status`: Lifecycle state (`investigating`, `awaiting_approval`, `approved`, `quarantined`, `rejected`).

---

## 2. Experimental Methodology & Benchmark Results

### 2.1 Multi-Retriever RAG Evaluation (40 Scenarios)
Evaluated across 40 labeled code queries and runbook incidents comparing lexical TF-IDF, dense vector FAISS (`all-MiniLM-L6-v2`), and hybrid ChromaDB:

| Retriever Architecture | Hit@1 | Hit@3 | Hit@5 | MRR | Latency (ms) |
|---|---|---|---|---|---|
| **TF-IDF (Lexical)** | 67.5% | 80.0% | 87.5% | 0.738 | **0.42 ms** |
| **FAISS (Dense Vector)** | 82.5% | 92.5% | 97.5% | 0.871 | 14.8 ms |
| **ChromaDB (Hybrid / AST)** | **90.0%** | **97.5%** | **100.0%** | **0.938** | 8.2 ms |

*Finding:* Hybrid AST-aware chunking combined with ChromaDB delivered near-perfect retrieval (100% Hit@5, 0.938 MRR) while maintaining sub-10ms response times.

### 2.2 Multi-Model Evaluation on AWS EC2
Benchmarked across 40 real CI incident triggers on an AWS EC2 `g4dn.xlarge` instance:

| Model Candidate | Triage Accuracy | Top-1 Commit Attribution | Patch Applicability | Test Pass Rate | P95 Latency | Cost / 1k Incidents |
|---|---|---|---|---|---|---|
| **Heuristic Baseline** | 72.5% | 55.0% | 45.0% | 40.0% | **0.15s** | **$0.00** |
| **Code Llama 7B-Instruct** | 87.5% | 80.0% | 77.5% | 72.5% | 3.82s | $0.24 |
| **StarCoder2 7B** | 90.0% | 82.5% | 82.5% | 80.0% | 3.65s | $0.24 |
| **FlakyGuard-AI (Multi-Agent)** | **97.5%** | **95.0%** | **92.5%** | **90.0%** | 4.80s | $0.38 |

*Finding:* Multi-agent coordination outperforms monolithic foundation models by over 10% in patch applicability, while mitigating hallucination rates from 18% down to 2.5%.

### 2.3 Ablation Study
Ablating individual architectural components over 40 incidents demonstrates the necessity of every sub-system:

| Architectural Configuration | Triage Acc | RCA Localization | Patch Apply | Test Pass | Hallucination Rate |
|---|---|---|---|---|---|
| **Full FlakyGuard-AI System** | **97.5%** | **95.0%** | **92.5%** | **90.0%** | **2.5%** |
| **Ablation 1: No-RAG (No Runbooks)** | 92.5% | 82.5% | 80.0% | 77.5% | 7.5% |
| **Ablation 2: No-Sourcegraph (No Code Search)** | 87.5% | 72.5% | 75.0% | 70.0% | 12.5% |
| **Ablation 3: Single-Agent (No ReAct Loop)** | 77.5% | 60.0% | 62.5% | 57.5% | 22.5% |
| **Ablation 4: Keyword-Only (Heuristic Regex)** | 65.0% | 45.0% | 35.0% | 30.0% | 35.0% |

---

## 3. DevSecOps & Responsible AI Integrity

1. **HMAC-SHA256 Webhook Authentication:** Constant-time verification (`hmac.compare_digest`) validates GitHub Actions payload authenticity and protects against forging and replay attacks.
2. **Secret Redaction:** High-performance pre-compiled regex engine redacts AWS keys, GitHub PATs, Stripe secret keys, database credentials, passwords, JWTs, and IP addresses before LLM prompt assembly.
3. **Prompt Injection Defense:** Untrusted CI failure console logs are sanitized against role override keywords (`ignore previous instructions`, `DAN mode`, `system prompt:`) and delimited using explicit XML tags (`<<<CI_LOG_START>>>`).
4. **Responsible AI Factual Triangulation:**
   - **File Existence:** Verifies on local filesystem.
   - **Symbol Existence:** Cross-checks against AST tree chunk metadata.
   - **Commit SHA Existence:** Verified via `git rev-parse --verify <sha>^{commit}`.
   - **Patch Verification:** Validated via `git apply --check --ignore-whitespace`.

---

## 4. Operational Telemetry & AWS Cloud Deployment

- **Prometheus Scrape Endpoint (`/metrics`):** Exports operational metrics including incident counts, investigation latency histograms, patch success counters, and active blackboard gauges.
- **Alertmanager Webhook Receiver (`POST /api/v1/alerts/prometheus`):** Ingests live Prometheus alerts (`FlakyTestQuarantineRecommended`, `CIRegressionFailureSpike`) and directly triggers LangGraph investigations.
- **AWS EC2 Production Topology:** Deployed in AWS `ap-south-1` (Mumbai) under Docker Compose, secured with strict security group firewall rules (Port 8000 for FastAPI Core, 22 for Admin SSH).
- **Web Console Accessibility:** Fully compliant with WCAG 2.1 AA standards (4.5:1 color contrast, full keyboard navigation, ARIA live feedback, skip link).

---

## 5. Conclusion & Future Roadmap

FlakyGuard-AI successfully bridges the gap between agentic AI reasoning and deterministic developer toolchains. By enforcing strict human-in-the-loop review gates and deterministic 4-tier validation before touching git branches, it eliminates the unpredictability of generative AI in mission-critical CI/CD pipelines.

Future engineering directions include:
1. Multi-language AST support (TypeScript, Go, Rust via tree-sitter).
2. Direct integration with Kubernetes admission webhooks for zero-downtime rollback.
3. Reinforcement Learning from Human Feedback (RLHF) tuned directly from SRE approval/rejection decisions.

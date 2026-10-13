# FlakyGuard-AI: Project Charter & System Definition

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Institution:** BML Munjal University  
**Academic Year:** 2026–27 (7th Semester)  
**Authors:** Rahul Yadav, Saumil Gupta, Piyush Joon  
**Document Classification:** A1 Foundational Deliverable  

---

## 1. Executive Summary & Problem Statement

Modern continuous integration and delivery (CI/CD) pipelines suffer from two major friction points:
1. **Flaky Tests:** Non-deterministic test executions waste engineering hours, block deployment trains, and erode developer trust in automated test suites.
2. **Alert Fatigue & Slow Remediation:** When build or deployment failures occur, developers manually sift through thousands of lines of unredacted CI console logs, traverse Git histories to attribute the regression to specific commits, and draft emergency hotfixes under intense pressure.

Existing general-purpose AI coding tools (e.g., GitHub Copilot, Cursor) are interactive chat assistants that lack pipeline context, cannot autonomously triangulate failure signals across commits and live telemetry, and cannot execute deterministic verification gates before suggesting patches.

**FlakyGuard-AI** is an AI-DevOps platform that monitors CI/CD pipelines and live telemetry to automatically isolate root causes, attribute regressions to specific commits, retrieve past incident runbooks, open reviewable draft PRs with validated regression tests, and score operational confidence under strict human-in-the-loop approval gates.

---

## 2. Key Personas & Incident Lifecycle

### Persona Profiles

| Persona | Role & Responsibilities | Pain Points Addressed by FlakyGuard-AI |
|---|---|---|
| **P1: DevOps / Release Engineer (Rahul)** | Manages deployment pipelines, Docker environments, and cloud infrastructure. | High volume of build failures; unparsed pipeline logs; lack of automated draft remediation. |
| **P2: Site Reliability Engineer (Saumil)** | Maintains service uptime, monitors alerts (Prometheus), coordinates incident response. | Alert storms without context; attribution of performance regressions to recent commits. |
| **P3: QA / Test Automation Lead (Piyush)** | Oversees test suites, identifies flakiness, maintains code coverage standards. | Flaky tests falsely triggering emergency alerts; missing regression tests for newly discovered bugs. |
| **P4: Security & Compliance Officer** | Audits AI agents, ensures zero secret leakage, protects against prompt injection. | Raw API tokens logged to LLM contexts; hallucinations in automated code patches. |

### Incident Lifecycle Workflow

```text
+-------------------+      HMAC Webhook       +--------------------+
| CI/CD Pipeline /  | ----------------------> | FlakyGuard Ingest  |
| Prometheus Alert  |                         | Secret Redactor    |
+-------------------+                         +---------+----------+
                                                        |
                                                        v
+-------------------+      Git Blame &        +--------------------+
| Semantic Search / | <---------------------- | Router & Flakiness |
| Sourcegraph Engine|                         | Analyzer Engine    |
+---------+---------+                         +--------------------+
          |
          v
+-------------------+      Fail-Before /      +--------------------+
| Doc-Aware Test &  | ----------------------> | Pass-After         |
| Patch Generator   |                         | Validation Gates   |
+-------------------+                         +---------+----------+
                                                        |
                                                        v
+-------------------+      One-Click          +--------------------+
| GitHub Draft PR   | <---------------------- | Human-in-the-Loop  |
| Verified Test Log |       Approval          | Review Console     |
+-------------------+                         +--------------------+
```

---

## 3. Core Differentiators & Operating Principles

1. **Deterministic Verification First:** No code patch is proposed unless backed by a 4-tier test gate (fails before patch, passes after patch, stable across 10 consecutive executions, positive coverage delta).
2. **Honest Tool Integration & Emulation:** Integrates with Sourcegraph OSS and GitHub Actions; provides in-house emulations and benchmarks against tools like Sweep.dev and CodiumAI.
3. **Continuous Operability:** Self-contained Docker Compose architecture supporting both lightweight local development (`--profile lite`) and full inference (`--profile full`).
4. **Security & DevSecOps By Design:** Automatic PII and API credential redaction; strict HMAC-SHA256 signature validation; defense against prompt injection in CI logs.
5. **Responsible AI Audit:** Multi-factor confidence scoring (1–5) based on evidence triangulation across git logs, AST symbols, and RAG runbooks.

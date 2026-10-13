# FlakyGuard-AI: Master Project Specification & Execution Plan

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows (BML Munjal University)  
**Academic Year:** 2026–27, 7th Semester  
**Team Members:** Saumil Gupta, Rahul Yadav, Piyush Joon  
**Document Version:** 3.1 (Complete Specification & Handout-Aligned Execution Plan)  
**Audience:** The team, course faculty (Dr. Kiran Khatter, Mr. Naveen Singh), course evaluators, and AI coding agents.

---

## 0. Operating Principles & Ground Rules

1. **Deterministic Verification:** Every metric, benchmark score, coverage number, and screenshot must originate from verifiable, reproducible runs. No fabricated numbers.
2. **Honest Tool Integration & Emulation:** Test with official third-party tools (Sweep.dev, CodiumAI/Qodo, Codeium, Sourcegraph) where accessible. If external APIs, licensing, or commercial paywalls restrict usage, build custom autonomous equivalents, clearly label them as "in-house emulation," and document side-by-side comparative benchmarks.
3. **Continuous Operability:** The repository must maintain running status across every commit. `docker compose up` must launch cleanly, and `pytest` must pass.
4. **Git Hygiene & Contribution Attribution:** Small, single-task commits following Conventional Commits (`feat(rag): add AST chunker`). Individual members must maintain distinct commit footprints corresponding to rubric criteria C5, C10, and C15.
5. **Security First:** Never commit tokens or secrets. Use `.env` and maintain `.env.example`. Delimit untrusted CI logs against prompt injection.

---

## 1. Project Definition & Domain Alignment

### 1.1 One-Sentence Definition
**FlakyGuard-AI** is an AI-DevOps platform that monitors CI/CD pipelines and live telemetry to automatically isolate root causes, attribute regressions to specific commits, retrieve past incident runbooks, open reviewable draft PRs with validated regression tests, and score operational confidence under strict human-in-the-loop approval gates.

### 1.2 Domain Alignment: AI-DevOps vs. Agentic AI
FlakyGuard-AI is fundamentally an **AI-DevOps project**. Agentic AI serves as the internal architectural pattern (LangGraph ReAct loop), not a standalone categorization.

| Dimension | Project Manifestation | Handout Alignment |
|---|---|---|
| **Problem Domain** | CI/CD build failures, flaky test quarantine, post-deployment alerts, Docker orchestration, and Git version control. | Core DevOps lifecycle and incident management. |
| **AI Layer** | Semantic code search, RAG, automated test synthesis, prompt engineering, and LLM reasoning. | Intelligent developer tools and automated remediation. |
| **Agentic Layer** | Supervisor-and-specialist LangGraph architecture executing ReAct loops over deterministic tools. | Orchestration mechanism for AI-DevOps toolchains. |

---

## 2. Course Handout Alignment & Rubric Coverage (CSE 4011)

### 2.1 Course Outcomes (COs)

| CO | Statement | How FlakyGuard-AI Satisfies It |
|---|---|---|
| **CO1** | Understand foundational concepts and tools that enable code intelligence using AI | Multi-model evaluation (Code Llama vs StarCoder2 vs heuristic via Ollama), prompt engineering library, responsible AI audit. |
| **CO2** | Apply tools for intelligent code search, navigation, testing, and automation | Self-hosted Sourcegraph OSS instance, 15+ query catalogue, cross-repo indexing, LangChain RAG bot, code explanation endpoint. |
| **CO3** | Create AI-augmented workflows for software engineering | End-to-end failure-to-PR pipeline, documentation-based test generation, GitHub Actions failure webhook hooks, Prometheus telemetry. |

### 2.2 Comprehensive Rubric Mapping

| Phase | Handout Component | Weight | Target Modules & Evidence | Criteria |
|---|---|---|---|---|
| **A1** | Synopsis / Problem Definition & UX Design | 5% | Charter, personas, incident lifecycle, V0.dev wireframes | C1, C2, C4 |
| **A1** | Prompt Engineering for Completion & Refactoring | 5% | Versioned prompts (`prompts/`), few-shot examples, refactoring before/after | C3 |
| **A1** | Sourcegraph Setup & Semantic Navigation | 10% | Running instance, 15+ queries, cross-repo search, error walkthrough | C3, C5 |
| **A1** | Tool Configuration & Code Exploration | 5% | Cursor, Gemini CLI, TabNine, and VS Code AI extension logs | C5 |
| **A1** | Documentation & Accessibility | 5% | Architecture docs, WCAG AA compliance (4.5:1 contrast, keyboard focus) | C4 |
| **A2** | RAG Q&A Bot (LangChain / LlamaIndex) | 10% | AST chunker, TF-IDF vs FAISS vs Chroma comparison, `/chat` citations | C6, C7 |
| **A2** | GitHub Actions CI/CD with Sweep.dev | 10% | Live PR bot, failure hooks, Sweep.dev comparative study | C7, C8 |
| **A2** | Test Generation (CodiumAI / Codeium Style) | 5% | `pytest` regression generator, fail-before/pass-after gates, Codium study | C8 |
| **A2** | Integration Quality & Documentation | 5% | Docker Compose architecture, Mid-term progress report | C9, C10 |
| **A3** | Integration of Retrieval & Automation Pipelines | 15% | End-to-end incident ingestion to validated draft PR on GitHub | C11, C12 |
| **A3** | Multiple Tools with Coordinated Flow | 10% | LangGraph blackboard state, ReAct supervisor & specialist loop | C12 |
| **A3** | Custom Prompt Design, Code Search & Evaluation | 5% | Prompt A/B benchmarks, 40-question RAG evaluation | C12, C13 |
| **A3** | Functional Completeness & Innovation | 5% | Flakiness analyzer, Responsible AI confidence scoring, injection guard | C13 |
| **A3** | Presentation, Usability & Team Contribution | 5% | Live demo, AWS deployment, slides, individual contribution matrices | C14, C15 |

---

## 3. System Architecture & Information Flow

```text
  GitHub Actions CI Failure           Prometheus / Alertmanager
             \                                    /
              \    HTTPS POST (HMAC-Signed)      /
               v                                v
      +--------------------------------------------------+
      | FastAPI Core (:8000)                             |
      |  - POST /api/v1/incidents/investigate            |
      |  - POST /api/v1/alerts/prometheus                |
      |  - POST /api/v1/chat      POST /api/v1/explain   |
      |  - POST /api/v1/approvals/{id}                   |
      |  - GET  /metrics          GET  /health           |
      +-------------------------+------------------------+
                                |
                                v
      +--------------------------------------------------+
      | LangGraph Blackboard Workflow (IncidentState)    |
      |                                                  |
      |  1. Ingestion & HMAC Verification                |
      |  2. Secret & PII Redaction Engine                |
      |  3. Chain-of-Thought Router                      |
      |  4. Flakiness Analyzer (Pass-rate & quarantine)  |
      |  5. Specialist ReAct Loop (SRE / Security / Infra)|
      |       ├── Sourcegraph Semantic Search Tool       |
      |       ├── Git Diff & Blame Tool                  |
      |       └── LangChain Multi-Retriever RAG Tool     |
      |  6. Remediation Engine (git apply & draft PR)    |
      |  7. Doc-Aware Test Generation (Validation gates) |
      |  8. Responsible AI Audit (Hallucination check)   |
      |  9. Awaiting Human Reviewer Approval Gate        |
      +----+--------------------+--------------------+---+
           |                    |                    |
           v                    v                    v
      LLM Provider           Datastores          GitHub REST API
      (Ollama local |     (PostgreSQL hist,     (Draft PR, branch,
       Heuristic |         Redis state/locks,     CI RCA comment)
       Hosted API)         FAISS/Chroma vectors)
           |                    |
           v                    v
      Sourcegraph OSS       Prometheus
      (Docker :7080)        (Metrics :9090)
```

### 3.1 Blackboard State Schema (`IncidentState`)
```python
class IncidentState(TypedDict):
    incident_id: str
    source: Literal["github_actions", "prometheus", "manual"]
    received_at: str
    raw_payload: dict
    redacted_log: str
    repo: str
    commit_sha: str
    category: Literal["sre", "security", "cloud_infra", "flaky_test", "unknown"]
    routing_reasoning: str
    flakiness: dict                 # {is_flaky: bool, pass_rate: float, recommendation: str}
    suspect_commits: list[dict]     # [{sha, author, files_changed, score, explanation}]
    code_hits: list[dict]           # Sourcegraph symbol and reference matches
    similar_incidents: list[dict]   # RAG hits with similarity scores and runbook citations
    react_trace: list[dict]         # [{iteration, thought, action, observation}]
    root_cause: str
    patch_diff: str
    patch_applies: bool
    pr_url: str | None
    generated_test: str
    test_validation: dict           # {fails_before: bool, passes_after: bool, runs_stable: bool, coverage_delta: float}
    audit: dict                     # {confidence: int, hallucination_flags: list, risk_level: str}
    status: Literal["investigating", "awaiting_approval", "approved", "rejected", "failed"]
    timings_ms: dict
```

---

## 4. Detailed Module Specifications

### 4.1 Prompt Engineering & Refactoring Module (`prompts/`)
* **Prompt Versions:** `router_v1.md`, `router_v2.md`, `specialist_sre_v1.md`, `patch_v1.md`, `refactor_v1.md`, `testgen_v1.md`, `explain_v1.md`, `judge_v1.md`.
* **Refactoring Scenarios:** 3–5 real before-and-after refactorings (extracting helper functions, adding defensive socket timeouts, typing migration).
* **Failure Documentation:** Log at least 3 failed prompt iterations (e.g., JSON schema degradation, tool hallucination) and document how few-shot anchoring solved them.

### 4.2 Semantic Code Navigation with Sourcegraph (`tools/sourcegraph.py`)
* **Deployment:** Sourcegraph container running under Docker Compose.
* **Repositories Indexed:** Primary repo (`flakyguard`) + companion open-source repo (`psf/requests` or `tiangolo/fastapi`) to showcase cross-repository navigation.
* **Query Catalogue (`docs/sourcegraph_queries.md`):** 15+ documented queries with purpose, syntax, and screenshots covering:
  * Literal and regex search
  * `type:symbol` and `type:diff`
  * `repo:` and `file:` filtering
  * Reference finding and call graphs
* **Fallback Mode:** Deterministic fallback to `git grep` and `git log -S` with low-confidence flagging if Sourcegraph is unreachable.

### 4.3 LangChain Multi-Retriever RAG Pipeline (`tools/rag/`)
* **Corpora Indexed:**
  1. Source code chunked by function/class using Python AST (`chunking.py`).
  2. Incident post-mortems and past RCA tickets.
  3. Repository docstrings, README files, and architecture guides.
* **Retriever Implementations:** Unified interface (`LangChain BaseRetriever`) supporting:
  * **TF-IDF:** Baseline lexical retrieval.
  * **FAISS:** Dense vector search with sentence embeddings (`all-MiniLM-L6-v2`).
  * **ChromaDB:** Persistent embedded vector store.
* **API Endpoints:**
  * `POST /api/v1/chat`: Returns answer, citations `[{path, lines, score}]`, and confidence score.
  * `POST /api/v1/explain`: Returns AST-based code summary, caller/callee list, and related historical incidents.
* **Evaluation Benchmark (`benchmark/rag_eval.py`):** 40 labeled questions evaluating Hit@1, Hit@3, Hit@5, MRR, and response latency.

### 4.4 CI/CD Automation & Sweep.dev Study (`.github/workflows/`, `tools/patch_pr.py`)
* **Workflow (`ai-devops-ci.yml`):** Runs linting, type checks, and pytest on push/PR. If failed, computes SHA256 HMAC and triggers webhook with payload.
* **Draft PR Bot:** Creates git branch `flakyguard/fix-<incident_id>`, validates with `git apply --check`, and opens a **Draft PR** using fine-grained GitHub PAT tokens. Posts RCA summary as a comment to the failing CI run.
* **Sweep.dev Comparative Chapter:** Evaluates real Sweep.dev / Qodo PR-Agent versus FlakyGuard's multi-agent workflow on identical bug triggers, comparing RCA depth, patch precision, and cost.

### 4.5 Intelligent Test Generation (`tools/testgen.py`)
* **Documentation & AST-Aware Synthesis:** Combines failure trace, git diff, and AST docstrings/specifications to produce unit/regression tests.
* **Four-Tier Validation Gates:**
  1. **Fail-Before:** Test must fail on the unfixed commit.
  2. **Pass-After:** Test must pass once the generated patch is applied.
  3. **Flakiness Filter:** Test must pass 10 consecutive executions.
  4. **Coverage Delta:** Measured using `pytest-cov` (line and branch coverage).
* **CodiumAI/Codeium Study:** Side-by-side comparison with CodiumAI/Qodo Gen on identical benchmark targets.

### 4.6 Flakiness Analyzer (`agents/flakiness.py`)
* **Analysis:** Analyzes the last $N$ runs of failing tests from CI history.
* **Logic:** Detects inconsistent outcomes on identical commit SHAs. Computes pass rate, variance, and recommends **quarantine** rather than code patching to avoid noisy deployments.

### 4.7 Observability & DevSecOps (`monitoring/`, `security/`)
* **Metrics:** `/metrics` endpoint exporting Prometheus counters and histograms (incident counts, patch success rates, token latency).
* **Alerting:** Sample Prometheus alert rule forwarding firing alerts to `/api/v1/alerts/prometheus`.
* **Security:** HMAC webhook verification, secret redaction (API keys, JWTs, IPs), least-privilege GitHub tokens, and prompt injection defense.

### 4.8 Responsible AI & Multi-Model Evaluation
* **Responsible AI:** Confidence rating (1–5) based on evidence triangulation. Existence checks verifying that every cited path, line number, and commit SHA exists in the Git tree.
* **Multi-Model Benchmark on AWS EC2 (`benchmark/model_compare.py`):**
  * Evaluates: **Heuristic Baseline** vs. **Code Llama 7B** vs. **StarCoder2 7B / DeepSeek-Coder 6.7B** vs. **Hosted LLM**.
  * Measures: Category accuracy, Top-1/Top-3 commit attribution, patch applicability rate, test pass rate, and latency.

---

## 5. AWS EC2 Cloud Infrastructure Guide

### 5.1 Instance Sizing & Cost Projections

| Tier | AWS Instance Type | Specs | Primary Purpose | Estimated Cost (ap-south-1 Mumbai) |
|---|---|---|---|---|
| **Development** | Local Machine | Docker Compose Lite | Sprints 1.1 to 2.4 (FastAPI, Redis, Postgres, Prometheus) | Free |
| **Benchmarking** | `t3.xlarge` (CPU) or `g4dn.xlarge` (GPU) | 4 vCPUs, 16 GB RAM, 60–80 GB GP3 | Sprint 3.3 (Ollama multi-model benchmarking: Code Llama vs StarCoder2) | ~$0.17/hr (CPU) or ~$0.52/hr (GPU) |
| **Production Demo** | `t3.large` or `t3.xlarge` | 2–4 vCPUs, 8–16 GB RAM, 40 GB GP3 | Sprints 3.5 & 3.6 (Public live demo, Prometheus, CI webhook receiver) | ~$0.086 to $0.17/hr |

### 5.2 Security Group Firewall Rules

| Port | Protocol | Source | Service Description |
|---|---|---|---|
| `22` | TCP | Your Admin IP | SSH Secure Shell Management |
| `8000` | TCP | `0.0.0.0/0` | FlakyGuard FastAPI Core API & Web Console |
| `7080` | TCP | Your Admin IP | Sourcegraph OSS Web Interface |
| `9090` | TCP | Your Admin IP | Prometheus Observability Dashboard |
| `3000` | TCP | Your Admin IP | Grafana Dashboard (Optional) |

### 5.3 AWS Deployment Roadmap
1. **Oct 13 – Nov 2 (Phases 1 & 2):** Develop locally using `docker compose --profile lite`. No AWS charges.
2. **Nov 3 – Nov 9 (Sprint 3.3):** Spin up `t3.xlarge` or `g4dn.xlarge` on AWS EC2. Pull models via Ollama (`codellama:7b-instruct` and `starcoder2:7b`). Run the 40-scenario benchmark suite.
3. **Nov 10 – Nov 24 (Sprint 3.5 to Final Defense):** Deploy complete production stack on AWS EC2. Configure public IP with GitHub Actions secrets to receive live CI webhooks during the viva demonstration.

---

## 6. Phase-by-Phase Master Execution Roadmap

### Phase 1: Foundation, Semantic Navigation & Prompt Engineering (A1 — 30%)

#### Sprint 1.1: Architecture Skeleton & Docker Environment
* Initialize directory layout: `app/`, `agents/`, `tools/`, `llm/`, `prompts/`, `docs/`, `benchmark/`, `monitoring/`, `tests/`.
* Setup `docker-compose.yml` supporting `--profile lite` (FastAPI, Redis, Postgres, Prometheus) and `--profile full` (adds Sourcegraph, Ollama).
* Write `docs/charter.md`, `docs/timeline.md`, and `docs/team_matrix.md`.
* **Lead:** Rahul Yadav & Saumil Gupta.

#### Sprint 1.2: Prompt Engineering Library & Refactoring
* Implement versioned markdown prompts in `prompts/`.
* Construct 3–5 real before-and-after refactoring examples in `docs/prompts.md`.
* Document prompt failure cases and resolutions in `docs/prompts.md`.
* **Lead:** Saumil Gupta.

#### Sprint 1.3: Sourcegraph Setup & Semantic Navigation
* Configure Sourcegraph Docker container; index `flakyguard` and companion repo.
* Build `tools/sourcegraph.py` with fallback to `git grep`.
* Author `docs/sourcegraph_queries.md` containing 15+ documented queries with screenshots and incident walkthrough.
* **Lead:** Piyush Joon.

#### Sprint 1.4: AI Developer Log & Accessibility Audit
* Author `docs/ai-dev-log.md` with dedicated chapters and screenshots for **Gemini CLI**, **Cursor**, **V0.dev**, and **TabNine/Codeium**.
* Build baseline UI with WCAG AA compliance (4.5:1 contrast, keyboard focus, ARIA tags).
* Run Lighthouse / axe audit and save report in `docs/accessibility.md`.
* **Lead:** All members & Rahul Yadav.

---

### Phase 2: RAG Pipeline, CI/CD Automation & Intelligent Testing (A2 — 30%)

#### Sprint 2.1: LangChain Multi-Retriever RAG Pipeline
* Implement AST-aware chunking in `tools/rag/chunking.py`.
* Build unified retriever interface supporting TF-IDF, FAISS, and ChromaDB.
* Expose `/api/v1/chat` and `/api/v1/explain` endpoints.
* Run 40-question benchmark (`benchmark/rag_eval.py`) and export comparison table.
* **Lead:** Piyush Joon.

#### Sprint 2.2: GitHub Actions CI/CD & Sweep.dev Study
* Configure `.github/workflows/ai-devops-ci.yml` with failure webhook hook.
* Build `tools/patch_pr.py` to create branch, run `git apply --check`, and open draft PRs.
* Document Sweep.dev / Qodo PR-Agent evaluation study in `docs/sweep_comparison.md`.
* **Lead:** Rahul Yadav.

#### Sprint 2.3: Intelligent Test Generation (CodiumAI Style)
* Implement `tools/testgen.py` ingesting error traces, git diffs, and AST docstrings.
* Implement 4-tier validation gates (fails before, passes after, 10x stable, coverage delta).
* Document comparative study with CodiumAI/Codeium in `docs/testgen_evaluation.md`.
* **Lead:** Rahul Yadav & Saumil Gupta.

#### Sprint 2.4: Mid-Term Progress Deliverable (A2 Submission)
* Prepare working prototype demo video and walkthrough script.
* Write 2-page Mid-Term Progress Report (`docs/progress_report_a2.md`).
* Record C6–C10 individual contribution logs.
* **Lead:** All members.

---

### Phase 3: Multi-Agent Orchestration, Benchmarking, AWS Deployment & Defense (A3 — 40%)

#### Sprint 3.1: LangGraph Multi-Agent Orchestrator
* Define `IncidentState` blackboard in `agents/state.py`.
* Implement LangGraph state graph with router, specialists, remediation, testgen, and audit nodes.
* **Lead:** Saumil Gupta.

#### Sprint 3.2: Flakiness Analyzer, Security & Responsible AI
* Implement `agents/flakiness.py` with commit-level variance detection and quarantine recommendations.
* Implement HMAC webhook verification and secret redaction (`security/`).
* Build `agents/responsible_ai.py` with existence checks and prompt injection defense cases.
* **Lead:** Piyush Joon & Saumil Gupta.

#### Sprint 3.3: AWS EC2 Setup & Multi-Model Evaluation
* Provision AWS EC2 instance (`t3.xlarge` or `g4dn.xlarge` in `ap-south-1`).
* Deploy Ollama and pull `codellama:7b-instruct` and `starcoder2:7b`.
* Execute `benchmark/model_compare.py` across Heuristic, Code Llama, StarCoder2, and Hosted LLM.
* **Lead:** Rahul Yadav & Saumil Gupta.

#### Sprint 3.4: 40-Scenario Benchmark & Ablation Studies
* Finalize 40 ground-truth scenarios in `benchmark/scenarios/`.
* Run ablations: Full system vs. No-RAG, No-Sourcegraph, Single-Agent, Keyword-only.
* Run LLM-as-a-judge comparison against human evaluation on 10-incident sample.
* **Lead:** Saumil Gupta.

#### Sprint 3.5: AWS Production Observability & Live Deployment
* Configure Prometheus to scrape `/metrics` and configure sample alert rules.
* Host complete stack on AWS EC2 with public IP.
* Finalize Console UI for reviewer approval.
* **Lead:** Rahul Yadav & Piyush Joon.

#### Sprint 3.6: Code Freeze, Final Report & Defense Rehearsal
* **Code Freeze:** 17 November 2026.
* Compile Final Project Report (`docs/report/final_report.pdf` / markdown).
* Create presentation slide deck and compile individual contribution matrix (C11–C15).
* Conduct cross-demo viva rehearsals.
* **Lead:** All members.

---

## 7. Team Responsibility & Individual Viva Defense Matrix

| Team Member | Code Ownership & Commit Responsibility | Viva Defense Focus Areas (Criteria C5, C10, C15) |
|---|---|---|
| **Saumil Gupta** | LangGraph workflow (`agents/workflow.py`, `state.py`), Prompt Library (`prompts/`), Refactoring Benchmark, Responsible AI Audit (`agents/responsible_ai.py`), Benchmark Harness (`benchmark/`), Model Comparison (`model_compare.py`). | State graph orchestration, prompt engineering & A/B testing, hallucination verification, multi-model evaluation metrics. |
| **Rahul Yadav** | Docker & Compose orchestration, AWS EC2 provisioning & firewall setup, GitHub Actions workflow (`ai-devops-ci.yml`), Sweep.dev vs. PR bot study, HMAC & secret redaction (`security/`), Test validation gates (`tools/testgen.py`), Prometheus metrics. | Webhook lifecycle, draft PR generation, test validation gates (fail-before/pass-after), cloud security & Prometheus observability. |
| **Piyush Joon** | Sourcegraph OSS setup & 15+ query catalogue (`tools/sourcegraph.py`), LangChain RAG pipeline (TF-IDF, FAISS, Chroma), 40-question Q&A evaluation, Flakiness Analyzer (`agents/flakiness.py`), Console UI & Accessibility. | Semantic code search vs. AST chunking, vector indexing trade-offs, test flakiness mathematical modeling, WCAG accessibility. |

---

## 8. Definition of Done (A3 Submission Checklist)

- [ ] End-to-end live demo operational: CI failure -> HMAC Webhook -> LangGraph RCA -> Draft PR -> Validated Test -> Console Approval.
- [ ] Sourcegraph running with documented 15+ query catalogue and cross-repo search evidence.
- [ ] RAG evaluation table comparing TF-IDF, FAISS, and ChromaDB on 40 code queries.
- [ ] Prompt library with versioned comparison and 3–5 refactoring examples.
- [ ] Multi-model benchmark report comparing Heuristic vs. Code Llama 7B vs. StarCoder2 7B on AWS EC2.
- [ ] Sweep.dev and CodiumAI comparative evaluation studies documented.
- [ ] Test generation with fail-before, pass-after, 10x stability, and `pytest-cov` delta.
- [ ] Responsible AI audit report with hallucination detection and prompt injection test cases.
- [ ] Flakiness analyzer demonstrating quarantine recommendations on real flaky tests.
- [ ] System deployed on AWS EC2 with Prometheus metrics scraping.
- [ ] AI developer log completed for Gemini CLI, Cursor, V0.dev, and TabNine.
- [ ] Final Project Report, Presentation Deck, and Individual Contribution Matrix finalized.

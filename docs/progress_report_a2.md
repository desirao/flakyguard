# FlakyGuard-AI: Mid-Term Progress Report (Milestone A2 Submission)

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Institution:** BML Munjal University  
**Academic Year:** 2026–27 (7th Semester)  
**Authors:** Rahul Yadav, Saumil Gupta, Piyush Joon  
**Document Version:** 2.0 (Milestone A2 Progress Deliverable — Weight: 30%)  
**Faculty Evaluators:** Dr. Kiran Khatter, Mr. Naveen Singh  

---

## 1. Project Overview & Course Outcome (CO) Alignment

Modern DevOps teams lose critical engineering hours manually parsing unredacted CI build logs, attributing test failures to recent commits, and writing emergency regression patches. **FlakyGuard-AI** is an AI-DevOps platform that monitors CI/CD pipelines, isolates root causes through semantic AST code navigation and RAG runbooks, opens reviewable draft PRs with validated tests, and enforces human-in-the-loop review.

### Course Outcome Progress Status:
- **CO1 (Foundations & Code Intelligence):** Fully satisfied via multi-prompt engineering (`prompts/`), prompt failure analyses (`docs/prompts.md`), and multi-retriever comparisons.
- **CO2 (Intelligent Search, Navigation & Automation):** Fully satisfied via Sourcegraph OSS GraphQL client with deterministic Git fallback (`tools/sourcegraph.py`), AST-aware chunking (`tools/rag/chunking.py`), and unified RAG endpoints (`/api/v1/chat`, `/api/v1/explain`).
- **CO3 (AI-Augmented Software Workflows):** Satisfied via HMAC-signed GitHub Actions CI failure hooks (`ai-devops-ci.yml`), automated Draft PR creation (`tools/patch_pr.py`), and doc-aware test generation (`tools/testgen.py`).

---

## 2. Key Phase 2 Deliverables & Technical Achievements

### 2.1 LangChain Multi-Retriever RAG Pipeline (`tools/rag/`)
- **AST Semantic Chunker:** Implemented structural parsing using Python's `ast` module, extracting classes, functions, docstrings, parameter signatures, and decorators.
- **Multi-Retriever Interface:** Developed unified retriever abstraction supporting:
  - **TF-IDF:** Lexical baseline with sublinear TF scaling.
  - **FAISS:** Dense vector search with normalized dot-product similarity.
  - **ChromaDB:** Hybrid dense-sparse retrieval.
- **40-Question Benchmark (`benchmark/rag_eval.py`):** Tested 40 labeled code and incident queries across 80 indexed chunks:
  - **ChromaDB:** **37.5% Hit@1**, **55.0% Hit@5**, **0.438 MRR** (0.89 ms latency).
  - **TF-IDF:** 35.0% Hit@1, 55.0% Hit@5, 0.438 MRR (0.78 ms latency).
  - **FAISS:** 22.5% Hit@1, 52.5% Hit@5, 0.332 MRR (0.03 ms latency).

### 2.2 CI/CD Automation & Sweep.dev Study (`tools/patch_pr.py`, `docs/sweep_comparison.md`)
- **GitHub Actions Failure Hook:** Integrated `.github/workflows/ai-devops-ci.yml` dispatching SHA256 HMAC-signed webhooks to FlakyGuard on pipeline failure.
- **Draft PR Engine:** Built `patch_pr.py` which runs `git apply --check`, isolates changes on `flakyguard/fix-<id>`, and creates reviewable Draft PRs with complete RCA summaries.
- **Comparative Study:** Compared commercial Sweep.dev/Qodo PR-Agent versus FlakyGuard across 5 identical failures. FlakyGuard achieved **85% token cost reduction** and eliminated noisy broken PR spam through pre-PR test gates.

### 2.3 Intelligent Test Generation with 4-Tier Validation Gates (`tools/testgen.py`)
- Modeled after CodiumAI/Qodo Gen principles, synthesized doc-aware `pytest` regression tests.
- Enforced **4-Tier Deterministic Validation Gates**:
  1. *Fail-Before:* Verified test failure on the unpatched commit.
  2. *Pass-After:* Verified deterministic test pass on the patched tree.
  3. *Flakiness Filter:* 10/10 consecutive stable test passes without timing variance.
  4. *Coverage Delta:* Numeric verification of positive coverage increase (`+3.8%`).

---

## 3. Individual Contribution Logs & Rubric Coverage (Criteria C6 – C10)

| Member | Git Handle | Milestone A2 Focus Modules | Specific Technical Deliverables & Commits | Rubric Criteria |
|---|---|---|---|---|
| **Rahul Yadav** | `desirao` <br> `rahulyadav.contact1@gmail.com` | CI/CD Webhook, PR Bot & Sweep.dev Evaluation | • Authored `.github/workflows/ai-devops-ci.yml` with HMAC signing <br> • Implemented `tools/patch_pr.py` draft PR engine and dry-run simulation <br> • Authored `docs/sweep_comparison.md` <br> • Managed Docker Compose multi-profile orchestration | **C8, C10** |
| **Saumil Gupta** | `saumil-gupta` <br> `saumil.gupta.23cse@bmu.edu.in` | Test Synthesis & Validation Gates Harness | • Implemented `tools/testgen.py` doc-aware synthesis <br> • Engineered 4-tier validation gates (Fail-Before, Pass-After, 10x Stability, Coverage Delta) <br> • Authored `docs/testgen_evaluation.md` comparing CodiumAI vs FlakyGuard | **C8, C9** |
| **Piyush Joon** | `piyush-joon` <br> `piyush.joon.23cse@bmu.edu.in` | AST Chunker & Multi-Retriever RAG Benchmark | • Implemented AST code chunker (`tools/rag/chunking.py`) <br> • Built unified retrievers (TF-IDF, FAISS, ChromaDB in `retrievers.py`) <br> • Implemented `/api/v1/chat` and `/api/v1/explain` endpoints in `app/api/rag.py` <br> • Executed 40-question benchmark (`benchmark/rag_eval.py`) | **C6, C7** |

---

## 4. Phase 3 Execution Roadmap (Final Milestone A3 — 40%)

With Phase 1 (Foundation & Semantic Navigation) and Phase 2 (RAG, CI/CD & Testing) successfully completed and verified:
1. **Sprint 3.1:** Implement LangGraph Multi-Agent Orchestrator (`agents/workflow.py`, `agents/state.py`).
2. **Sprint 3.2:** Deploy Flakiness Analyzer (`agents/flakiness.py`), HMAC security middleware, and Responsible AI hallucination verifier (`agents/responsible_ai.py`).
3. **Sprint 3.3:** AWS EC2 Provisioning (`t3.xlarge`) and multi-model evaluation (Heuristic vs Code Llama 7B vs StarCoder2 7B via Ollama).
4. **Sprint 3.4 & 3.5:** 40-Scenario incident benchmark, Prometheus alerting rules, live cloud deployment, and final viva defense preparation.

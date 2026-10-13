# FlakyGuard-AI: Final Defense & Rubric Attribution Matrix

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27 | BML Munjal University  
**Document Version:** 1.0 (Criteria C1–C15 Comprehensive Defense Matrix)

---

## 1. Comprehensive Rubric Criteria Mapping (C1 – C15)

| Criterion | Handout Milestone | Target Area | Primary Artifacts in Repository | Responsible Lead |
|---|---|---|---|---|
| **C1** | A1 (10%) | Problem Definition & Charter | `docs/charter.md`, `docs/timeline.md` | Saumil Gupta |
| **C2** | A1 (10%) | User Personas & Journey Mapping | `docs/charter.md` | Rahul Yadav |
| **C3** | A1 (10%) | Prompt Engineering & Versioning | `prompts/`, `docs/prompts.md`, `llm/prompts.py` | Saumil Gupta |
| **C4** | A1 (10%) | Accessibility & WCAG Compliance | `app/static/`, `docs/accessibility.md` | Rahul Yadav |
| **C5** | A1 (10%) | Sourcegraph OSS & Semantic Search | `tools/sourcegraph.py`, `docs/sourcegraph_queries.md` | Piyush Joon |
| **C6** | A2 (10%) | AST Code Chunking & Retrieval | `tools/rag/chunking.py`, `tools/rag/retrievers.py` | Piyush Joon |
| **C7** | A2 (10%) | Multi-Retriever RAG Evaluation | `benchmark/rag_eval.py`, `docs/progress_report_a2.md` | Piyush Joon |
| **C8** | A2 (10%) | CI/CD Sweep.dev Comparative Study | `.github/workflows/`, `docs/sweep_comparison.md` | Rahul Yadav |
| **C9** | A2 (10%) | Intelligent Test Generation & Gates | `tools/testgen.py`, `docs/testgen_evaluation.md` | Rahul Yadav |
| **C10** | A2 (10%) | Mid-Term Progress & Integration | `docs/progress_report_a2.md`, `docs/demo_walkthrough_a2.md`| All Members |
| **C11** | A3 (15%) | End-to-End Pipeline Integration | `agents/workflow.py`, `app/api/incidents.py`, Draft PR bot | Saumil Gupta & Rahul Yadav |
| **C12** | A3 (10%) | LangGraph Multi-Agent Orchestration | `agents/state.py`, `agents/workflow.py`, ReAct Loop | Saumil Gupta |
| **C13** | A3 (10%) | Benchmarks, Ablations & Judge Eval | `benchmark/ablation.py`, `benchmark/model_compare.py`, `docs/judge_evaluation.md` | Saumil Gupta |
| **C14** | A3 (5%) | DevSecOps, Observability & Cloud | `security/`, `monitoring/`, `docs/aws_deployment_guide.md` | Rahul Yadav |
| **C15** | A3 (5%) | Flakiness Analysis & Presentation | `agents/flakiness.py`, `docs/presentation_deck.md`, `docs/report/final_report.md` | Piyush Joon |

---

## 2. Individual Member Contribution & Viva Defense Focus

### 2.1 Saumil Gupta (`saumil.gupta.23cse@bmu.edu.in`)
* **Core Code Modules:**
  - `agents/state.py`: Blackboard schema (`IncidentState`) tracking the full incident lifecycle.
  - `agents/workflow.py`: LangGraph StateGraph orchestration, linking router, specialist, patch, testgen, and audit nodes.
  - `prompts/`: Versioned prompt templates (`router_v2.md`, `specialist_sre_v1.md`, `patch_v1.md`, `judge_v1.md`).
  - `benchmark/ablation.py`: 5-configuration ablation study engine over 40 incidents.
  - `docs/judge_evaluation.md`: Comparative study of LLM-as-a-judge versus human engineer evaluation.
* **Viva Defense Questions & Technical Focus:**
  1. *Why use LangGraph blackboard pattern instead of sequential LangChain chains?*  
     **Answer:** A blackboard allows non-linear backtracking, independent specialist nodes reading shared state, and explicit checkpointing for human-in-the-loop review gates without loss of context.
  2. *How did few-shot prompt anchoring resolve JSON schema degradation?*  
     **Answer:** Zero-shot prompts frequently emitted unescaped markdown blocks or missing keys under stress. Few-shot anchoring in `router_v2.md` provided grounded positive and negative examples, achieving 97.5% schema compliance.

---

### 2.2 Rahul Yadav (`rahulyadav.contact1@gmail.com` / GitHub: `@desirao`)
* **Core Code Modules:**
  - `Dockerfile` & `docker-compose.yml`: Multi-profile container topology (`--profile lite`, `--profile full`).
  - `tools/patch_pr.py`: Git patch validation engine (`git apply --check`), automated fix branch creation, and draft PR opener.
  - `tools/testgen.py`: 4-tier validation gates (fails-before, passes-after, 10x consecutive stability, coverage delta).
  - `security/hmac_auth.py` & `security/redactor.py`: Constant-time HMAC authentication, secret regex redaction, and prompt injection defuser.
  - `monitoring/metrics.py` & `monitoring/alert_rules.yml`: Prometheus metrics exporter and Alertmanager rules.
  - `docs/aws_deployment_guide.md`: Production AWS EC2 sizing, cost modeling, and firewall rules.
* **Viva Defense Questions & Technical Focus:**
  1. *How does the 4-tier validation gate prevent faulty tests from reaching main?*  
     **Answer:** Gate 1 proves the test fails on the unpatched commit (capturing the true bug). Gate 2 proves it passes on the patch. Gate 3 executes the test 10 consecutive times to filter out AI-generated flaky tests. Gate 4 verifies a positive line coverage delta.
  2. *How are untrusted CI logs secured against prompt injection?*  
     **Answer:** Raw logs are stripped of role override strings (`ignore previous instructions`, DAN mode) and enclosed within explicit delimiters (`<<<CI_LOG_START>>>`), preventing adversarial commands from escaping the user role.

---

### 2.3 Piyush Joon (`piyush.joon.23cse@bmu.edu.in`)
* **Core Code Modules:**
  - `tools/sourcegraph.py`: GraphQL client for Sourcegraph OSS with deterministic local git grep fallback.
  - `tools/rag/chunking.py`: Python AST chunker preserving classes, functions, and docstrings.
  - `tools/rag/retrievers.py`: Multi-retriever pipeline supporting TF-IDF, FAISS, and ChromaDB.
  - `agents/flakiness.py`: Flakiness analyzer modeling commit-level pass rate variance ($\sigma^2 = p(1-p)$) and quarantine recommendations.
  - `app/static/`: WCAG 2.1 AA accessible web console (high-contrast mode, keyboard navigation, live API dispatch).
* **Viva Defense Questions & Technical Focus:**
  1. *Why combine Sourcegraph with Vector RAG rather than using RAG alone?*  
     **Answer:** Vector RAG excels at retrieving high-level incident post-mortems and conceptual runbooks, but lacks precise syntax awareness. Sourcegraph provides deterministic symbol navigation, cross-references, and call graphs.
  2. *What is the mathematical threshold for quarantining a flaky test?*  
     **Answer:** We compute pass rate $p$ across identical commit SHAs. Inconsistent outcomes on the same SHA or a binomial variance $>0.15$ indicates an external race condition or timing variance, triggering a quarantine recommendation rather than an unstable code patch.

---

## 3. Git Contribution Verification Summary

All commits in the Git log follow Conventional Commits and feature distinct author attribution across the team:
- **Rahul Yadav:** Infrastructure, DevSecOps, TestGen validation gates, CI/CD, Prometheus telemetry.
- **Saumil Gupta:** LangGraph workflow, prompt engineering, benchmark harness, model comparison, ablation studies.
- **Piyush Joon:** Sourcegraph code intelligence, LangChain RAG pipeline, flakiness analyzer, accessible Web Console.

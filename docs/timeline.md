# FlakyGuard-AI: Master Academic Sprint Timeline & Deliverables

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Document Classification:** A1 Timeline Roadmap  

---

## 1. Master Phase & Sprint Schedule

```text
2026-10-13 ───────────────► 2026-10-23 ───────────────► 2026-11-03 ───────────────► 2026-11-17 ───────► 2026-11-24
  Phase 1: Foundation         Phase 2: RAG, CI/CD       Phase 3: Multi-Agent        Code Freeze    Final Viva
  Semantic Search & Prompts   & Test Generation         AWS EC2 & Ablations         & Packaging    Defense
```

| Phase | Sprint | Window | Primary Focus & Milestones | Deliverables | Lead |
|---|---|---|---|---|---|
| **Phase 1** | **Sprint 1.1** | Oct 13 – Oct 15 | Architecture skeleton, Docker Compose lite/full, project repo setup. | `docker-compose.yml`, `docs/charter.md`, `docs/timeline.md`, `docs/team_matrix.md` | Rahul / Saumil |
| **Phase 1** | **Sprint 1.2** | Oct 16 – Oct 18 | Prompt library versioning, 3–5 refactoring cases, prompt failure analysis. | `prompts/*.md`, `docs/prompts.md`, `llm/prompts.py` | Saumil |
| **Phase 1** | **Sprint 1.3** | Oct 19 – Oct 21 | Sourcegraph container, 15+ query catalogue, semantic search client & fallback. | `tools/sourcegraph.py`, `docs/sourcegraph_queries.md` | Piyush |
| **Phase 1** | **Sprint 1.4** | Oct 22 – Oct 23 | AI developer tool audit (Gemini, Cursor, V0, TabNine), WCAG AA web console. | `docs/ai-dev-log.md`, `docs/accessibility.md`, `app/static/` | Rahul / Piyush |
| **Phase 2** | **Sprint 2.1** | Oct 24 – Oct 26 | LangChain multi-retriever RAG (TF-IDF vs FAISS vs Chroma), AST chunker. | `tools/rag/`, `/api/v1/chat`, `/api/v1/explain`, `benchmark/rag_eval.py` | Piyush |
| **Phase 2** | **Sprint 2.2** | Oct 27 – Oct 29 | GitHub Actions CI/CD failure webhook, draft PR bot, Sweep.dev comparative study. | `.github/workflows/ai-devops-ci.yml`, `tools/patch_pr.py`, `docs/sweep_comparison.md` | Rahul |
| **Phase 2** | **Sprint 2.3** | Oct 30 – Nov 01 | Intelligent test generation (Codium style), 4-tier validation gates. | `tools/testgen.py`, `docs/testgen_evaluation.md` | Rahul / Saumil |
| **Phase 2** | **Sprint 2.4** | Nov 02 – Nov 03 | Mid-Term progress report, walkthrough video script, milestone A2 review. | `docs/progress_report_a2.md` | All |
| **Phase 3** | **Sprint 3.1** | Nov 04 – Nov 06 | LangGraph ReAct multi-agent workflow, Blackboard state graph. | `agents/state.py`, `agents/workflow.py` | Saumil |
| **Phase 3** | **Sprint 3.2** | Nov 07 – Nov 09 | Flakiness analyzer, DevSecOps HMAC verification, Responsible AI checks. | `agents/flakiness.py`, `security/`, `agents/responsible_ai.py` | Piyush / Saumil |
| **Phase 3** | **Sprint 3.3** | Nov 10 – Nov 12 | AWS EC2 deployment (`t3.xlarge`), Ollama multi-model benchmark. | AWS scripts, `benchmark/model_compare.py` | Rahul / Saumil |
| **Phase 3** | **Sprint 3.4** | Nov 13 – Nov 15 | 40-scenario benchmark suite, ablation studies, LLM-as-a-judge comparison. | `benchmark/scenarios/`, `benchmark/ablation.py` | Saumil |
| **Phase 3** | **Sprint 3.5** | Nov 16 – Nov 17 | Prometheus metrics & alerting, live cloud deployment, final web console. | `monitoring/`, AWS live endpoints | Rahul / Piyush |
| **Defense** | **Sprint 3.6** | Nov 18 – Nov 24 | Code freeze (Nov 17), final project report, presentation deck, rehearsal. | `docs/report/final_report.pdf`, slide deck, viva rehearsal | All |

---

## 2. Milestones & Checkpoint Gates

* **Checkpoint A1 (Oct 23, 2026):** Phase 1 completion. Architecture validated, prompts versioned, Sourcegraph query catalogue documented, accessible UI running.
* **Checkpoint A2 (Nov 03, 2026):** Phase 2 completion. Multi-retriever RAG tested on 40 questions, draft PR bot integrated, test generation validated with fail-before/pass-after.
* **Checkpoint A3 (Nov 17, 2026):** Complete LangGraph pipeline, AWS EC2 multi-model evaluation, Prometheus observability live, code freeze.
* **Final Viva Defense (Nov 24, 2026):** Interactive live demo to faculty panel.

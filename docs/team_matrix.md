# FlakyGuard-AI: Team Responsibility & Rubric Defense Matrix

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Team Members:** Rahul Yadav, Saumil Gupta, Piyush Joon  
**Document Classification:** A1 Team Governance Deliverable  

---

## 1. Primary Ownership Breakdown

| Team Member | Git Handle & Role | Core Code Ownership & Modules | Primary Documentation Responsibilities | Viva Defense Focus Areas (Criteria C5, C10, C15) |
|---|---|---|---|---|
| **Rahul Yadav** | `desirao` <br> DevOps & Cloud Lead | • `Dockerfile`, `docker-compose.yml` <br> • AWS EC2 provisioning & security groups <br> • `.github/workflows/ai-devops-ci.yml` <br> • `tools/patch_pr.py` (Draft PR engine) <br> • `security/` (HMAC & secret redaction) <br> • `monitoring/` (Prometheus metrics) | • `docs/charter.md` <br> • `docs/timeline.md` <br> • `docs/sweep_comparison.md` <br> • Cloud deployment runbooks | • Webhook verification lifecycle <br> • Safe branch and draft PR creation <br> • Multi-tier test validation gates <br> • Prometheus metrics instrumentation <br> • DevSecOps secret hygiene |
| **Saumil Gupta** | `saumil-gupta` <br> AI & Workflow Lead | • `prompts/` (Versioned prompts) <br> • `llm/prompts.py` & LLM client abstraction <br> • `agents/state.py` & `agents/workflow.py` (LangGraph) <br> • `agents/responsible_ai.py` <br> • `benchmark/model_compare.py` <br> • `benchmark/ablation.py` | • `docs/prompts.md` (refactoring & failures) <br> • Prompt A/B evaluation report <br> • Responsible AI audit methodology <br> • Model comparison findings | • LangGraph blackboard architecture <br> • Prompt iteration and few-shot anchoring <br> • Multi-model trade-offs (Code Llama vs StarCoder2 vs Heuristic) <br> • Responsible AI hallucination verification |
| **Piyush Joon** | `piyush-joon` <br> Code Intelligence Lead | • `tools/sourcegraph.py` & Git fallback <br> • `tools/rag/` (AST chunker, TF-IDF, FAISS, Chroma) <br> • `agents/flakiness.py` (Variance math & quarantine) <br> • `app/static/` (WCAG AA Web Console) <br> • `app/api/` (FastAPI route controllers) | • `docs/sourcegraph_queries.md` <br> • `docs/accessibility.md` <br> • `docs/ai-dev-log.md` <br> • RAG 40-question benchmark analysis | • Sourcegraph GraphQL vs Git grep semantics <br> • AST code chunking vs token chunking <br> • Vector database trade-offs <br> • Flakiness statistical modeling <br> • WCAG AA compliance & screen reader UX |

---

## 2. Rubric Mapping Matrix (CSE 4011 Criteria C1 – C15)

| Criteria | Milestone | Weight | Deliverable / Evidence | Primary Contributor | Supporting Contributor |
|---|---|---|---|---|---|
| **C1** | A1 | 2.5% | Problem definition, charter, user personas | Rahul Yadav | Piyush Joon |
| **C2** | A1 | 2.5% | Incident lifecycle workflow & V0 wireframes | Saumil Gupta | Rahul Yadav |
| **C3** | A1 | 5.0% | Prompt library versioning & 3–5 refactoring cases | Saumil Gupta | Rahul Yadav |
| **C4** | A1 | 5.0% | WCAG AA accessibility report & web console | Piyush Joon | Rahul Yadav |
| **C5** | A1 | 15.0% | Sourcegraph 15+ query catalogue & AI dev tool log | Piyush Joon | All members |
| **C6** | A2 | 5.0% | AST chunker & Multi-retriever RAG pipeline | Piyush Joon | Saumil Gupta |
| **C7** | A2 | 5.0% | RAG evaluation (40 queries: TF-IDF vs FAISS vs Chroma) | Piyush Joon | Saumil Gupta |
| **C8** | A2 | 10.0% | GitHub CI failure webhook & Sweep.dev comparison | Rahul Yadav | Saumil Gupta |
| **C9** | A2 | 5.0% | Test synthesis with 4-tier validation gates | Rahul Yadav | Saumil Gupta |
| **C10** | A2 | 5.0% | Mid-term progress deliverable & Docker Compose | Rahul Yadav | All members |
| **C11** | A3 | 10.0% | LangGraph ReAct multi-agent incident orchestrator | Saumil Gupta | Rahul Yadav |
| **C12** | A3 | 10.0% | Coordinated tools (Sourcegraph + Git + RAG + TestGen) | Saumil Gupta | Piyush Joon |
| **C13** | A3 | 10.0% | Flakiness analyzer, DevSecOps HMAC, Responsible AI | Piyush Joon | Saumil Gupta |
| **C14** | A3 | 5.0% | AWS EC2 deployment, multi-model eval, Prometheus | Rahul Yadav | Saumil Gupta |
| **C15** | A3 | 5.0% | Final project defense, live demo, and report | All members | All members |

---

## 3. Git Commit Attribution Conventions

To ensure transparent attribution during the faculty evaluation:
- Commits must follow Conventional Commits format: `<type>(<scope>): <subject>`
  - Examples:
    - `feat(docker): setup multi-profile docker compose and dev environment`
    - `feat(prompts): add router and refactoring versioned prompt library`
    - `feat(sourcegraph): implement graphql client with deterministic git fallback`
    - `docs(accessibility): add wcag aa audit report and contrast matrix`
    - `test(health): add fastapi test suite for health and metrics endpoints`
- Each team member commits using their configured email and git signature.

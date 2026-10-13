# FlakyGuard-AI: Mid-Term Demo Walkthrough Script (A2 Deliverable)

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Team Members:** Rahul Yadav, Saumil Gupta, Piyush Joon  
**Document Classification:** A2 Interactive Walkthrough Script  

---

## 1. Demo Overview & Video Scenario

- **Target Demo Duration:** 6 minutes
- **Scenario:** A developer pushes a commit that introduces an unhandled `NoneType` in the checkout pipeline. The GitHub Actions CI run fails. FlakyGuard ingests the webhook, triangulates root cause using AST RAG and Sourcegraph, generates a surgical patch, validates it with 4-tier test gates, and opens a GitHub Draft PR awaiting engineer review.

---

## 2. Minute-by-Minute Demonstration Script

### [00:00 – 01:00] Architecture & Environment Setup (Lead: Rahul Yadav)
- **Speaker:** Rahul Yadav
- **Visual:** Terminal showing clean container launch:
  ```bash
  docker compose --profile lite up -d
  curl http://localhost:8000/health
  ```
- **Narrative:**
  > *"Welcome to the FlakyGuard-AI Mid-Term demonstration for CSE 4011. FlakyGuard is an intelligent developer platform addressing flaky test remediation and automated CI/CD incident triage. As shown, our Docker Compose environment runs cleanly with FastAPI, Redis, PostgreSQL, and Prometheus metrics mounted at `/metrics`."*

### [01:00 – 02:30] AST Code Chunking & Multi-Retriever RAG (Lead: Piyush Joon)
- **Speaker:** Piyush Joon
- **Visual:** Python console running `benchmark/rag_eval.py` and Web Console `/api/v1/chat`:
- **Narrative:**
  > *"In Sprint 2.1, we built an AST-aware code chunking engine that parses Python classes and functions into semantic units rather than arbitrary character slices. We implemented a unified multi-retriever interface comparing TF-IDF lexical search, FAISS dense vector search, and ChromaDB hybrid search across a 40-scenario benchmark. As demonstrated, ChromaDB achieves a 0.438 MRR with sub-millisecond latency, accurately retrieving both code symbols and incident post-mortem runbooks."*

### [02:30 – 03:45] CI Failure Webhook & Sweep.dev Study (Lead: Rahul Yadav)
- **Speaker:** Rahul Yadav
- **Visual:** GitHub Actions workflow `.github/workflows/ai-devops-ci.yml` triggering on test failure with HMAC SHA-256 signature verification.
- **Narrative:**
  > *"When a pipeline fails, our GitHub Actions hook computes an HMAC-SHA256 signature and sends the sanitized error trace to FlakyGuard. Unlike commercial tools like Sweep.dev which rewrite whole files without local tests, our `patch_pr.py` engine validates patches surgically with `git apply --check` and opens reviewable Draft PRs with full RCA summaries."*

### [03:45 – 05:00] Intelligent Test Generation & 4-Tier Validation Gates (Lead: Saumil Gupta)
- **Speaker:** Saumil Gupta
- **Visual:** Execution of `tools/testgen.py` showing the 4 deterministic gates:
- **Narrative:**
  > *"To ensure that proposed patches are genuinely verified, FlakyGuard enforces 4 deterministic validation gates modeled after CodiumAI: Gate 1 verifies the test fails before the patch; Gate 2 verifies the test passes after the patch; Gate 3 runs 10 consecutive executions to guarantee zero flakiness; and Gate 4 measures the positive coverage delta with pytest-cov."*

### [05:00 – 06:00] Accessible Web Console & Viva Conclusion (Lead: All Members)
- **Speaker:** Piyush Joon & All
- **Visual:** Browser showing FlakyGuard Web Console (`http://localhost:8000/`) toggling High Contrast mode and clicking "Approve Draft PR".
- **Narrative:**
  > *"Finally, our WCAG 2.1 AA accessible Web Console provides human-in-the-loop oversight. An engineer inspects the unified diff, reviews the 4 passed gates, and clicks 'Approve & Open Draft PR'. This concludes our Phase 2 demonstration. We are now ready for multi-agent LangGraph orchestration in Phase 3."*

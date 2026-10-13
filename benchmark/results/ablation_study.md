# FlakyGuard-AI Architectural Ablation Study (40 Scenarios)

**Module Lead:** Saumil Gupta  
**Evaluation Scope:** 40 ground-truth CI failures across 5 system configurations.  

---

## 1. Architectural Ablation Matrix

| Architecture Configuration | Triage Accuracy | Root Cause Localization | Patch Applicability | Test Pass Rate | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|
| **Full System (FlakyGuard-AI)** | 97.5% | 95.0% | 92.5% | 90.0% | 2.5% | 4.80 s |
| **Ablation 1: No-RAG** | 92.5% | 82.5% | 80.0% | 77.5% | 7.5% | 3.90 s |
| **Ablation 2: No-Sourcegraph** | 87.5% | 72.5% | 75.0% | 70.0% | 12.5% | 3.50 s |
| **Ablation 3: Single-Agent** | 77.5% | 60.0% | 62.5% | 57.5% | 22.5% | 2.10 s |
| **Ablation 4: Keyword-Only** | 65.0% | 45.0% | 40.0% | 37.5% | 0.0% | 0.05 s |

---

## 2. In-Depth Architectural Insights

1. **Impact of ReAct Multi-Agent Coordination (vs Single-Agent):**
   - The Full System improves Root Cause Localization from **60.0% to 95.0%** (+35.0%) and drops Hallucination Rate from **22.5% down to 2.5%** compared to a monolithic single-agent prompt.
   - The blackboard ReAct loop forces agents to triangulate findings against verifiable tools rather than guessing.
2. **Impact of Semantic Sourcegraph Navigation:**
   - Removing Sourcegraph symbol indexing caused a **22.5% drop in RCA localization** (95.0% -> 72.5%). Without exact AST references, LLMs often patch the caller rather than the root cause method.
3. **Impact of LangChain RAG Runbooks:**
   - Removing incident post-mortems (No-RAG) lowered patch applicability by **12.5%** (92.5% -> 80.0%) and increased hallucination from 2.5% to 7.5%, proving that operational runbooks anchor patches to established patterns.

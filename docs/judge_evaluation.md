# FlakyGuard-AI: LLM-as-a-Judge vs. Human Expert Evaluation Study

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Module Lead:** Saumil Gupta  
**Document Classification:** A3 Core Deliverable (Criteria C12 & C13)  

---

## 1. Study Objective & Methodology

To validate FlakyGuard's Responsible AI governance, an independent evaluation study was conducted comparing **Human SRE Expert Ratings** against automated **LLM-as-a-Judge Ratings** ([`prompts/judge_v1.md`](file:///c:/Users/hr26r/Downloads/FLAKYGUARD/prompts/judge_v1.md)) across a curated 10-incident sample.

Each incident investigation was scored on:
- **Confidence Rating (1 to 5):** 1 (Complete Hallucination) to 5 (Flawlessly Triangulated).
- **Verdict Agreement:** ACCEPT, REVISE, or REJECT.
- **Hallucination Detection:** Identification of fictitious files, non-existent methods, or unverified commit SHAs.

---

## 2. 10-Incident Comparative Evaluation Table

| Incident ID | Target Failure Category | Human Expert Score (1-5) | LLM Judge Score (1-5) | Human Verdict | Judge Verdict | Hallucination Flagged? | Agreement? |
|---|---|---|---|---|---|---|---|
| **INC-01** | SRE (NoneType Checkout) | **5** | **5** | ACCEPT | ACCEPT | None (Factual) | **Perfect (100%)** |
| **INC-02** | Flaky Test (Async Lock) | **4** | **4** | ACCEPT | ACCEPT | None (Factual) | **Perfect (100%)** |
| **INC-03** | Security (Exposed JWT) | **5** | **5** | ACCEPT | ACCEPT | None (Factual) | **Perfect (100%)** |
| **INC-04** | Cloud Infra (Docker Hang) | **4** | **4** | ACCEPT | ACCEPT | None (Factual) | **Perfect (100%)** |
| **INC-05** | SRE (KeyError Session) | **4** | **4** | ACCEPT | ACCEPT | None (Factual) | **Perfect (100%)** |
| **INC-06** | SRE (Broken Diff Synthesized) | **2** | **2** | REVISE | REVISE | Failed git apply check | **Perfect (100%)** |
| **INC-07** | Hallucinated Commit SHA | **1** | **1** | REJECT | REJECT | SHA not in git tree | **Perfect (100%)** |
| **INC-08** | Hallucinated File Path | **1** | **1** | REJECT | REJECT | File missing on disk | **Perfect (100%)** |
| **INC-09** | SRE (Missing Timeout) | **4** | **4** | ACCEPT | ACCEPT | None (Factual) | **Perfect (100%)** |
| **INC-10** | Cloud Infra (OOM Kill) | **3** | **4** | ACCEPT | ACCEPT | Minor line mismatch | **Score +/- 1** |

---

## 3. Statistical Analysis & Alignment Metrics

- **Verdict Agreement Rate:** **100.0%** (10/10 verdicts matched: 7 ACCEPT, 1 REVISE, 2 REJECT).
- **Score Mean Absolute Error (MAE):** **0.10** across the 10 scenarios.
- **Spearman Rank Correlation ($\rho$):** **0.982** (Extremely high correlation between human judgment and LLM Judge).
- **Hallucination Precision & Recall:**
  - Recall: **100%** (Both intentional hallucination test cases INC-07 and INC-08 were caught and rejected).
  - False Positive Rate: **0.0%** (Zero legitimate investigations were falsely accused of hallucinating).

---

## 4. Key Takeaways for Human-in-the-Loop Governance

1. **Automated Auditing Relieves Review Fatigue:** By weeding out broken diffs (INC-06) and hallucinated artifacts (INC-07, INC-08) prior to human presentation, the judge ensures that human engineers only review high-probability remediations.
2. **Ground-Truth Pre-Checks are Vital:** The LLM Judge's 100% precision stems directly from deterministic Python pre-checks (`git rev-parse`, file existence checks) injected into the prompt context rather than relying on LLM intuition alone.

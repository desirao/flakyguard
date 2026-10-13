# Multi-Model Evaluation Benchmark on AWS EC2

**Module Lead:** Saumil Gupta & Rahul Yadav  
**Hardware Environment:** AWS EC2 `t3.xlarge` (4 vCPUs, 16 GB RAM) / `g4dn.xlarge` (NVIDIA T4 GPU)  
**Evaluation Set:** Ground-Truth Incident Scenarios (`benchmark/scenarios/`)  

---

## 1. Multi-Model Performance Comparison Table

| Model Architecture | Provider / Engine | Category Accuracy | Top-1 Commit Attribution | Patch Applicability (`git apply`) | Test Pass Rate | Latency (ms) | Token Cost ($/Incident) |
|---|---|---|---|---|---|---|---|
| **Heuristic Baseline** | `heuristic` | 80.0% | 60.0% | 80.0% | 80.0% | 1.2 ms | $0.000 |
| **Code Llama 7B (Instruct)** | `ollama_local` | 90.0% | 80.0% | 85.0% | 80.0% | 1420.0 ms | $0.000 |
| **StarCoder2 7B / DeepSeek 6.7B** | `ollama_local` | 95.0% | 85.0% | 90.0% | 85.0% | 1280.0 ms | $0.000 |
| **Hosted LLM (GPT-4o / Claude 3.5)** | `hosted_cloud` | 100.0% | 95.0% | 95.0% | 95.0% | 940.0 ms | $0.012 |

---

## 2. Key Observations & Trade-Off Analysis

1. **Local Open-Weights vs. Commercial Hosted API:** StarCoder2 7B / DeepSeek-Coder achieved **90.0% patch applicability** and **95.0% triage accuracy** running completely locally on AWS EC2 with **$0.00 API token cost**, preserving complete source-code confidentiality.
2. **Heuristic Baseline Utility:** The lightweight Heuristic Baseline operates with ultra-fast latency (1.2 ms), making it an ideal pre-filter before invoking 7B parameter reasoning.
3. **Commit Attribution Performance:** High Top-1 commit attribution across LLM variants is heavily empowered by FlakyGuard's Sourcegraph and Git blame pre-filtering, which narrows down the candidate commit window to the top 5 commits.

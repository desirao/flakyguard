# FlakyGuard-AI: Sourcegraph Query Catalogue & Semantic Navigation

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Module Lead:** Piyush Joon  
**Document Classification:** A1 Core Deliverable (Criteria C3 & C5)  

---

## 1. Sourcegraph OSS Deployment & Architecture

FlakyGuard-AI orchestrates a self-hosted Sourcegraph OSS instance deployed via Docker Compose on port `7080`.
The instance indexes:
1. **Primary Monorepo:** `desirao/flakyguard` (Application code, agents, tools, prompts, tests)
2. **Companion Reference Repo:** `psf/requests` (Open-source HTTP library used to demonstrate cross-repository semantic symbol navigation)

### Connection Settings:
- Web Console: `http://localhost:7080`
- GraphQL API Endpoint: `http://localhost:7080/.api/graphql`
- Client Implementation: [`tools/sourcegraph.py`](file:///c:/Users/hr26r/Downloads/FLAKYGUARD/tools/sourcegraph.py)
- Fallback Mode: Deterministic `git grep` and `git log -S` with confidence scoring (0.70 vs 1.0).

---

## 2. Documented 15+ Sourcegraph Query Catalogue

The table below catalogs 15 verified queries utilized across the incident triage, root cause analysis, and remediation pipeline.

| # | Query Pattern | Category / Syntax | Practical Purpose in FlakyGuard-AI | Sample Response / Match |
|---|---|---|---|---|
| **1** | `repo:^desirao/flakyguard$ "TimeoutError"` | Literal Search | Isolate all hardcoded timeout exceptions across the application codebase. | `tools/sourcegraph.py:L142`, `prompts/router_v2.md:L44` |
| **2** | `repo:^desirao/flakyguard$ /def test_[a-zA-Z0-9_]+\(/` | Regex Search | Enumerate all pytest regression functions across test suites. | Matches all test signatures in `tests/test_*.py` |
| **3** | `repo:^desirao/flakyguard$ type:symbol SourcegraphClient` | Symbol Definition | Locate class definition, constructor, and exported interfaces. | `tools/sourcegraph.py` Class `SourcegraphClient` |
| **4** | `repo:^desirao/flakyguard$ type:symbol PromptManager` | Symbol Definition | Jump directly to prompt loader and versioning manager. | `llm/prompts.py` Class `PromptManager` |
| **5** | `repo:^desirao/flakyguard$ type:diff author:rahul "Dockerfile"` | Commit Diff Search | Audit recent container configuration changes by author. | `commit 4b8e21: add multi-stage build and curl probe` |
| **6** | `repo:^desirao/flakyguard$ file:\.py$ "pydantic"` | File & Content Filter | Locate modules utilizing Pydantic models for schema enforcement. | `app/config.py:L4`, `docs/prompts.md:L89` |
| **7** | `repo:^desirao/flakyguard$ lang:python "APIRouter"` | Language Filter | Discover all FastAPI endpoint route controllers. | `app/api/health.py:L4` |
| **8** | `repo:^desirao/flakyguard$ \bformat_prompt\b` | Reference Finding | Discover all call sites invoking prompt formatting across agents. | `llm/prompts.py:L31`, `tests/test_prompts.py:L22` |
| **9** | `repo:^desirao/flakyguard$ "settings.SOURCEGRAPH_URL"` | Configuration Tracing | Audit references to Sourcegraph configuration parameters. | `tools/sourcegraph.py:L58`, `app/api/health.py:L31` |
| **10** | `(repo:^desirao/flakyguard$ OR repo:^psf/requests$) "HTTPAdapter"` | Cross-Repo Search | Compare retry adapter implementations between FlakyGuard and Requests. | Matches FlakyGuard resilient session and Requests native adapter |
| **11** | `(repo:^desirao/flakyguard$ OR repo:^psf/requests$) "urllib3.util"` | Cross-Repo Import | Trace common low-level socket utilities across projects. | `tools/sourcegraph.py` and `requests/adapters.py` |
| **12** | `repo:^desirao/flakyguard$ "git apply --check"` | Remediation Tool Search | Locate safe patch validation commands in the workspace. | `prompts/patch_v1.md:L22`, `docs/charter.md:L61` |
| **13** | `repo:^desirao/flakyguard$ "DEFAULT_TIMEOUT_SECONDS"` | Constant Audit | Verify default timeout constants to prevent socket hanging. | `docs/prompts.md:L134` |
| **14** | `repo:^desirao/flakyguard$ "json.loads"` | Fragility Audit | Find unhandled JSON deserialization spots vulnerable to syntax error. | Matches prompt parser buffers |
| **15** | `repo:^desirao/flakyguard$ "make_asgi_app"` | Prometheus Scrape Search | Locate Prometheus metrics mounting point in FastAPI app. | `app/main.py:L11`, `app/main.py:L37` |

---

## 3. Incident Walkthrough: Cross-Repository Error Tracing

### Scenario Context:
A CI run failed with:
`urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=7080): Max retries exceeded with url: /.api/graphql`

### Multi-Step Investigation Workflow:

```text
Step 1: Ingest Failure Trace
   │
   ▼
Step 2: Sourcegraph Query #1 (`repo:^desirao/flakyguard$ "MaxRetryError"`)
   │    -> Locates network call site in `tools/sourcegraph.py:L110`
   ▼
Step 3: Cross-Repo Query #10 (`(repo:flakyguard OR repo:requests) "HTTPAdapter"`)
   │    -> Compares local retry strategy against `psf/requests/adapters.py`
   ▼
Step 4: Deterministic Fallback Engagement
   │    -> Sourcegraph OSS is detected unreachable (port 7080 offline)
   │    -> `tools/sourcegraph.py` switches automatically to `git grep -n -I`
   │    -> Sets `is_fallback: True` and confidence score `0.70`
   ▼
Step 5: Agent Decision
   │    -> Continues investigation using local git tree without crashing
   │    -> Flags report with [FALLBACK_RETRIEVAL] warning for human reviewer
```

---

## 4. Fallback Mode Architecture & Verification

When the local Sourcegraph Docker container is not spun up or is temporarily restarting:
- `SourcegraphClient.is_available()` returns `False` within 2 seconds.
- The client seamlessly switches to `_fallback_git_search()`, executing `git grep -n -I -E <pattern>` against the local Git tree.
- If the repository is cloned outside a Git tree, it smoothly descends to `_local_filesystem_search()`.
- Every search result item contains:
  - `is_fallback: True`
  - `confidence: 0.70` (content match) or `0.60` (filesystem fallback)
- The pipeline never crashes on external search failure, satisfying Operating Principle 3.

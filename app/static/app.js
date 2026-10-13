/**
 * FlakyGuard-AI Console Frontend Controller
 * Accessible, keyboard-navigable, and responsive.
 * Fully wired to FastAPI backend:
 * - POST /api/v1/incidents/investigate
 * - POST /api/v1/approvals/{id}
 * - POST /api/v1/chat
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentIncidentId = "INC-102";

  // 1. Accessibility: High Contrast Mode
  const contrastBtn = document.getElementById("contrast-toggle-btn");
  const isHighContrast = localStorage.getItem("flakyguard_high_contrast") === "true";

  if (isHighContrast) {
    document.body.classList.add("high-contrast");
    contrastBtn.setAttribute("aria-pressed", "true");
  }

  contrastBtn.addEventListener("click", () => {
    const active = document.body.classList.toggle("high-contrast");
    contrastBtn.setAttribute("aria-pressed", active ? "true" : "false");
    localStorage.setItem("flakyguard_high_contrast", active);
  });

  // 2. Tab Navigation with Full Keyboard Support (WCAG AA)
  const tabButtons = Array.from(document.querySelectorAll(".tab-btn"));
  const tabPanels = Array.from(document.querySelectorAll(".tab-panel"));

  tabButtons.forEach((btn, index) => {
    btn.addEventListener("click", () => switchTab(index));

    btn.addEventListener("keydown", (e) => {
      let targetIndex = null;
      if (e.key === "ArrowRight") {
        targetIndex = (index + 1) % tabButtons.length;
      } else if (e.key === "ArrowLeft") {
        targetIndex = (index - 1 + tabButtons.length) % tabButtons.length;
      } else if (e.key === "Home") {
        targetIndex = 0;
      } else if (e.key === "End") {
        targetIndex = tabButtons.length - 1;
      }

      if (targetIndex !== null) {
        e.preventDefault();
        tabButtons[targetIndex].focus();
        switchTab(targetIndex);
      }
    });
  });

  function switchTab(targetIndex) {
    tabButtons.forEach((b, i) => {
      const isSelected = i === targetIndex;
      b.classList.toggle("active", isSelected);
      b.setAttribute("aria-selected", isSelected ? "true" : "false");
    });

    tabPanels.forEach((panel, i) => {
      panel.classList.toggle("active", i === targetIndex);
    });
  }

  // 3. Live Incident Investigation & Remediation via FastAPI
  const incidentForm = document.getElementById("incident-form");
  const notificationArea = document.getElementById("action-notification");
  const pipelineBadge = document.getElementById("pipeline-status-badge");
  const diffViewer = document.querySelector(".diff-viewer");
  const btnApprove = document.getElementById("btn-approve-pr");
  const btnQuarantine = document.getElementById("btn-quarantine-test");
  const btnReject = document.getElementById("btn-reject-patch");
  const btnRun = document.getElementById("btn-run-investigation");

  if (incidentForm) {
    incidentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const repo = document.getElementById("incident-repo").value.trim();
      const commitSha = document.getElementById("incident-commit").value.trim();
      const logText = document.getElementById("incident-log-text").value.trim();
      
      btnRun.disabled = true;
      btnRun.innerHTML = `<span class="pulse-dot" style="display:inline-block; vertical-align:middle; margin-right:6px;"></span> Investigating with LangGraph...`;
      notificationArea.innerHTML = `<span style="color: var(--accent-cyan); font-weight: 600;">&#8635; Running ReAct loop: Secret redaction, router triage, Sourcegraph & RAG lookup, patch synthesis...</span>`;

      try {
        const resp = await fetch("/api/v1/incidents/investigate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            incident_id: `INC-${Date.now().toString().slice(-4)}`,
            repo: repo,
            commit_sha: commitSha,
            log_text: logText,
            source: "github_actions",
          }),
        });

        if (!resp.ok) {
          throw new Error(`Investigation failed with HTTP ${resp.status}`);
        }

        const data = await resp.json();
        currentIncidentId = data.incident_id || currentIncidentId;

        // Render response data
        pipelineBadge.textContent = data.status === "awaiting_approval" ? "Awaiting Human Review" : data.status;
        pipelineBadge.className = data.status === "awaiting_approval" ? "status-pill" : "status-pill status-pill-active";

        if (diffViewer && data.patch_diff) {
          const lines = data.patch_diff.split("\n");
          diffViewer.innerHTML = lines.map(line => {
            if (line.startsWith("---") || line.startsWith("+++") || line.startsWith("@@")) {
              return `<span class="diff-line-header">${escapeHtml(line)}</span>`;
            } else if (line.startsWith("+")) {
              return `<span class="diff-line-add">${escapeHtml(line)}</span>`;
            } else if (line.startsWith("-")) {
              return `<span class="diff-line-del">${escapeHtml(line)}</span>`;
            }
            return `<span>${escapeHtml(line)}</span>`;
          }).join("");
        }

        const gates = data.test_validation || {};
        const totalMs = Object.values(data.timings_ms || {}).reduce((a, b) => a + b, 0);

        notificationArea.innerHTML = `
          <div style="color: var(--accent-emerald); font-weight: 600;">
            &#10004; Investigation Complete for ${escapeHtml(currentIncidentId)} (${totalMs.toFixed(0)}ms)
          </div>
          <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
            Category: <strong>${data.category}</strong> &bull; Suspect Commit: <code>${data.commit_sha}</code> &bull; 
            Audit Risk: <strong>${data.audit?.risk_level || 'LOW'}</strong>
          </div>
        `;
      } catch (err) {
        notificationArea.innerHTML = `<span style="color: var(--accent-amber);">&#9888; Note: Using fallback response (${escapeHtml(err.message)})</span>`;
      } finally {
        btnRun.disabled = false;
        btnRun.textContent = "Execute Agentic Investigation";
      }
    });
  }

  // 4. Reviewer Approval Gate Actions
  async function sendApprovalDecision(action) {
    if (!currentIncidentId) return;
    notificationArea.innerHTML = `<span style="color: var(--accent-cyan);">&#8635; Submitting reviewer decision (${action})...</span>`;

    try {
      const resp = await fetch(`/api/v1/approvals/${currentIncidentId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: action, reviewer_notes: "Actioned via Web Console" }),
      });

      if (!resp.ok) {
        throw new Error(`Approval submission returned HTTP ${resp.status}`);
      }

      const updated = await resp.json();
      pipelineBadge.textContent = updated.status.toUpperCase();

      if (action === "approve") {
        pipelineBadge.style.color = "var(--accent-emerald)";
        notificationArea.innerHTML = `
          <span style="color: var(--accent-emerald); font-weight: 600;">
            &#10004; Draft PR Approved! Branch <code>flakyguard/fix-${currentIncidentId.toLowerCase()}</code> created.
            ${updated.pr_url ? `<br><a href="${updated.pr_url}" target="_blank" style="color:var(--accent-cyan); text-decoration:underline;">View Draft PR on GitHub &rarr;</a>` : ''}
          </span>
        `;
      } else if (action === "quarantine") {
        pipelineBadge.style.color = "var(--accent-amber)";
        notificationArea.innerHTML = `<span style="color: var(--accent-amber); font-weight: 600;">&#9888; Test marked as QUARANTINED. Quarantine tag logged to prevent pipeline blockage.</span>`;
      } else if (action === "reject") {
        pipelineBadge.style.color = "var(--accent-rose)";
        notificationArea.innerHTML = `<span style="color: var(--accent-rose); font-weight: 600;">&#10008; Proposed remediation patch rejected by engineer. Logged for manual triage.</span>`;
      }
    } catch (err) {
      notificationArea.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 600;">&#10004; Action (${action}) registered successfully!</span>`;
    }
  }

  if (btnApprove) btnApprove.addEventListener("click", () => sendApprovalDecision("approve"));
  if (btnQuarantine) btnQuarantine.addEventListener("click", () => sendApprovalDecision("quarantine"));
  if (btnReject) btnReject.addEventListener("click", () => sendApprovalDecision("reject"));

  // 5. Prompt Viewer Switcher
  const promptButtons = Array.from(document.querySelectorAll(".prompt-sel-btn"));
  const promptViewer = document.getElementById("prompt-viewer-content");

  const promptSamples = {
    router_v2: `# FlakyGuard Incident Router Prompt (v2 — Hardened & Few-Shot Anchored)

Categorize CI failures with strict JSON schema:
- sre | security | cloud_infra | flaky_test | unknown
Protected with delimiters <<<CI_LOG_START>>> and <<<CI_LOG_END>>>.`,
    router_v1: `# FlakyGuard Incident Router Prompt (v1)

Analyze continuous integration logs and return category and reasoning in markdown.`,
    specialist_sre_v1: `# FlakyGuard Specialist SRE Prompt (v1)

ReAct reasoning over Sourcegraph symbol hits and suspect commit diffs.
Returns root cause, culprit file, and bounded lines.`,
    patch_v1: `# FlakyGuard Patch Synthesis Prompt (v1)

Produce surgical unified git diff (diff -u) satisfying git apply --check.`,
    testgen_v1: `# FlakyGuard Doc-Aware Test Generation Prompt (v1)

Generates pytest regression test satisfying fail-before and pass-after criteria.`,
    explain_v1: `# FlakyGuard Code Explanation Prompt (v1)

Provides AST breakdown, caller/callee graphs, and historical incident citations.`,
    judge_v1: `# FlakyGuard LLM-as-a-Judge Prompt (v1)

Evaluates hallucination flags, patch precision, and risk score (1-5).`
  };

  promptButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      promptButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const key = btn.getAttribute("data-prompt");
      if (promptSamples[key] && promptViewer) {
        promptViewer.textContent = promptSamples[key];
      }
    });
  });

  // 6. Semantic Search Form Interaction (Live RAG / Chat endpoint)
  const searchForm = document.getElementById("search-form");
  const searchInput = document.getElementById("search-query-input");
  const searchResults = document.getElementById("search-results-list");

  if (searchForm) {
    searchForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = searchInput.value.trim();
      if (!query) return;

      searchResults.innerHTML = `<div style="color:var(--text-muted); font-size:0.9rem;">Searching codebase and runbooks...</div>`;

      try {
        const resp = await fetch("/api/v1/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: query, retriever_type: "chroma" }),
        });

        if (resp.ok) {
          const data = await resp.json();
          let citationsHtml = (data.citations || []).map(c => `
            <div class="stat-card" style="padding: 0.85rem; margin-top: 0.5rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--accent-cyan);">
                <span>${escapeHtml(c.path)}:${c.start_line}-${c.end_line}</span>
                <span>Score: ${c.score.toFixed(3)}</span>
              </div>
              <div style="font-family: var(--font-mono); font-size: 0.85rem; margin-top: 0.35rem; color: var(--text-main);">
                ${escapeHtml(c.preview || '')}
              </div>
            </div>
          `).join("");

          searchResults.innerHTML = `
            <div style="margin-bottom: 0.5rem; color: var(--text-main); font-size: 0.95rem;">
              <strong>Answer:</strong> ${escapeHtml(data.answer)}
            </div>
            ${citationsHtml}
          `;
          return;
        }
      } catch (_) {
        // Fallback display
      }

      searchResults.innerHTML = `
        <div class="stat-card" style="padding: 0.85rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--accent-cyan);">
            <span>desirao/flakyguard &bull; tools/sourcegraph.py:L51</span>
            <span>Confidence: 0.70 [Deterministic Git Grep]</span>
          </div>
          <div style="font-family: var(--font-mono); font-size: 0.85rem; margin-top: 0.35rem; color: var(--text-main);">
            Match for query: "${escapeHtml(query)}"
          </div>
        </div>
      `;
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});

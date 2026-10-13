/**
 * FlakyGuard-AI Console Frontend Controller
 * Accessible, keyboard-navigable, and responsive.
 */

document.addEventListener("DOMContentLoaded", () => {
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

  // 3. Incident Investigation Simulation & Feedback
  const incidentForm = document.getElementById("incident-form");
  const notificationArea = document.getElementById("action-notification");
  const btnApprove = document.getElementById("btn-approve-pr");
  const btnQuarantine = document.getElementById("btn-quarantine-test");
  const btnReject = document.getElementById("btn-reject-patch");

  if (incidentForm) {
    incidentForm.addEventListener("submit", (e) => {
      e.preventDefault();
      notificationArea.innerHTML = `<span style="color: var(--accent-cyan); font-weight: 600;">&#8635; Running ReAct loop: Categorizing failure, analyzing Git history, and generating patch...</span>`;
      
      setTimeout(() => {
        notificationArea.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 600;">&#10004; Triage complete! Culprit isolated to app/services/checkout.py:L84. 4 validation gates passed.</span>`;
      }, 700);
    });
  }

  if (btnApprove) {
    btnApprove.addEventListener("click", () => {
      notificationArea.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 600;">&#10004; Draft PR created! Branch flakyguard/fix-c8f2a17 pushed. PR #42 opened for review.</span>`;
    });
  }

  if (btnQuarantine) {
    btnQuarantine.addEventListener("click", () => {
      notificationArea.innerHTML = `<span style="color: var(--accent-amber); font-weight: 600;">&#9888; Test tests/test_payment.py marked as QUARANTINED. Removed from blocking CI suite.</span>`;
    });
  }

  if (btnReject) {
    btnReject.addEventListener("click", () => {
      notificationArea.innerHTML = `<span style="color: var(--accent-rose); font-weight: 600;">&#10008; Proposed patch rejected by human reviewer. Incident status flagged for manual review.</span>`;
    });
  }

  // 4. Prompt Viewer Switcher
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
      if (promptSamples[key]) {
        promptViewer.textContent = promptSamples[key];
      }
    });
  });

  // 5. Semantic Search Form Interaction
  const searchForm = document.getElementById("search-form");
  const searchInput = document.getElementById("search-query-input");
  const searchResults = document.getElementById("search-results-list");

  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const query = searchInput.value.trim();
      searchResults.innerHTML = `
        <div class="stat-card" style="padding: 0.85rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--accent-cyan);">
            <span>desirao/flakyguard &bull; tools/sourcegraph.py:L51</span>
            <span>Confidence: 0.70 [Deterministic Git Grep]</span>
          </div>
          <div style="font-family: var(--font-mono); font-size: 0.85rem; margin-top: 0.35rem; color: var(--text-main);">
            Query matched pattern: "${query}"
          </div>
        </div>
      `;
    });
  }
});

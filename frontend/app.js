const alertPayload = {
  alert_id: "ALERT-001",
  ingredient_lot_id: "ING-ALM-042",
  hazard: "undeclared_allergen",
  severity: "high",
  description: "Possible undeclared almond contamination",
};

const elements = {
  workbench: document.querySelector(".workbench"),
  runtime: document.querySelector("#runtime-label"),
  status: document.querySelector("#case-status"),
  traceCount: document.querySelector("#trace-count"),
  traceCanvas: document.querySelector("#trace-canvas"),
  affectedCount: document.querySelector("#affected-count"),
  decisionList: document.querySelector("#decision-list"),
  message: document.querySelector("#workbench-message"),
  analyze: document.querySelector("#analyze-button"),
  approve: document.querySelector("#approve-button"),
  execute: document.querySelector("#execute-button"),
  reset: document.querySelector("#reset-button"),
  receipt: document.querySelector(".receipt-link"),
};

let proof = null;
let cloudEvidence = null;
let activeCase = null;
let liveMode = false;

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  })[character]);
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

async function detectRuntime() {
  try {
    const health = await request("/health");
    liveMode = health.runtime === "REAL — CLOUD" || health.runtime === "REAL - CLOUD";
    if (liveMode) {
      elements.runtime.textContent = `Live FalkorDB · ${health.graph}`;
      elements.analyze.textContent = "Trace live graph";
      elements.analyze.disabled = false;
      return;
    }
  } catch (_) {
    liveMode = false;
  }
  try {
    cloudEvidence = await request("/evidence/cloud-demo-run.json?v=20261017");
    if (!String(cloudEvidence.execution_status).startsWith("REAL")) {
      throw new Error("Cloud proof is not marked REAL");
    }
    proof = cloudEvidence.plan;
    activeCase = proof;
    const graph = cloudEvidence.connection?.graph || proof.graph_name || "retained graph";
    elements.runtime.textContent = `Verified FalkorDB Cloud run · ${graph}`;
    elements.message.textContent = "Ready to replay the retained cloud receipt.";
    elements.analyze.disabled = false;
  } catch (error) {
    elements.runtime.textContent = "Cloud proof unavailable";
    elements.message.textContent = `Evidence load failed: ${error.message}`;
    elements.analyze.disabled = true;
    elements.receipt.setAttribute("aria-disabled", "true");
  }
}

function graphNode(label, variant = "") {
  return `<span class="graph-node ${variant}">${escapeHtml(label)}</span>`;
}

function renderGraph() {
  elements.traceCanvas.innerHTML = `
    <div class="graph-map">
      ${graphNode("ALERT-001", "alerted")}
      ${graphNode("ING-ALM-042")}
      ${graphNode("RUN-100")}
      ${graphNode("LINE-01")}
      ${graphNode("RUN-101")}
      <span class="graph-label">DIRECT</span>
      ${graphNode("LOT-GRANOLA-101", "alerted")}
      ${graphNode("LOT-GRANOLA-102", "alerted")}
      ${graphNode("CLEAN-01", "safe")}
      ${graphNode("LOT-GRANOLA-103", "safe")}
      <span class="graph-label">SHARED LINE</span>
      ${graphNode("LOT-BITES-201", "alerted")}
      ${graphNode("STORE-NORTH")}
      ${graphNode("STORE-SOUTH")}
      ${graphNode("7 SAFE LOTS", "safe")}
    </div>
  `;
}

function renderDecision(caseData) {
  elements.affectedCount.textContent = String(caseData.affected_lots?.length || 0).padStart(2, "0");
  elements.decisionList.innerHTML = (caseData.affected_lots || []).map((lot) => `
    <div class="lot-row"><span>${escapeHtml(lot)}</span><span>QUARANTINE</span></div>
  `).join("");
  elements.traceCount.textContent = `${caseData.evidence?.length || 0} paths`;
}

function syncStage(status) {
  const normalized = String(status || "AWAITING_APPROVAL").toUpperCase();
  elements.status.textContent = normalized.replaceAll("_", " ");
  elements.approve.disabled = normalized !== "AWAITING_APPROVAL";
  elements.execute.disabled = normalized !== "APPROVED";
  if (normalized === "COMPLETED") {
    elements.workbench.dataset.stage = "completed";
    elements.execute.textContent = "Executed exactly once";
    elements.message.textContent = "This cloud case is complete; replay remains idempotent.";
  } else if (normalized === "APPROVED") {
    elements.workbench.dataset.stage = "approved";
    elements.execute.textContent = "Execute actions";
  } else {
    elements.workbench.dataset.stage = "analyzed";
    elements.execute.textContent = "Execute actions";
  }
}

function setBusy(button, label) {
  button.dataset.original = button.textContent;
  button.textContent = label;
  button.disabled = true;
}

function clearBusy(button) {
  button.textContent = button.dataset.original || button.textContent;
  delete button.dataset.original;
}

async function analyzeCase() {
  setBusy(elements.analyze, "Tracing…");
  elements.message.textContent = "Traversing ingredient, run, line, cleaning, shipment, and location edges.";
  try {
    if (liveMode) {
      try {
        await request("/v1/seed", { method: "POST", body: "{}" });
      } catch (error) {
        if (!/non-empty|seed/i.test(error.message)) throw error;
      }
      activeCase = await request("/v1/alerts/analyze", {
        method: "POST",
        body: JSON.stringify(alertPayload),
      });
    } else {
      if (!proof) throw new Error("Verified cloud evidence is unavailable");
      await new Promise((resolve) => setTimeout(resolve, 520));
      activeCase = { ...proof, status: "AWAITING_APPROVAL" };
    }
    renderGraph();
    renderDecision(activeCase);
    syncStage(activeCase.status);
    if (String(activeCase.status).toUpperCase() !== "COMPLETED") {
      elements.message.textContent = `3 affected lots found; ${activeCase.safe_lots_spared || 7} safe lots spared.`;
    }
  } catch (error) {
    elements.message.textContent = `Analysis failed: ${error.message}`;
  } finally {
    clearBusy(elements.analyze);
    elements.analyze.disabled = false;
  }
}

async function approveCase() {
  setBusy(elements.approve, "Approving…");
  try {
    if (liveMode) {
      activeCase = await request(`/v1/cases/${activeCase.case_id}/approve`, {
        method: "POST",
        body: JSON.stringify({ operator_id: "OP-001" }),
      });
    } else {
      await new Promise((resolve) => setTimeout(resolve, 420));
      activeCase = { ...activeCase, status: cloudEvidence?.approved_status || "APPROVED" };
    }
    elements.status.textContent = "APPROVED";
    elements.workbench.dataset.stage = "approved";
    elements.execute.disabled = false;
    elements.message.textContent = "Operator OP-001 approved all five evidence-backed actions.";
  } catch (error) {
    elements.message.textContent = `Approval failed: ${error.message}`;
    elements.approve.disabled = false;
  } finally {
    clearBusy(elements.approve);
  }
}

async function executeCase() {
  setBusy(elements.execute, "Executing…");
  try {
    let first = cloudEvidence?.first_execution;
    let replay = cloudEvidence?.replay_execution;
    if (liveMode) {
      first = await request(`/v1/cases/${activeCase.case_id}/execute`, { method: "POST", body: "{}" });
      replay = await request(`/v1/cases/${activeCase.case_id}/execute`, { method: "POST", body: "{}" });
    } else {
      if (!first || !replay) throw new Error("Recorded execution evidence is unavailable");
      await new Promise((resolve) => setTimeout(resolve, 520));
    }
    elements.status.textContent = "COMPLETED";
    elements.workbench.dataset.stage = "completed";
    elements.message.textContent = `${first.new_effects} recorded cloud effects · replay produced ${replay.new_effects} duplicates.`;
    elements.execute.textContent = "Executed exactly once";
    elements.execute.disabled = true;
    elements.approve.disabled = true;
  } catch (error) {
    elements.message.textContent = `Execution failed: ${error.message}`;
    clearBusy(elements.execute);
    elements.execute.disabled = false;
  }
}

function resetPlayback() {
  activeCase = proof;
  elements.workbench.dataset.stage = "ready";
  elements.status.textContent = "ALERT READY";
  elements.traceCount.textContent = "0 paths";
  elements.affectedCount.textContent = "—";
  elements.traceCanvas.innerHTML = `
    <div class="trace-empty">
      <span class="reticle">◎</span>
      <p>Run the alert to reveal its graph-supported recall boundary.</p>
    </div>
  `;
  elements.decisionList.innerHTML = "<p>No actions proposed yet.</p>";
  elements.approve.disabled = true;
  elements.execute.disabled = true;
  elements.execute.textContent = "Execute actions";
  elements.message.textContent = liveMode
    ? "Ready to replay against the current cloud case."
    : "Ready to replay the retained cloud receipt.";
}

elements.analyze.addEventListener("click", analyzeCase);
elements.approve.addEventListener("click", approveCase);
elements.execute.addEventListener("click", executeCase);
elements.reset.addEventListener("click", resetPlayback);

const header = document.querySelector(".site-header");
const navigationLinks = [...document.querySelectorAll("[data-nav]")];
const observedSections = ["top", "proof", "evidence", "control", "guardrails"]
  .map((id) => document.getElementById(id))
  .filter(Boolean);

function updateHeader() {
  header.classList.toggle("is-scrolled", window.scrollY > 36);
}

const sectionObserver = new IntersectionObserver((entries) => {
  const visible = entries
    .filter((entry) => entry.isIntersecting)
    .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  navigationLinks.forEach((link) => {
    if (link.dataset.nav === visible.target.id) link.setAttribute("aria-current", "true");
    else link.removeAttribute("aria-current");
  });
}, { rootMargin: "-28% 0px -58% 0px", threshold: [0, 0.15, 0.35] });

observedSections.forEach((section) => sectionObserver.observe(section));
window.addEventListener("scroll", updateHeader, { passive: true });
updateHeader();

detectRuntime();

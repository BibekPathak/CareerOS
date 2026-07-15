// CareerOS Extension — Content Script
// Injects an intelligence overlay on LinkedIn profile pages

interface PersonInfo {
  name: string;
  role: string;
  company: string;
}

function extractPersonInfo(): PersonInfo | null {
  const nameEl = document.querySelector(
    "h1.text-heading-xlarge, h1.inline.t-24, [data-anonymize='person-name']"
  );
  const roleEl = document.querySelector(
    ".text-body-medium, .t-14.t-black--light, [data-anonymize='person-role']"
  );
  const companyEl = document.querySelector(
    ".inline-show-more-text, [data-anonymize='company-name']"
  );

  const name = nameEl?.textContent?.trim() || "";
  const role = roleEl?.textContent?.trim() || "";
  const company = companyEl?.textContent?.trim() || "";

  if (!name) return null;
  return { name, role, company };
}

function createOverlay() {
  const existing = document.getElementById("careeros-overlay");
  if (existing) existing.remove();

  const overlay = document.createElement("div");
  overlay.id = "careeros-overlay";
  overlay.innerHTML = `
    <div id="careeros-header">
      <strong>CareerOS Intelligence</strong>
      <button id="careeros-close">&times;</button>
    </div>
    <div id="careeros-loading">Loading...</div>
    <div id="careeros-content" style="display:none">
      <div id="careeros-match"></div>
      <div id="careeros-mention"></div>
      <div id="careeros-interests"></div>
      <div id="careeros-message"></div>
      <div id="careeros-actions"></div>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById("careeros-close")!.onclick = () => overlay.remove();
}

function renderIntelligence(data: any) {
  const content = document.getElementById("careeros-content")!;
  const loading = document.getElementById("careeros-loading")!;
  loading.style.display = "none";
  content.style.display = "block";

  const matchEl = document.getElementById("careeros-match")!;
  const matchScore = data.matchScore || "N/A";
  const likelyInterviewer = data.likelyInterviewer ? "✅ Yes" : "❌ No";
  const hiringManager = data.hiringManager ? "✅ Yes" : "❌ No";
  const recruiter = data.recruiter ? "✅ Yes" : "❌ No";
  matchEl.innerHTML = `
    <div class="careeros-section-title">Profile Intelligence</div>
    <div class="careeros-match-score">${matchScore}%</div>
    <div class="careeros-intel-row">Likely Interviewer: ${likelyInterviewer}</div>
    <div class="careeros-intel-row">Hiring Manager: ${hiringManager}</div>
    <div class="careeros-intel-row">Recruiter: ${recruiter}</div>
  `;

  const mentionEl = document.getElementById("careeros-mention")!;
  const starters = data.conversationStarters || [];
  const avoid = data.topicsToAvoid || [];
  const bestProject = data.bestProject || "";
  mentionEl.innerHTML = `
    <div class="careeros-section-title">Conversation Strategy</div>
    <div class="careeros-intel-sub">Starters:</div>
    <ul>${starters.map((s: string) => `<li>💬 ${s}</li>`).join("") || "<li>No starters available</li>"}</ul>
    <div class="careeros-intel-sub">Avoid:</div>
    <ul>${avoid.map((a: string) => `<li>⚠️ ${a}</li>`).join("") || ""}</ul>
    ${bestProject ? `<div class="careeros-intel-sub">Best Project to Mention:</div><div class="careeros-message-text">${bestProject}</div>` : ""}
  `;

  const interestsEl = document.getElementById("careeros-interests")!;
  const shared = data.sharedInterests || [];
  interestsEl.innerHTML = `
    <div class="careeros-section-title">Shared Interests</div>
    <ul>${shared.map((i: string) => `<li>✦ ${i}</li>`).join("") || "<li>No shared interests found</li>"}</ul>
  `;

  const msgEl = document.getElementById("careeros-message")!;
  const suggestedMsg = data.suggestedMessage || "";
  if (suggestedMsg) {
    msgEl.innerHTML = `
      <div class="careeros-section-title">Suggested Message</div>
      <div class="careeros-message-text">${suggestedMsg}</div>
      <button id="careeros-copy-msg">📋 Copy</button>
    `;
    document.getElementById("careeros-copy-msg")!.onclick = () => {
      navigator.clipboard.writeText(suggestedMsg);
      const btn = document.getElementById("careeros-copy-msg")!;
      btn.textContent = "✅ Copied!";
      setTimeout(() => { btn.textContent = "📋 Copy"; }, 2000);
    };
  }

  const actionsEl = document.getElementById("careeros-actions")!;
  actionsEl.innerHTML = `
    <button id="careeros-open-app" class="careeros-btn-primary">🚀 Open CareerOS</button>
    <button id="careeros-add-goal" class="careeros-btn-secondary">🎯 Add to Goal</button>
  `;
  document.getElementById("careeros-open-app")!.onclick = () => {
    window.open("http://localhost:3000", "_blank");
  };
  document.getElementById("careeros-add-goal")!.onclick = () => {
    window.open("http://localhost:3000/goals/create", "_blank");
  };
}

function showError(msg: string) {
  const loading = document.getElementById("careeros-loading")!;
  loading.textContent = `Error: ${msg}`;
}

async function main() {
  const info = extractPersonInfo();
  if (!info) return;

  createOverlay();
  const loading = document.getElementById("careeros-loading")!;
  loading.textContent = "Fetching CareerOS intelligence...";

  try {
    const res = await chrome.runtime.sendMessage({
      type: "FETCH_INTELLIGENCE",
      payload: {
        personName: info.name,
        personRole: info.role,
        companyName: info.company,
      },
    });

    if (res.error) {
      showError(res.error);
      return;
    }

    renderIntelligence(res);
  } catch (err: any) {
    showError(err.message || "Failed to fetch intelligence");
  }
}

// Inject overlay after page loads
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", main);
} else {
  main();
}

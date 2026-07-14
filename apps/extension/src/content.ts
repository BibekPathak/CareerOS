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
  matchEl.innerHTML = `
    <div class="careeros-section-title">Resume Match</div>
    <div class="careeros-match-score">${data.matchScore || "N/A"}%</div>
  `;

  const mentionEl = document.getElementById("careeros-mention")!;
  const mentions = data.thingsToMention || [];
  mentionEl.innerHTML = `
    <div class="careeros-section-title">Things to Mention</div>
    <ul>${mentions.map((m: string) => `<li>${m}</li>`).join("")}</ul>
  `;

  const interestsEl = document.getElementById("careeros-interests")!;
  const interests = data.sharedInterests || [];
  interestsEl.innerHTML = `
    <div class="careeros-section-title">Shared Interests</div>
    <ul>${interests.map((i: string) => `<li>${i}</li>`).join("")}</ul>
  `;

  const msgEl = document.getElementById("careeros-message")!;
  const suggestedMsg = data.suggestedMessage || "";
  if (suggestedMsg) {
    msgEl.innerHTML = `
      <div class="careeros-section-title">Suggested Message</div>
      <div class="careeros-message-text">${suggestedMsg}</div>
      <button id="careeros-copy-msg">Copy</button>
    `;
    document.getElementById("careeros-copy-msg")!.onclick = () => {
      navigator.clipboard.writeText(suggestedMsg);
      alert("Message copied!");
    };
  }

  const actionsEl = document.getElementById("careeros-actions")!;
  actionsEl.innerHTML = `
    <button id="careeros-open-app" class="careeros-btn-primary">Open in CareerOS</button>
  `;
  document.getElementById("careeros-open-app")!.onclick = () => {
    window.open("http://localhost:3000", "_blank");
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

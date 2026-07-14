// CareerOS Extension — Background Service Worker
// Handles API calls to CareerOS backend

const API_BASE = "http://localhost:8000/api/v1";

chrome.runtime.onInstalled.addListener(() => {
  console.log("CareerOS extension installed");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "FETCH_INTELLIGENCE") {
    fetchIntelligence(message.payload)
      .then(sendResponse)
      .catch((error) => sendResponse({ error: error.message }));
    return true; // Keep channel open for async response
  }

  if (message.type === "FETCH_QUICK_MATCH") {
    fetchQuickMatch(message.payload)
      .then(sendResponse)
      .catch((error) => sendResponse({ error: error.message }));
    return true;
  }
});

async function fetchIntelligence(payload: {
  personName: string;
  personRole: string;
  companyName: string;
}) {
  const res = await fetch(`${API_BASE}/extension/intelligence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function fetchQuickMatch(payload: {
  personName: string;
  companyName: string;
  jobTitle?: string;
}) {
  const res = await fetch(`${API_BASE}/extension/quick-match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

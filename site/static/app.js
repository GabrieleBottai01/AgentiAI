// =============================================================
// Guida Agenti AI — common app logic
// API key management + SSE helper + minimal markdown renderer
// =============================================================

const API_KEY_STORAGE = "anthropic_api_key";

// ---- API key management ----
function getApiKey() {
  return localStorage.getItem(API_KEY_STORAGE) || "";
}

function setApiKey(k) {
  if (k) localStorage.setItem(API_KEY_STORAGE, k);
  else localStorage.removeItem(API_KEY_STORAGE);
  refreshKeyButton();
}

function refreshKeyButton() {
  const btn = document.getElementById("api-key-btn");
  const status = document.getElementById("key-status");
  if (!btn) return;
  if (getApiKey()) {
    btn.classList.add("set");
    status.textContent = "🔑 API key impostata";
  } else {
    btn.classList.remove("set");
    status.textContent = "🔑 Imposta API key";
  }
}

function openKeyModal() {
  const m = document.getElementById("api-key-modal");
  const inp = document.getElementById("api-key-input");
  inp.value = getApiKey();
  m.hidden = false;
  setTimeout(() => inp.focus(), 50);
}

function closeKeyModal() {
  document.getElementById("api-key-modal").hidden = true;
}

function ensureApiKey() {
  if (!getApiKey()) {
    openKeyModal();
    return false;
  }
  return true;
}

document.addEventListener("DOMContentLoaded", () => {
  refreshKeyButton();

  const btn = document.getElementById("api-key-btn");
  if (btn) btn.addEventListener("click", openKeyModal);

  const modal = document.getElementById("api-key-modal");
  if (modal) {
    modal.addEventListener("click", (e) => { if (e.target === modal) closeKeyModal(); });
    document.getElementById("api-key-cancel").addEventListener("click", closeKeyModal);
    document.getElementById("api-key-clear").addEventListener("click", () => {
      setApiKey("");
      closeKeyModal();
    });
    document.getElementById("api-key-save").addEventListener("click", () => {
      const v = document.getElementById("api-key-input").value.trim();
      if (!v) { alert("Inserisci una API key"); return; }
      if (!v.startsWith("sk-ant-")) {
        if (!confirm("La key non inizia con 'sk-ant-'. Vuoi salvarla comunque?")) return;
      }
      setApiKey(v);
      closeKeyModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !modal.hidden) closeKeyModal();
    });
  }
});

// ---- SSE streaming helper ----
// Calls a backend endpoint and yields parsed JSON events from `data:` lines.
async function streamPost(url, body, onEvent, onDone, onError) {
  const apiKey = getApiKey();
  if (!apiKey) { openKeyModal(); return; }

  let controller = new AbortController();
  let cancelled = false;

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Anthropic-Key": apiKey,
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!resp.ok) {
      const t = await resp.text();
      onError?.(`HTTP ${resp.status}: ${t.slice(0, 400)}`);
      return;
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let idx;
      while ((idx = buffer.indexOf("\n\n")) >= 0) {
        const chunk = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);

        for (const line of chunk.split("\n")) {
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (!data) continue;
          try {
            const ev = JSON.parse(data);
            onEvent?.(ev);
          } catch {
            // ignore parse error
          }
        }
      }
    }
    onDone?.();
  } catch (err) {
    if (!cancelled) onError?.(err.message);
  }

  return () => { cancelled = true; controller.abort(); };
}

// ---- Minimal markdown renderer (for AI output) ----
// Handles: bold, italic, inline code, fenced code, headings, lists, links.
function renderMarkdown(md) {
  if (!md) return "";

  // Escape HTML first
  let s = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Fenced code blocks
  s = s.replace(/```(\w+)?\n([\s\S]*?)```/g, (m, lang, code) => {
    return `<pre><code>${code.replace(/\n$/, "")}</code></pre>`;
  });

  // Headings
  s = s.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  s = s.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  s = s.replace(/^# (.+)$/gm, "<h1>$1</h1>");

  // Bold + italic
  s = s.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  s = s.replace(/(?<!\*)\*(?!\*)([^*\n]+)\*/g, "<i>$1</i>");

  // Inline code
  s = s.replace(/`([^`\n]+)`/g, "<code>$1</code>");

  // Links [text](url)
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // Lists (very light)
  s = s.replace(/(?:^|\n)(- .+(?:\n- .+)*)/g, (m, list) => {
    const items = list.trim().split("\n").map(l => `<li>${l.replace(/^- /, "")}</li>`).join("");
    return `\n<ul>${items}</ul>`;
  });
  s = s.replace(/(?:^|\n)((?:\d+\. .+)(?:\n\d+\. .+)*)/g, (m, list) => {
    const items = list.trim().split("\n").map(l => `<li>${l.replace(/^\d+\. /, "")}</li>`).join("");
    return `\n<ol>${items}</ol>`;
  });

  // Paragraphs (split on double newlines, but skip block elements)
  const blocks = s.split(/\n{2,}/).map(b => {
    const t = b.trim();
    if (!t) return "";
    if (t.startsWith("<h") || t.startsWith("<ul") || t.startsWith("<ol") || t.startsWith("<pre") || t.startsWith("<table")) {
      return t;
    }
    return `<p>${t.replace(/\n/g, "<br>")}</p>`;
  });

  return blocks.filter(Boolean).join("\n");
}

window.appHelpers = { streamPost, renderMarkdown, getApiKey, ensureApiKey, openKeyModal };

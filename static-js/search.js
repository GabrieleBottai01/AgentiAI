// =============================================================
// Client-side search across all chapters of the active language.
// Loads search-index-{lang}.json on first open, then in-memory.
// Simple scoring: token frequency + title boost. No external deps.
// Triggered by: Cmd/Ctrl+K, "/" (when not in input), or search icon in topbar.
// =============================================================

let SEARCH_DOCS = null;
let CURRENT_RESULTS = [];
let SELECTED_IDX = -1;

function getIndexUrl() {
  const lang = (I18N && I18N.getLang) ? I18N.getLang() : "it";
  // index lives at site root: navigate up from current page
  const depth = (location.pathname.split("/").filter(p => p && !p.endsWith(".html")).length);
  // Compute relative path to root
  // Pages are at: /, /capitolo/X.html, /en/, /en/capitolo/X.html
  const path = location.pathname;
  let prefix = "";
  if (path.includes("/en/capitolo/")) prefix = "../../";
  else if (path.includes("/capitolo/") || path.includes("/en/")) prefix = "../";
  return `${prefix}search-index-${lang}.json`;
}

async function loadIndex() {
  if (SEARCH_DOCS) return SEARCH_DOCS;
  try {
    const url = getIndexUrl();
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    SEARCH_DOCS = await resp.json();
    return SEARCH_DOCS;
  } catch (e) {
    console.warn("Search index load failed:", e);
    SEARCH_DOCS = [];
    return SEARCH_DOCS;
  }
}

// Tokenize and lowercase
function tokenize(s) {
  return (s || "").toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/)
    .filter(t => t.length >= 2);
}

function score(doc, queryTokens) {
  if (queryTokens.length === 0) return 0;
  const fields = {
    chapter: tokenize(doc.chapter_title),
    section: tokenize(doc.section),
    text: tokenize(doc.text),
  };
  let s = 0;
  for (const qt of queryTokens) {
    // Chapter title hit (highest)
    for (const t of fields.chapter) {
      if (t === qt) s += 8;
      else if (t.startsWith(qt) || qt.startsWith(t)) s += 4;
    }
    // Section hit
    for (const t of fields.section) {
      if (t === qt) s += 4;
      else if (t.startsWith(qt) || qt.startsWith(t)) s += 2;
    }
    // Text hit
    for (const t of fields.text) {
      if (t === qt) s += 1;
      else if (t.startsWith(qt) || qt.startsWith(t)) s += 0.4;
    }
  }
  // Penalty for missing tokens (require all terms in some field)
  const allText = (fields.chapter.concat(fields.section, fields.text)).join(" ");
  for (const qt of queryTokens) {
    if (!allText.includes(qt) && !allText.split(" ").some(t => t.startsWith(qt))) {
      s *= 0.3;
    }
  }
  return s;
}

function buildSnippet(text, queryTokens, maxLen = 180) {
  if (!text) return "";
  const lower = text.toLowerCase();
  let bestIdx = 0;
  for (const qt of queryTokens) {
    const i = lower.indexOf(qt);
    if (i >= 0) { bestIdx = Math.max(0, i - 30); break; }
  }
  let snip = text.slice(bestIdx, bestIdx + maxLen);
  if (bestIdx > 0) snip = "…" + snip;
  if (bestIdx + maxLen < text.length) snip += "…";
  // Highlight
  let html = snip.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  for (const qt of queryTokens) {
    if (qt.length < 2) continue;
    const re = new RegExp(`(${qt.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
    html = html.replace(re, "<mark>$1</mark>");
  }
  return html;
}

async function performSearch(query) {
  const docs = await loadIndex();
  const tokens = tokenize(query);
  if (tokens.length === 0) return [];
  const scored = docs.map(d => ({ doc: d, score: score(d, tokens) }))
                      .filter(x => x.score > 0)
                      .sort((a, b) => b.score - a.score)
                      .slice(0, 30);
  return scored.map(x => ({
    doc: x.doc,
    snippet: buildSnippet(x.doc.text, tokens),
    title_html: buildSnippet(x.doc.chapter_title, tokens, 100),
    section_html: x.doc.section ? buildSnippet(x.doc.section, tokens, 100) : "",
  }));
}

/**
 * Retrieve top-K chunks for a query, returning raw docs (no HTML markup).
 * Used by the tutor RAG pipeline.
 */
async function retrieveChunks(query, k = 4) {
  const docs = await loadIndex();
  const tokens = tokenize(query);
  if (tokens.length === 0) return [];
  return docs.map(d => ({ doc: d, score: score(d, tokens) }))
              .filter(x => x.score > 0)
              .sort((a, b) => b.score - a.score)
              .slice(0, k)
              .map(x => x.doc);
}

window.SearchAPI = { performSearch, retrieveChunks, loadIndex };

function chapterUrl(slug) {
  // Determine relative path from current page to /capitolo/{slug}.html in current lang
  const path = location.pathname;
  if (path.includes("/en/capitolo/")) return `${slug}.html`;
  if (path.includes("/en/")) return `capitolo/${slug}.html`;
  if (path.includes("/capitolo/")) return `${slug}.html`;
  return `capitolo/${slug}.html`;
}

function renderResults(results) {
  const el = document.getElementById("search-results");
  CURRENT_RESULTS = results;
  SELECTED_IDX = results.length > 0 ? 0 : -1;

  if (results.length === 0) {
    el.innerHTML = `<div class="search-empty"><span data-i18n="search.no_results"></span></div>`;
    if (window.I18N) I18N.applyTranslations(el);
    return;
  }

  el.innerHTML = results.map((r, i) => {
    const url = chapterUrl(r.doc.slug);
    const sectionHtml = r.section_html
      ? `<span class="search-section">${r.section_html}</span>`
      : "";
    return `
      <a class="search-result ${i === 0 ? 'selected' : ''}" href="${url}" data-idx="${i}">
        <div class="search-result-head">
          <span class="search-num">${String(r.doc.n).padStart(2, "0")}</span>
          <span class="search-title">${r.title_html}</span>
          ${sectionHtml}
        </div>
        <div class="search-snippet">${r.snippet}</div>
      </a>
    `;
  }).join("");

  // Hover updates selection
  el.querySelectorAll(".search-result").forEach(a => {
    a.addEventListener("mouseenter", () => {
      el.querySelectorAll(".search-result").forEach(x => x.classList.remove("selected"));
      a.classList.add("selected");
      SELECTED_IDX = parseInt(a.dataset.idx, 10);
    });
  });
}

function openSearch() {
  const modal = document.getElementById("search-modal");
  const input = document.getElementById("search-input");
  if (!modal || !input) return;
  modal.hidden = false;
  setTimeout(() => input.focus(), 30);
  // Pre-fetch index in background
  loadIndex();
  // Apply placeholder translation
  input.placeholder = I18N.t("search.placeholder");
  // Show empty results / hint
  document.getElementById("search-results").innerHTML = "";
  CURRENT_RESULTS = [];
  SELECTED_IDX = -1;
}

function closeSearch() {
  const modal = document.getElementById("search-modal");
  if (modal) {
    modal.hidden = true;
    document.getElementById("search-input").value = "";
  }
}

function moveSelection(delta) {
  if (CURRENT_RESULTS.length === 0) return;
  SELECTED_IDX = (SELECTED_IDX + delta + CURRENT_RESULTS.length) % CURRENT_RESULTS.length;
  const el = document.getElementById("search-results");
  el.querySelectorAll(".search-result").forEach((a, i) => {
    a.classList.toggle("selected", i === SELECTED_IDX);
    if (i === SELECTED_IDX) a.scrollIntoView({ block: "nearest" });
  });
}

function activateSelection() {
  if (SELECTED_IDX < 0 || SELECTED_IDX >= CURRENT_RESULTS.length) return;
  const r = CURRENT_RESULTS[SELECTED_IDX];
  location.href = chapterUrl(r.doc.slug);
}

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("search-btn");
  const input = document.getElementById("search-input");
  const modal = document.getElementById("search-modal");

  if (btn) btn.addEventListener("click", openSearch);

  // Keyboard: Cmd/Ctrl+K opens; "/" opens (when not in input); Esc closes
  document.addEventListener("keydown", (e) => {
    const isInput = ["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName);
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openSearch();
      return;
    }
    if (e.key === "/" && !isInput && modal && modal.hidden) {
      e.preventDefault();
      openSearch();
      return;
    }
    if (e.key === "Escape" && modal && !modal.hidden) {
      closeSearch();
    }
    if (modal && !modal.hidden) {
      if (e.key === "ArrowDown") { e.preventDefault(); moveSelection(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); moveSelection(-1); }
      else if (e.key === "Enter") { e.preventDefault(); activateSelection(); }
    }
  });

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeSearch();
    });
  }

  // Debounced search-on-type
  let timer = null;
  if (input) {
    input.addEventListener("input", () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (!q) {
        document.getElementById("search-results").innerHTML = "";
        CURRENT_RESULTS = [];
        return;
      }
      timer = setTimeout(async () => {
        const results = await performSearch(q);
        renderResults(results);
      }, 80);
    });
  }
});

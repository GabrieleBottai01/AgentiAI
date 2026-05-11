// =============================================================
// App — theme, lang, provider modal, mobile menu
// =============================================================

const THEME_STORAGE = "site_theme";

// ---- Theme ----
function getTheme() {
  return localStorage.getItem(THEME_STORAGE) || (
    matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
  );
}
function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem(THEME_STORAGE, theme);
  refreshThemeButton();
}
function toggleTheme() {
  setTheme(getTheme() === "dark" ? "light" : "dark");
}
function refreshThemeButton() {
  const btn = document.getElementById("theme-btn");
  if (!btn) return;
  const theme = getTheme();
  btn.innerHTML = IconLib.icon(theme === "dark" ? "sun" : "moon");
  btn.title = I18N.t("theme.toggle");
}

// Init theme as early as possible to avoid FOUC
(function initTheme() {
  const t = localStorage.getItem(THEME_STORAGE);
  if (t) document.documentElement.setAttribute("data-theme", t);
})();

// ---- Lang ----
function refreshLangButton() {
  const btn = document.getElementById("lang-btn");
  if (!btn) return;
  const lang = I18N.getLang();
  btn.textContent = lang.toUpperCase();
  btn.title = I18N.t("lang.toggle");
}
function toggleLang() {
  // Each page has a <meta name="lang-toggle-url"> with the URL to navigate to
  // when switching languages. We navigate there (the new page is in the other language).
  const target = document.querySelector('meta[name="lang-toggle-url"]')?.content;
  if (target) {
    // Persist the user's preference so future visits to other pages adapt too
    const currentLang = I18N.getLang();
    const newLang = currentLang === "it" ? "en" : "it";
    localStorage.setItem("site_language", newLang);
    location.href = target;
    return;
  }
  // Fallback: just toggle UI strings (legacy behavior)
  const cur = localStorage.getItem("site_language") || "it";
  I18N.setLang(cur === "it" ? "en" : "it");
  refreshLangButton();
  refreshProviderButton();
  ["pg-model", "ag-model"].forEach(id => {
    const el = document.getElementById(id);
    if (el && window.appHelpers?.populateModelSelect) appHelpers.populateModelSelect(el);
  });
  ["pg-provider", "ag-provider"].forEach(id => refreshProviderLine(id));
}

// ---- Provider modal ----
function refreshProviderButton() {
  const btn = document.getElementById("api-key-btn");
  const status = document.getElementById("key-status");
  if (!btn) return;

  const active = AI.getActive();
  const iconHtml = IconLib.icon("key");
  if (active.key) {
    btn.classList.add("set");
    const providerName = active.info.label.split(" ")[0]; // "Gemini" or "Claude"
    status.innerHTML = `${iconHtml} ${I18N.t("key.set", { provider: providerName })}`;
  } else {
    btn.classList.remove("set");
    status.innerHTML = `${iconHtml} ${I18N.t("key.unset")}`;
  }
}

function buildProviderCards() {
  const container = document.getElementById("provider-cards");
  if (!container) return;
  container.innerHTML = "";

  const active = AI.getActive();

  Object.values(AI.providers).forEach(p => {
    const isActive = active.name === p.name;
    const savedKey = AI.getKey(p.name);
    const pricingKey = p.pricing === "free" ? "pc.free" : "pc.paid";

    const card = document.createElement("div");
    card.className = `provider-card ${isActive ? "selected" : ""} ${p.pricing}`;
    card.dataset.provider = p.name;
    card.innerHTML = `
      <div class="pc-header">
        <span class="pc-badge ${p.pricing}">
          ${IconLib.icon(p.pricing === "free" ? "gift" : "credit-card")}
          ${I18N.t(pricingKey)}
        </span>
        ${isActive ? `<span class="pc-active">${IconLib.icon("check")} ${I18N.t("pc.active")}</span>` : ''}
      </div>
      <h3 class="pc-title">${p.label}</h3>
      <p class="pc-desc">${p.description}</p>
      <p class="pc-link">
        ${I18N.t("pc.create")}<br>
        <a href="${p.consoleUrl}" target="_blank" rel="noopener">
          ${p.consoleLabel} ${IconLib.icon("external-link")}
        </a>
      </p>
      <label class="pc-input-label">
        <span>${I18N.t("pc.input.label", { prefix: `<code>${p.keyPrefix}</code>` })}</span>
        <input type="password" class="pc-input" data-provider="${p.name}"
               placeholder="${p.keyPrefix}..."
               value="${savedKey}">
      </label>
      <div class="pc-actions">
        <button type="button" class="btn btn-ghost pc-clear" data-provider="${p.name}">
          ${IconLib.icon("trash")} ${I18N.t("pc.remove")}
        </button>
        <button type="button" class="btn ${isActive ? 'btn-ghost' : 'btn-primary'} pc-use" data-provider="${p.name}">
          ${isActive
            ? `${IconLib.icon("check")} ${I18N.t("pc.inuse")}`
            : `${I18N.t("pc.use")} ${p.label.split(" ")[0]}`}
        </button>
      </div>
    `;
    container.appendChild(card);
  });

  container.querySelectorAll(".pc-use").forEach(b => {
    b.addEventListener("click", () => {
      const provider = b.dataset.provider;
      const input = container.querySelector(`.pc-input[data-provider="${provider}"]`);
      const key = input.value.trim();
      const info = AI.providers[provider];

      if (!key) {
        input.focus();
        input.style.borderColor = "var(--danger)";
        setTimeout(() => { input.style.borderColor = ""; }, 2000);
        return;
      }
      if (!key.startsWith(info.keyPrefix)) {
        if (!confirm(`Key doesn't start with '${info.keyPrefix}'. Save anyway?`)) return;
      }
      AI.setKey(provider, key);
      AI.setActive(provider);
      closeKeyModal();
      refreshProviderButton();
      window.dispatchEvent(new CustomEvent("ai-provider-changed"));
    });
  });

  container.querySelectorAll(".pc-clear").forEach(b => {
    b.addEventListener("click", () => {
      AI.setKey(b.dataset.provider, "");
      buildProviderCards();
      refreshProviderButton();
    });
  });
}

function openKeyModal() {
  buildProviderCards();
  document.getElementById("api-key-modal").hidden = false;
}
function closeKeyModal() { document.getElementById("api-key-modal").hidden = true; }

function ensureApiKey() {
  if (!AI.hasValidActive()) {
    openKeyModal();
    return false;
  }
  return true;
}

// ---- File:// banner ----
function showFileProtocolBanner() {
  if (location.protocol !== "file:") return;
  if (document.getElementById("file-banner")) return;
  const banner = document.createElement("div");
  banner.id = "file-banner";
  banner.style.cssText = "background:var(--warning-soft);border-bottom:2px solid var(--warning);padding:12px 20px;font-size:14px;color:var(--warning);text-align:center;";
  banner.innerHTML = `${IconLib.icon("alert-triangle")} <b>file://</b> — AI calls will be blocked by CORS. Run <code>Avvia-sito.command</code> to start a local server.`;
  document.body.insertBefore(banner, document.body.firstChild);
}

// ---- Mobile drawer ----
function initMobileDrawer() {
  const btn = document.getElementById("mobile-menu-btn");
  const drawer = document.getElementById("mobile-drawer");
  if (!btn || !drawer) return;
  btn.addEventListener("click", () => drawer.classList.add("open"));
  drawer.addEventListener("click", (e) => {
    if (e.target === drawer) drawer.classList.remove("open");
  });
  drawer.querySelectorAll("a").forEach(a => {
    a.addEventListener("click", () => drawer.classList.remove("open"));
  });
}

// ---- Markdown renderer ----
function renderMarkdown(md) {
  if (!md) return "";
  let s = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  s = s.replace(/```(\w+)?\n([\s\S]*?)```/g, (m, lang, code) => {
    return `<pre><code>${code.replace(/\n$/, "")}</code></pre>`;
  });

  s = s.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  s = s.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  s = s.replace(/^# (.+)$/gm, "<h1>$1</h1>");

  s = s.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  s = s.replace(/(?<!\*)\*(?!\*)([^*\n]+)\*/g, "<i>$1</i>");
  s = s.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  s = s.replace(/(?:^|\n)(- .+(?:\n- .+)*)/g, (m, list) => {
    const items = list.trim().split("\n").map(l => `<li>${l.replace(/^- /, "")}</li>`).join("");
    return `\n<ul>${items}</ul>`;
  });
  s = s.replace(/(?:^|\n)((?:\d+\. .+)(?:\n\d+\. .+)*)/g, (m, list) => {
    const items = list.trim().split("\n").map(l => `<li>${l.replace(/^\d+\. /, "")}</li>`).join("");
    return `\n<ol>${items}</ol>`;
  });

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

// Populate model select for the active provider
function populateModelSelect(selectEl) {
  if (!selectEl) return;
  const active = AI.getActive();
  selectEl.innerHTML = "";
  active.info.models.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = m.label;
    if (m.default) opt.selected = true;
    selectEl.appendChild(opt);
  });
}

// Render the provider line (es. "Provider attivo: Gemini · cambia") in a given element
function refreshProviderLine(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  const a = AI.getActive();
  const iconName = a.info.pricing === "free" ? "gift" : "credit-card";
  el.innerHTML = `${IconLib.icon(iconName)} <span>${I18N.t("provider.active")}</span> <b>${a.info.label}</b> <span style="opacity:.5">·</span> <a href="#" id="${elId}-change">${I18N.t("provider.change")}</a>`;
  const link = document.getElementById(`${elId}-change`);
  if (link) link.addEventListener("click", e => { e.preventDefault(); openKeyModal(); });
}

// ---- Init ----
document.addEventListener("DOMContentLoaded", () => {
  showFileProtocolBanner();

  // Theme & lang buttons
  refreshThemeButton();
  refreshLangButton();
  document.getElementById("theme-btn")?.addEventListener("click", toggleTheme);
  document.getElementById("lang-btn")?.addEventListener("click", toggleLang);

  // Provider button
  refreshProviderButton();
  document.getElementById("api-key-btn")?.addEventListener("click", openKeyModal);

  // Modal
  const modal = document.getElementById("api-key-modal");
  if (modal) {
    modal.addEventListener("click", (e) => { if (e.target === modal) closeKeyModal(); });
    document.getElementById("modal-close")?.addEventListener("click", closeKeyModal);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !modal.hidden) closeKeyModal();
    });
  }

  initMobileDrawer();
});

window.appHelpers = { renderMarkdown, ensureApiKey, openKeyModal, populateModelSelect, refreshProviderLine };

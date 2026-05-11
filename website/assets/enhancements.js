// =============================================================
// UX enhancements — code copy buttons, mobile chapter selector, share
// Activated automatically on chapter pages.
// =============================================================

// ---- Copy button on every <pre><code> ----
function attachCopyButtons() {
  document.querySelectorAll(".chapter-content pre, .markdown-output pre").forEach(pre => {
    if (pre.dataset.copyAttached) return;
    pre.dataset.copyAttached = "1";
    pre.style.position = "relative";
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.setAttribute("aria-label", "Copy");
    btn.innerHTML = IconLib ? IconLib.icon("copy") : "Copy";
    btn.addEventListener("click", async () => {
      const code = pre.querySelector("code") || pre;
      const text = code.innerText;
      try {
        await navigator.clipboard.writeText(text);
        btn.classList.add("copied");
        btn.innerHTML = IconLib ? IconLib.icon("check") : "✓";
        setTimeout(() => {
          btn.classList.remove("copied");
          btn.innerHTML = IconLib ? IconLib.icon("copy") : "Copy";
        }, 1500);
      } catch (e) {
        console.warn("Copy failed:", e);
      }
    });
    pre.appendChild(btn);
  });
}

// ---- Mobile chapter selector ----
function buildMobileChapterSelector() {
  const sidebarList = document.querySelector(".sidebar .sidebar-list");
  if (!sidebarList) return;
  const article = document.querySelector(".chapter");
  if (!article) return;
  if (article.querySelector(".mobile-ch-select")) return;

  const select = document.createElement("select");
  select.className = "mobile-ch-select";

  // Optional placeholder option
  const lang = document.documentElement.lang || "it";
  const placeholder = document.createElement("option");
  placeholder.disabled = true;
  placeholder.textContent = lang === "en" ? "Jump to chapter…" : "Vai al capitolo…";
  select.appendChild(placeholder);

  sidebarList.querySelectorAll("li").forEach(li => {
    const a = li.querySelector("a");
    if (!a) return;
    const num = li.querySelector(".num")?.textContent.trim() || "";
    const title = li.querySelector(".title")?.textContent.trim() || "";
    const opt = document.createElement("option");
    opt.value = a.getAttribute("href");
    opt.textContent = `${num}. ${title}`;
    if (li.classList.contains("current")) opt.selected = true;
    select.appendChild(opt);
  });

  select.addEventListener("change", () => {
    if (select.value) location.href = select.value;
  });

  // Insert at top of article (after breadcrumb)
  const breadcrumb = article.querySelector(".breadcrumb");
  if (breadcrumb) breadcrumb.after(select);
  else article.prepend(select);
}

// ---- Share buttons on chapters ----
function buildShareButtons() {
  const article = document.querySelector(".chapter");
  if (!article) return;
  if (article.querySelector(".share-buttons")) return;

  const url = location.href;
  const titleEl = article.querySelector(".chapter-content h1");
  const title = titleEl ? titleEl.textContent.trim() : document.title;
  const author = "@bottai_gabriele";
  const lang = document.documentElement.lang || "it";

  const tweetText = encodeURIComponent(
    `${title} — ${lang === "en" ? "Guide to AI Agents" : "Guida agli Agenti AI"} by ${author}`
  );
  const tweetUrl = `https://twitter.com/intent/tweet?text=${tweetText}&url=${encodeURIComponent(url)}`;
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;

  const labels = lang === "en"
    ? { share: "Share this chapter:", copy: "Copy link", copied: "Copied!" }
    : { share: "Condividi questo capitolo:", copy: "Copia link", copied: "Copiato!" };

  const wrap = document.createElement("div");
  wrap.className = "share-buttons";
  wrap.innerHTML = `
    <span class="share-label">${labels.share}</span>
    <a href="${tweetUrl}" target="_blank" rel="noopener" class="share-btn" aria-label="Twitter">
      <svg class="icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    </a>
    <a href="${linkedinUrl}" target="_blank" rel="noopener" class="share-btn" aria-label="LinkedIn">
      <svg class="icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.852 3.37-1.852 3.601 0 4.267 2.37 4.267 5.455v6.288zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.063 2.063 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
      </svg>
    </a>
    <button type="button" class="share-btn share-copy" data-url="${url}" aria-label="${labels.copy}">
      <i data-icon-replace="copy"></i>
      <span class="share-copy-label">${labels.copy}</span>
    </button>
  `;

  // Insert before chapter-nav
  const nav = article.querySelector(".chapter-nav");
  if (nav) nav.before(wrap);
  else article.appendChild(wrap);

  // Wire copy
  const copyBtn = wrap.querySelector(".share-copy");
  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(copyBtn.dataset.url);
      copyBtn.classList.add("copied");
      copyBtn.querySelector(".share-copy-label").textContent = labels.copied;
      setTimeout(() => {
        copyBtn.classList.remove("copied");
        copyBtn.querySelector(".share-copy-label").textContent = labels.copy;
      }, 1500);
    } catch (e) {
      console.warn("Copy failed:", e);
    }
  });

  // Apply icons to the button (so the copy icon renders)
  if (window.IconLib) IconLib.applyIcons(wrap);
}

document.addEventListener("DOMContentLoaded", () => {
  attachCopyButtons();
  buildMobileChapterSelector();
  buildShareButtons();
});

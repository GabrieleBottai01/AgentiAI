"""
Build statico del sito (no backend) — bilingue IT + EN.

Genera tutto in ./dist/:
  - dist/index.html, dist/capitolo/*.html, dist/playground.html, ...   (IT)
  - dist/en/index.html, dist/en/capitolo/*.html, dist/en/...           (EN)
  - dist/search-index-it.json, dist/search-index-en.json               (search)
  - dist/Avvia-sito.command                                            (launcher)

Le chiavi API restano nel browser (localStorage) e vanno direttamente a
api.anthropic.com / generativelanguage.googleapis.com.

Uso: python3 build_site.py
"""

import re
import json
import shutil
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "website"
SITE = ROOT / "site"

# ---------------------------------------------------------------------------
# Chapter manifest — bilingual titles
# ---------------------------------------------------------------------------
CHAPTERS = [
    {"n": 1, "slug": "01-cosa-sono-gli-agenti-ai",
     "title_it": "Cosa sono gli Agenti AI",
     "title_en": "What AI Agents Are", "part_key": "toc.part.1"},
    {"n": 2, "slug": "02-come-funzionano-gli-llm",
     "title_it": "Come funzionano gli LLM",
     "title_en": "How LLMs Work", "part_key": "toc.part.1"},
    {"n": 3, "slug": "03-anatomia-di-un-agente",
     "title_it": "Anatomia di un agente",
     "title_en": "Anatomy of an Agent", "part_key": "toc.part.1"},
    {"n": 4, "slug": "04-tipi-di-agenti-e-architetture",
     "title_it": "Tipi di agenti e architetture",
     "title_en": "Types of Agents and Architectures", "part_key": "toc.part.1"},
    {"n": 5, "slug": "05-prompt-engineering",
     "title_it": "Prompt engineering",
     "title_en": "Prompt Engineering", "part_key": "toc.part.2"},
    {"n": 6, "slug": "06-tool-use-e-function-calling",
     "title_it": "Tool use e function calling",
     "title_en": "Tool Use and Function Calling", "part_key": "toc.part.2"},
    {"n": 7, "slug": "07-memoria-contesto-e-rag",
     "title_it": "Memoria, contesto e RAG",
     "title_en": "Memory, Context and RAG", "part_key": "toc.part.2"},
    {"n": 8, "slug": "08-usare-i-chatbot-ai",
     "title_it": "Usare i chatbot AI",
     "title_en": "Using AI Chatbots", "part_key": "toc.part.3"},
    {"n": 9, "slug": "09-claude-code-per-sviluppatori",
     "title_it": "Claude Code per sviluppatori",
     "title_en": "Claude Code for Developers", "part_key": "toc.part.3"},
    {"n": 10, "slug": "10-costruire-agenti-con-api-sdk",
     "title_it": "Costruire agenti con API e SDK",
     "title_en": "Building Agents with API and SDK", "part_key": "toc.part.4"},
    {"n": 11, "slug": "11-framework-langchain-autogen-crewai",
     "title_it": "Framework: LangChain, AutoGen, CrewAI",
     "title_en": "Frameworks: LangChain, AutoGen, CrewAI", "part_key": "toc.part.4"},
    {"n": 12, "slug": "12-best-practice-sviluppo-con-agenti",
     "title_it": "Best practice di sviluppo",
     "title_en": "Best Practices for Development", "part_key": "toc.part.5"},
    {"n": 13, "slug": "13-sicurezza-costi-e-limiti",
     "title_it": "Sicurezza, costi, limiti",
     "title_en": "Security, Costs, Limits", "part_key": "toc.part.5"},
    {"n": 14, "slug": "14-valutazione-e-miglioramento",
     "title_it": "Valutazione e miglioramento",
     "title_en": "Evaluation and Improvement", "part_key": "toc.part.5"},
    {"n": 15, "slug": "15-casi-uso-e-workflow-reali",
     "title_it": "Casi d'uso e workflow reali",
     "title_en": "Real Use Cases and Workflows", "part_key": "toc.part.6"},
    {"n": 16, "slug": "16-glossario-e-risorse",
     "title_it": "Glossario e risorse",
     "title_en": "Glossary and Resources", "part_key": "toc.part.6"},
]

EXERCISES = {
    1: {
        "id": "ex-cap1",
        "type": "classify",
        "title_it": "Esercizio: agente o chatbot?",
        "title_en": "Exercise: agent or chatbot?",
        "intro_it": "Per ognuna delle descrizioni, decidi se è un <b>agente</b>, un <b>chatbot</b> o un'<b>automazione con AI</b>. Poi premi 'Verifica' per il giudizio del tutor AI.",
        "intro_en": "For each description, decide whether it's an <b>agent</b>, a <b>chatbot</b> or an <b>AI automation</b>. Then press 'Verify' for AI tutor feedback.",
        "cases_it": [
            "Un assistente che, dato un bug report, esplora il codebase, propone una fix, scrive i test e apre la PR.",
            "Un'integrazione che traduce automaticamente i messaggi quando ne arriva uno in lingua diversa.",
            "Un copilota che risponde a domande sulla cucina italiana e suggerisce ricette.",
        ],
        "cases_en": [
            "An assistant that, given a bug report, explores the codebase, proposes a fix, writes tests and opens the PR.",
            "An integration that automatically translates messages when one arrives in a different language.",
            "A copilot that answers questions about Italian cuisine and suggests recipes.",
        ],
        "options_it": ["Agente", "Chatbot", "Automazione con AI"],
        "options_en": ["Agent", "Chatbot", "AI Automation"],
    },
    5: {
        "id": "ex-cap5",
        "type": "improve_prompt",
        "title_it": "Esercizio: migliora questo prompt",
        "title_en": "Exercise: improve this prompt",
        "intro_it": "Il prompt qui sotto è generico. Riscrivilo seguendo i criteri del capitolo (ruolo, obiettivo, vincoli, formato, esempi). Poi premi 'Valuta' per ricevere il feedback dell'AI.",
        "intro_en": "The prompt below is generic. Rewrite it following the chapter's criteria (role, goal, constraints, format, examples). Then press 'Verify' to get AI feedback.",
        "starter_it": "Riassumi il testo che ti mando.",
        "starter_en": "Summarize the text I send you.",
    },
    6: {
        "id": "ex-cap6",
        "type": "design_tool",
        "title_it": "Esercizio: progetta un tool",
        "title_en": "Exercise: design a tool",
        "intro_it": "Immagina un agente che prenota voli. Scrivi la <b>definizione di un tool</b> (nome, descrizione, schema parametri) seguendo le linee guida del capitolo.",
        "intro_en": "Imagine an agent that books flights. Write the <b>tool definition</b> (name, description, parameter schema) following the chapter's guidelines.",
        "starter_it": '{\n  "name": "search_flights",\n  "description": "...",\n  "input_schema": {\n    "type": "object",\n    "properties": {\n      ...\n    },\n    "required": [...]\n  }\n}',
        "starter_en": '{\n  "name": "search_flights",\n  "description": "...",\n  "input_schema": {\n    "type": "object",\n    "properties": {\n      ...\n    },\n    "required": [...]\n  }\n}',
    },
}


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------
def md_to_html(text: str) -> str:
    text = re.sub(r"\n→ \[.*?\]\(.*?\)\s*$", "", text, flags=re.DOTALL)
    text = re.sub(r"\n← \[.*?\]\(.*?\)\s*$", "", text, flags=re.DOTALL)
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "sane_lists", "nl2br", "codehilite", "toc"],
        extension_configs={
            "codehilite": {"css_class": "codehilite", "guess_lang": False},
            "toc": {"permalink": False},
        },
    )


def get_chapter_md(slug: str, lang: str):
    if lang == "it":
        path = ROOT / f"{slug}.md"
    else:
        path = ROOT / "en" / f"{slug}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Search index
# ---------------------------------------------------------------------------
def extract_search_docs(md_text: str, slug: str, n: int, title: str, lang: str) -> list[dict]:
    """Split markdown into searchable section docs (one per ## heading)."""
    # Strip code blocks and HTML for cleaner search
    text = re.sub(r"```.*?```", "", md_text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)

    # Split on H2 sections
    sections = re.split(r"\n## ", text)
    docs = []
    # First section: chapter intro (everything before first ##)
    intro = sections[0].strip()
    intro = re.sub(r"^# .*$", "", intro, flags=re.MULTILINE).strip()
    if intro:
        docs.append({
            "slug": slug, "n": n, "lang": lang,
            "chapter_title": title, "section": "",
            "text": intro[:600],
        })
    for sec in sections[1:]:
        lines = sec.split("\n", 1)
        section_title = lines[0].strip()
        section_body = lines[1].strip() if len(lines) > 1 else ""
        # collapse whitespace
        section_body = re.sub(r"\s+", " ", section_body)[:600]
        docs.append({
            "slug": slug, "n": n, "lang": lang,
            "chapter_title": title, "section": section_title,
            "text": section_body,
        })
    return docs


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
SITE_BASE_URL = "https://myfirstaiagent.netlify.app"  # Update if you migrate to a custom domain

def og_meta(lang: str, page_title: str, description: str, url_path: str, og_type: str = "website") -> str:
    """Generate Open Graph + Twitter Card meta tags."""
    full_url = f"{SITE_BASE_URL}{url_path}"
    image_url = f"{SITE_BASE_URL}/og-image.png"  # User can add a 1200x630 image here
    locale = "it_IT" if lang == "it" else "en_US"
    return f'''<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{locale}">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{full_url}">
<meta property="og:image" content="{image_url}">
<meta property="og:site_name" content="Guida agli Agenti AI">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page_title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image_url}">
<link rel="canonical" href="{full_url}">'''


def jsonld_article(lang: str, page_title: str, description: str, url_path: str) -> str:
    """JSON-LD structured data for article-style pages."""
    full_url = f"{SITE_BASE_URL}{url_path}"
    schema = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": page_title,
        "description": description,
        "url": full_url,
        "inLanguage": lang,
        "author": {
            "@type": "Person",
            "name": "Gabriele Bottai",
            "url": f"{SITE_BASE_URL}/about.html"
        },
        "publisher": {
            "@type": "Person",
            "name": "Gabriele Bottai"
        },
        "datePublished": "2026-05-01",
        "dateModified": "2026-05-07",
        "isPartOf": {
            "@type": "Book",
            "name": "Guida agli Agenti AI" if lang == "it" else "Guide to AI Agents",
            "author": "Gabriele Bottai"
        }
    }
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'


def base_html(body: str, lang: str, title_key: str = "site.title", extra_scripts: str = "",
              active: str = "", asset_prefix: str = "", lang_toggle_url: str = "",
              page_title: str = "", page_description: str = "", url_path: str = "",
              og_type: str = "website", include_jsonld: bool = False) -> str:
    """
    asset_prefix: relative path to dist/assets/ (e.g. "" for root, "../" for /capitolo/, "../../" for /en/capitolo/)
    lang_toggle_url: where the lang toggle button should navigate to switch languages
    page_title/page_description: for SEO meta tags
    url_path: absolute path on the site (for canonical / OG url)
    """
    # Defaults for page metadata
    if not page_title:
        page_title = "Guida agli Agenti AI" if lang == "it" else "Guide to AI Agents"
    if not page_description:
        page_description = (
            "Guida completa, in italiano e inglese, agli Agenti AI — di Gabriele Bottai. "
            "16 capitoli, esercizi interattivi, strumenti AI integrati."
            if lang == "it" else
            "Complete guide, in Italian and English, to AI Agents — by Gabriele Bottai. "
            "16 chapters, interactive exercises, integrated AI tools."
        )

    seo_meta = og_meta(lang, page_title, page_description, url_path, og_type)
    jsonld = jsonld_article(lang, page_title, page_description, url_path) if include_jsonld else ""
    nav_items = [
        ("home", "index.html", "home", "nav.home"),
        ("chapters", "capitolo/01-cosa-sono-gli-agenti-ai.html", "book-open", "nav.chapters"),
        ("playground", "playground.html", "flask", "nav.playground"),
        ("agent", "agente.html", "bot", "nav.agent"),
        ("tutor", "tutor.html", "message-circle", "nav.tutor"),
    ]
    # Path prefix for in-language links (relative to current page)
    inlang_prefix = "../" if active == "chapters" else ""
    nav_html = "".join(
        f'<a href="{inlang_prefix}{href}" class="{"active" if active==key else ""}">'
        f'<i data-icon-replace="{icon}"></i><span data-i18n="{i18n}"></span></a>'
        for key, href, icon, i18n in nav_items
    )
    drawer_html = "".join(
        f'<a href="{inlang_prefix}{href}"><i data-icon-replace="{icon}"></i><span data-i18n="{i18n}"></span></a>'
        for _, href, icon, i18n in nav_items
    )

    html_lang = lang
    return f"""<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="i18n-title" content="{title_key}">
<meta name="page-lang" content="{lang}">
<meta name="lang-toggle-url" content="{lang_toggle_url}">
<title>{page_title}</title>
<meta name="description" content="{page_description}">
<meta name="author" content="Gabriele Bottai">
{seo_meta}
{jsonld}
<link rel="icon" type="image/svg+xml" href="{asset_prefix}favicon.svg">
<link rel="stylesheet" href="{asset_prefix}assets/style.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>
(function(){{
  var t = localStorage.getItem("site_theme");
  if (t) document.documentElement.setAttribute("data-theme", t);
}})();
</script>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <a href="{asset_prefix}index.html" class="brand">
      <span class="brand-mark"><i data-icon-replace="hexagon"></i></span>
      <span class="brand-text" data-i18n="site.title">Guida agli Agenti AI</span>
    </a>
    <nav class="topnav">{nav_html}</nav>
    <div class="topbar-actions">
      <button id="search-btn" class="icon-btn" type="button" aria-label="Search" title="⌘K">
        <i data-icon-replace="search"></i>
      </button>
      <button id="theme-btn" class="icon-btn" type="button" aria-label="Toggle theme"></button>
      <button id="lang-btn" class="icon-btn lang-btn" type="button" aria-label="Toggle language">{lang.upper()}</button>
      <button id="api-key-btn" class="key-btn" type="button">
        <span id="key-status"></span>
      </button>
      <button id="mobile-menu-btn" class="icon-btn mobile-menu-btn" type="button" aria-label="Menu">
        <i data-icon-replace="menu"></i>
      </button>
    </div>
  </div>
</header>

<div id="mobile-drawer" class="mobile-drawer">
  <div class="mobile-drawer-inner">
    {drawer_html}
  </div>
</div>

<div id="api-key-modal" class="modal-overlay" hidden>
  <div class="modal modal-lg">
    <div class="modal-head">
      <div>
        <h2 data-i18n="modal.title">Configura il provider AI</h2>
        <p class="modal-sub" data-i18n="modal.subtitle"></p>
      </div>
      <button id="modal-close" type="button" class="modal-x" aria-label="Close">
        <i data-icon-replace="x"></i>
      </button>
    </div>
    <div id="provider-cards" class="provider-cards"></div>
    <p class="hint">
      <i data-icon-replace="lightbulb"></i>
      <span data-i18n="modal.hint"></span>
    </p>
  </div>
</div>

<div id="search-modal" class="modal-overlay" hidden>
  <div class="modal search-modal">
    <div class="search-input-wrap">
      <i data-icon-replace="search"></i>
      <input id="search-input" type="text" placeholder="" autocomplete="off">
      <kbd class="kbd-esc">esc</kbd>
    </div>
    <div id="search-results" class="search-results"></div>
    <div class="search-footer">
      <span class="muted small">
        <span data-i18n="search.hint"></span>
      </span>
    </div>
  </div>
</div>

<main class="main">
{body}
</main>

<footer class="footer">
  <div class="footer-inner">
    <span data-i18n="footer.copyright"></span>
    <span class="footer-links">
      <a href="{asset_prefix}about.html" data-i18n="footer.about">About</a> ·
      <a href="https://gabrielebottai.netlify.app/" target="_blank" rel="noopener">Portfolio</a> ·
      <a href="https://github.com/GabrieleBottai01" target="_blank" rel="noopener">GitHub</a>
    </span>
  </div>
</footer>

<script src="{asset_prefix}assets/icons.js"></script>
<script src="{asset_prefix}assets/i18n.js"></script>
<script src="{asset_prefix}assets/ai-client.js"></script>
<script src="{asset_prefix}assets/app.js"></script>
<script src="{asset_prefix}assets/search.js"></script>
{extra_scripts}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Page renderers
# ---------------------------------------------------------------------------
def render_index(lang: str) -> str:
    parts_html = ""
    for part_key in ["toc.part.1", "toc.part.2", "toc.part.3", "toc.part.4", "toc.part.5", "toc.part.6"]:
        cards = ""
        for ch in CHAPTERS:
            if ch["part_key"] != part_key:
                continue
            title = ch["title_it"] if lang == "it" else ch["title_en"]
            cards += f"""<a class="ch-card" href="capitolo/{ch['slug']}.html">
              <span class="ch-num">{ch['n']:02d}</span>
              <span class="ch-title">{title}</span>
            </a>"""
        parts_html += f"""<div class="part">
          <h3 data-i18n="{part_key}"></h3>
          <div class="part-grid">{cards}</div>
        </div>"""

    pdf_link = "../Guida-Agenti-AI.pdf" if lang == "en" else "Guida-Agenti-AI.pdf"
    if lang == "en":
        pdf_link = "../Guide-AI-Agents-EN.pdf"

    body = f"""<section class="hero">
  <div class="hero-inner">
    <span class="eyebrow">
      <i data-icon-replace="sparkles"></i>
      <span data-i18n="hero.eyebrow"></span>
    </span>
    <h1>
      <span data-i18n="hero.title.before"></span>
      <span class="accent" data-i18n="hero.title.accent"></span>
      <span data-i18n="hero.title.after"></span>
    </h1>
    <p class="lead" data-i18n="hero.lead"></p>
    <div class="hero-cta">
      <a href="capitolo/01-cosa-sono-gli-agenti-ai.html" class="btn btn-accent btn-lg">
        <span data-i18n="hero.cta.start"></span>
        <i data-icon-replace="arrow-right"></i>
      </a>
      <a href="playground.html" class="btn btn-ghost btn-lg">
        <i data-icon-replace="flask"></i>
        <span data-i18n="hero.cta.playground"></span>
      </a>
    </div>
    <div class="hero-free">
      <i data-icon-replace="gift"></i>
      <div>
        <b data-i18n="hero.free.title">Provala gratis:</b>
        <span data-i18n="hero.free.body"></span>
      </div>
    </div>
    <div class="hero-meta">
      <span data-i18n="hero.meta.author"></span>
      <span data-i18n="hero.meta.edition"></span>
      <a href="{pdf_link}" data-i18n="hero.meta.pdf"></a>
    </div>
  </div>
</section>

<section class="features">
  <div class="feature-card">
    <div class="feature-icon"><i data-icon-replace="message-circle"></i></div>
    <h3 data-i18n="features.tutor.title"></h3>
    <p data-i18n="features.tutor.desc"></p>
    <a href="tutor.html" class="link-arrow">
      <span data-i18n="features.tutor.cta"></span>
      <i data-icon-replace="arrow-right"></i>
    </a>
  </div>
  <div class="feature-card">
    <div class="feature-icon"><i data-icon-replace="flask"></i></div>
    <h3 data-i18n="features.playground.title"></h3>
    <p data-i18n="features.playground.desc"></p>
    <a href="playground.html" class="link-arrow">
      <span data-i18n="features.playground.cta"></span>
      <i data-icon-replace="arrow-right"></i>
    </a>
  </div>
  <div class="feature-card">
    <div class="feature-icon"><i data-icon-replace="bot"></i></div>
    <h3 data-i18n="features.agent.title"></h3>
    <p data-i18n="features.agent.desc"></p>
    <a href="agente.html" class="link-arrow">
      <span data-i18n="features.agent.cta"></span>
      <i data-icon-replace="arrow-right"></i>
    </a>
  </div>
</section>

<section class="toc">
  <h2 data-i18n="toc.title"></h2>
  <p class="muted" data-i18n="toc.subtitle"></p>
  {parts_html}
</section>"""

    asset_prefix = "../" if lang == "en" else ""
    toggle_url = "en/index.html" if lang == "it" else "../index.html"
    url_path = "/en/" if lang == "en" else "/"
    return base_html(body, lang, title_key="site.title", active="home",
                       asset_prefix=asset_prefix, lang_toggle_url=toggle_url,
                       url_path=url_path, include_jsonld=True)


def render_chapter(ch: dict, html_content: str, prev_ch, next_ch, lang: str) -> str:
    title_key = "title_it" if lang == "it" else "title_en"
    sidebar_items = ""
    for c in CHAPTERS:
        cls = "current" if c["n"] == ch["n"] else ""
        sidebar_items += f"""<li class="{cls}"><a href="{c['slug']}.html">
          <span class="num">{c['n']:02d}</span><span class="title">{c[title_key]}</span>
        </a></li>"""

    exercise = EXERCISES.get(ch["n"])
    exercise_html = ""
    if exercise:
        ex_title = exercise[f"title_{lang}"]
        ex_intro = exercise[f"intro_{lang}"]
        if exercise["type"] == "classify":
            cases_html = ""
            cases = exercise[f"cases_{lang}"]
            options = exercise[f"options_{lang}"]
            values = ["agente", "chatbot", "automazione"]
            for i, case in enumerate(cases):
                cases_html += f"""<li>
                  <p>{case}</p>
                  <div class="choice-row">
                    <label><input type="radio" name="item-{i}" value="{values[0]}"> {options[0]}</label>
                    <label><input type="radio" name="item-{i}" value="{values[1]}"> {options[1]}</label>
                    <label><input type="radio" name="item-{i}" value="{values[2]}"> {options[2]}</label>
                  </div>
                </li>"""
            exercise_input = f'<ol class="exercise-items">{cases_html}</ol>'
        elif exercise["type"] == "improve_prompt":
            starter = exercise[f"starter_{lang}"]
            exercise_input = f'<textarea class="exercise-input" rows="8">{starter}</textarea>'
        elif exercise["type"] == "design_tool":
            starter = exercise[f"starter_{lang}"]
            exercise_input = f'<textarea class="exercise-input mono" rows="14">{starter}</textarea>'
        else:
            exercise_input = ""

        exercise_html = f"""<section class="exercise"
                 data-exercise-id="{exercise['id']}"
                 data-exercise-type="{exercise['type']}">
          <div class="exercise-header">
            <span class="exercise-tag">
              <i data-icon-replace="edit"></i>
              <span data-i18n="exercise.tag"></span>
            </span>
            <h3>{ex_title}</h3>
          </div>
          <p class="exercise-intro">{ex_intro}</p>
          {exercise_input}
          <div class="exercise-actions">
            <button class="btn btn-accent exercise-submit" type="button">
              <i data-icon-replace="check-circle"></i>
              <span data-i18n="exercise.verify"></span>
            </button>
            <span class="exercise-status muted"></span>
          </div>
          <div class="exercise-feedback markdown-output" hidden></div>
        </section>"""

    nav_prev = ""
    nav_next = ""
    if prev_ch:
        prev_title = prev_ch["title_it"] if lang == "it" else prev_ch["title_en"]
        ch_label = "Cap." if lang == "it" else "Ch."
        nav_prev = (
            f'<a class="nav-prev" href="{prev_ch["slug"]}.html">'
            f'<span class="nav-label"><i data-icon-replace="arrow-left"></i> <span data-i18n="chapter.nav.prev"></span></span>'
            f'<span class="nav-title">{ch_label} {prev_ch["n"]}. {prev_title}</span></a>'
        )
    else:
        nav_prev = "<span></span>"

    if next_ch:
        next_title = next_ch["title_it"] if lang == "it" else next_ch["title_en"]
        ch_label = "Cap." if lang == "it" else "Ch."
        nav_next = (
            f'<a class="nav-next" href="{next_ch["slug"]}.html">'
            f'<span class="nav-label"><span data-i18n="chapter.nav.next"></span> <i data-icon-replace="arrow-right"></i></span>'
            f'<span class="nav-title">{ch_label} {next_ch["n"]}. {next_title}</span></a>'
        )
    else:
        nav_next = "<span></span>"

    chapter_title = ch["title_it"] if lang == "it" else ch["title_en"]
    ch_label = "Cap." if lang == "it" else "Ch."
    greeting = (f"Ciao! Sto guardando con te il <b>{ch_label} {ch['n']} — {chapter_title}</b>. "
                "Chiedimi spiegazioni alternative, esempi diversi o approfondimenti.") if lang == "it" else (
        f"Hi! I'm with you on <b>{ch_label} {ch['n']} — {chapter_title}</b>. "
        "Ask me for alternative explanations, different examples or deeper dives.")

    body = f"""<div class="chapter-layout">
  <aside class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-title" data-i18n="chapter.sidebar.title"></div>
      <ol class="sidebar-list">{sidebar_items}</ol>
    </div>
  </aside>

  <article class="chapter">
    <div class="breadcrumb">
      <a href="../index.html" data-i18n="nav.home">Home</a>
      <span class="breadcrumb-sep">/</span>
      <span data-i18n="{ch['part_key']}"></span>
      <span class="breadcrumb-sep">/</span>
      <span>{ch_label} {ch['n']}</span>
    </div>
    <div class="chapter-content">
      {html_content}
    </div>
    {exercise_html}

    <nav class="chapter-nav">
      {nav_prev}
      {nav_next}
    </nav>
  </article>

  <aside class="tutor-pane">
    <div class="tutor-header">
      <i data-icon-replace="message-circle"></i>
      <span class="tutor-title" data-i18n="features.tutor.title"></span>
      <span class="muted small">{ch_label.lower()} {ch['n']}</span>
    </div>
    <div class="tutor-messages" id="tutor-messages">
      <div class="tutor-msg tutor-msg-ai">{greeting}</div>
    </div>
    <form class="tutor-form" id="tutor-form" data-chapter-slug="{ch['slug']}" data-chapter-n="{ch['n']}" data-chapter-title="{chapter_title}">
      <textarea id="tutor-input" rows="2" data-i18n-attr="placeholder:chapter.tutor.placeholder"></textarea>
      <button type="submit" class="btn btn-primary" aria-label="Send"><i data-icon-replace="send"></i></button>
    </form>
  </aside>
</div>"""

    asset_prefix = "../../" if lang == "en" else "../"
    toggle_url = f"../en/capitolo/{ch['slug']}.html" if lang == "it" else f"../../capitolo/{ch['slug']}.html"

    extra = (
        '<script src="../../assets/tutor.js"></script>\n'
        '<script src="../../assets/exercise.js"></script>\n'
        '<script src="../../assets/enhancements.js"></script>'
        if lang == "en" else
        '<script src="../assets/tutor.js"></script>\n'
        '<script src="../assets/exercise.js"></script>\n'
        '<script src="../assets/enhancements.js"></script>'
    )

    # SEO metadata per chapter
    page_title_seo = (
        f"Cap. {ch['n']}. {chapter_title} · Guida agli Agenti AI"
        if lang == "it" else
        f"Ch. {ch['n']}. {chapter_title} · Guide to AI Agents"
    )
    # Extract a short description from the chapter content (first paragraph after h1)
    desc_match = re.search(r"<p>([^<]{50,300})</p>", html_content)
    page_desc_seo = (desc_match.group(1)[:280] if desc_match else
                       f"Capitolo {ch['n']} della Guida agli Agenti AI di Gabriele Bottai.")
    url_path = (
        f"/en/capitolo/{ch['slug']}.html" if lang == "en"
        else f"/capitolo/{ch['slug']}.html"
    )

    return base_html(body, lang, title_key="site.title", extra_scripts=extra,
                     active="chapters", asset_prefix=asset_prefix,
                     lang_toggle_url=toggle_url,
                     page_title=page_title_seo, page_description=page_desc_seo,
                     url_path=url_path, og_type="article", include_jsonld=True)


def render_playground(lang: str) -> str:
    body = """<div class="page-header">
  <span class="eyebrow">
    <i data-icon-replace="flask"></i>
    <span data-i18n="page.tag"></span>
  </span>
  <h1 data-i18n="playground.title"></h1>
  <p class="lead" data-i18n="playground.lead"></p>
  <p id="pg-provider" class="provider-line"></p>
</div>

<div class="playground-layout">
  <div class="pg-config">
    <div class="card">
      <label class="field">
        <span data-i18n="form.system"></span>
        <textarea id="pg-system" rows="6" data-i18n-attr="placeholder:pg.placeholder.system"></textarea>
      </label>
      <label class="field">
        <span data-i18n="form.user"></span>
        <textarea id="pg-user" rows="8" data-i18n-attr="placeholder:pg.placeholder.user"></textarea>
      </label>
      <div class="field-row">
        <label class="field">
          <span data-i18n="form.model"></span>
          <select id="pg-model"></select>
        </label>
        <label class="field">
          <span><span data-i18n="form.temperature"></span>: <span id="pg-temp-val">0.7</span></span>
          <input id="pg-temp" type="range" min="0" max="1.5" step="0.05" value="0.7">
        </label>
        <label class="field">
          <span data-i18n="form.maxtokens"></span>
          <input id="pg-max" type="number" min="64" max="4096" step="64" value="1024">
        </label>
      </div>
      <details class="presets">
        <summary>
          <i data-icon-replace="lightbulb"></i>
          <span data-i18n="pg.presets"></span>
        </summary>
        <div class="preset-grid">
          <button type="button" class="preset" data-preset="role" data-i18n="pg.preset.role"></button>
          <button type="button" class="preset" data-preset="few-shot" data-i18n="pg.preset.fewshot"></button>
          <button type="button" class="preset" data-preset="cot" data-i18n="pg.preset.cot"></button>
          <button type="button" class="preset" data-preset="json" data-i18n="pg.preset.json"></button>
          <button type="button" class="preset" data-preset="critic" data-i18n="pg.preset.critic"></button>
        </div>
      </details>
      <div class="actions">
        <button id="pg-submit" type="button" class="btn btn-accent">
          <i data-icon-replace="play"></i>
          <span data-i18n="form.run"></span>
        </button>
        <button id="pg-cancel" type="button" class="btn btn-ghost" disabled>
          <i data-icon-replace="x"></i>
          <span data-i18n="form.cancel"></span>
        </button>
      </div>
    </div>
  </div>
  <div class="pg-output">
    <div class="card output-card">
      <div class="output-header">
        <span data-i18n="pg.output.title"></span>
        <span id="pg-stats" class="muted small"></span>
      </div>
      <div id="pg-result" class="markdown-output empty" data-i18n="pg.output.empty"></div>
    </div>
  </div>
</div>"""
    asset_prefix = "../" if lang == "en" else ""
    toggle_url = "en/playground.html" if lang == "it" else "../playground.html"
    extra = '<script src="../assets/playground.js"></script>' if lang == "en" else '<script src="assets/playground.js"></script>'
    return base_html(body, lang, title_key="playground.title", extra_scripts=extra,
                     active="playground", asset_prefix=asset_prefix, lang_toggle_url=toggle_url)


def render_agent(lang: str) -> str:
    body = """<div class="page-header">
  <span class="eyebrow">
    <i data-icon-replace="bot"></i>
    <span data-i18n="page.tag"></span>
  </span>
  <h1 data-i18n="agent.title"></h1>
  <p class="lead">
    <span data-i18n="agent.lead"></span>
    <span data-i18n="agent.tools"></span>
  </p>
  <p id="ag-provider" class="provider-line"></p>
</div>

<div class="agent-layout">
  <div class="agent-config card">
    <label class="field">
      <span data-i18n="form.goal"></span>
      <textarea id="ag-goal" rows="3" data-i18n-attr="placeholder:agent.placeholder.goal"></textarea>
    </label>
    <div class="examples">
      <span class="muted small" data-i18n="agent.examples"></span>
      <button class="chip" data-goal-key="agent.example.1.goal" data-i18n="agent.example.1"></button>
      <button class="chip" data-goal-key="agent.example.2.goal" data-i18n="agent.example.2"></button>
      <button class="chip" data-goal-key="agent.example.3.goal" data-i18n="agent.example.3"></button>
      <button class="chip" data-goal-key="agent.example.4.goal" data-i18n="agent.example.4"></button>
    </div>
    <div class="field-row" style="grid-template-columns: 2fr 1fr;">
      <label class="field">
        <span data-i18n="form.model"></span>
        <select id="ag-model"></select>
      </label>
      <label class="field">
        <span data-i18n="form.maxiter"></span>
        <input id="ag-max" type="number" min="1" max="15" value="8">
      </label>
    </div>
    <div class="actions">
      <button id="ag-submit" type="button" class="btn btn-accent">
        <i data-icon-replace="play"></i>
        <span data-i18n="form.launch"></span>
      </button>
      <button id="ag-clear" type="button" class="btn btn-ghost">
        <i data-icon-replace="trash"></i>
        <span data-i18n="form.clear"></span>
      </button>
    </div>
  </div>
  <div class="agent-trace card">
    <div class="trace-header">
      <span data-i18n="agent.trace.title"></span>
      <span id="ag-status" class="muted small"></span>
    </div>
    <div id="ag-trace" class="trace empty" data-i18n="agent.trace.empty"></div>
  </div>
</div>

<div class="callout">
  <h3>
    <i data-icon-replace="info"></i>
    <span data-i18n="agent.callout.title"></span>
  </h3>
  <ol>
    <li data-i18n="agent.callout.1"></li>
    <li data-i18n="agent.callout.2"></li>
    <li data-i18n="agent.callout.3"></li>
    <li data-i18n="agent.callout.4"></li>
  </ol>
  <p class="muted small" data-i18n="agent.callout.note"></p>
</div>"""
    asset_prefix = "../" if lang == "en" else ""
    toggle_url = "en/agente.html" if lang == "it" else "../agente.html"
    extra = '<script src="../assets/agent.js"></script>' if lang == "en" else '<script src="assets/agent.js"></script>'
    return base_html(body, lang, title_key="agent.title", extra_scripts=extra,
                     active="agent", asset_prefix=asset_prefix, lang_toggle_url=toggle_url)


def render_about(lang: str) -> str:
    if lang == "it":
        body = """<div class="page-header">
  <span class="eyebrow">
    <i data-icon-replace="info"></i>
    L'AUTORE
  </span>
  <h1>Gabriele Bottai</h1>
  <p class="lead">Sviluppatore software, autore di questa guida.</p>
</div>

<div class="about-grid">
  <article class="about-bio card">
    <h2>Chi sono</h2>
    <p>Sono <b>Gabriele Bottai</b>, sviluppatore software con interesse per gli agenti AI e la loro applicazione pratica. Ho scritto questa guida perché credo che l'AI debba essere accessibile a chi parte da zero, senza compromessi sul rigore tecnico.</p>
    <p>Mi piace lavorare su progetti dove la teoria incontra la pratica: scrivere codice che funziona, spiegare concetti complessi in modo semplice, costruire strumenti che le persone possano davvero usare.</p>
    <p>Per altri miei lavori, dai un'occhiata al mio <a href="https://gabrielebottai.netlify.app/" target="_blank" rel="noopener">portfolio</a>.</p>

    <h2>Cosa è questa guida</h2>
    <p>Una guida completa, in italiano e inglese, agli Agenti AI. <b>16 capitoli</b>, organizzati in 6 parti, che coprono dai fondamenti (cosa sono gli LLM e gli agenti) alla produzione (sicurezza, costi, valutazione). Include strumenti AI integrati per imparare facendo: tutor, playground, demo agente.</p>
    <p>Disponibile come <a href="Guida-Agenti-AI.pdf">PDF (italiano)</a>, <a href="Guide-AI-Agents-EN.pdf">PDF (English)</a>, e come sito web interattivo.</p>

    <h2>Come usare la guida</h2>
    <ul>
      <li><b>Da zero</b>: leggi i capitoli in ordine. Aspettati 8-10 ore di lettura attiva.</li>
      <li><b>Già esperto</b>: usa la <a href="#" onclick="document.getElementById('search-btn').click();return false">ricerca</a> (Cmd/Ctrl+K) per saltare ai temi che ti interessano.</li>
      <li><b>Per progetti</b>: scarica gli <a href="https://github.com/GabrieleBottai01" target="_blank" rel="noopener">esempi runnable</a> e adattali.</li>
    </ul>
  </article>

  <aside class="about-side">
    <div class="card about-contact">
      <h3>Contatti</h3>
      <ul class="contact-list">
        <li><a href="mailto:gabriele.bottai2001@gmail.com"><i data-icon-replace="send"></i> Email</a></li>
        <li><a href="https://github.com/GabrieleBottai01" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> GitHub</a></li>
        <li><a href="https://www.linkedin.com/in/gabriele-bottai-1825a9302/" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> LinkedIn</a></li>
        <li><a href="https://x.com/bottai_gabriele" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> X / Twitter</a></li>
        <li><a href="https://gabrielebottai.netlify.app/" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> Portfolio</a></li>
      </ul>
    </div>

    <div class="card about-feedback">
      <h3>Hai feedback?</h3>
      <p>Errori, suggerimenti, capitoli che non sono chiari: <a href="mailto:gabriele.bottai2001@gmail.com">scrivimi</a>. Ogni feedback è benvenuto e migliora la prossima edizione.</p>
    </div>

    <div class="card about-license">
      <h3>Licenza</h3>
      <p>© 2026 Gabriele Bottai. Tutti i diritti riservati.</p>
      <p class="muted small">La rivendita o redistribuzione non autorizzata è vietata. Per uso commerciale o didattico in azienda, <a href="mailto:gabriele.bottai2001@gmail.com">contattami</a>.</p>
    </div>
  </aside>
</div>"""
    else:
        body = """<div class="page-header">
  <span class="eyebrow">
    <i data-icon-replace="info"></i>
    THE AUTHOR
  </span>
  <h1>Gabriele Bottai</h1>
  <p class="lead">Software developer, author of this guide.</p>
</div>

<div class="about-grid">
  <article class="about-bio card">
    <h2>About me</h2>
    <p>I'm <b>Gabriele Bottai</b>, a software developer with a focus on AI agents and their practical applications. I wrote this guide because I believe AI should be accessible to beginners, without compromising on technical rigor.</p>
    <p>I enjoy projects where theory meets practice: writing code that works, explaining complex concepts simply, building tools people can actually use.</p>
    <p>For my other work, take a look at my <a href="https://gabrielebottai.netlify.app/" target="_blank" rel="noopener">portfolio</a>.</p>

    <h2>About this guide</h2>
    <p>A complete guide, in Italian and English, to AI Agents. <b>16 chapters</b>, organized in 6 parts, covering everything from fundamentals (what LLMs and agents are) to production (security, costs, evaluation). It includes integrated AI tools so you can learn by doing: tutor, playground, agent demo.</p>
    <p>Available as <a href="../Guida-Agenti-AI.pdf">PDF (Italian)</a>, <a href="../Guide-AI-Agents-EN.pdf">PDF (English)</a>, and as an interactive website.</p>

    <h2>How to use the guide</h2>
    <ul>
      <li><b>From scratch</b>: read chapters in order. Expect 8-10 hours of active reading.</li>
      <li><b>Already experienced</b>: use <a href="#" onclick="document.getElementById('search-btn').click();return false">search</a> (Cmd/Ctrl+K) to jump to topics you care about.</li>
      <li><b>For projects</b>: download the <a href="https://github.com/GabrieleBottai01" target="_blank" rel="noopener">runnable examples</a> and adapt them.</li>
    </ul>
  </article>

  <aside class="about-side">
    <div class="card about-contact">
      <h3>Contact</h3>
      <ul class="contact-list">
        <li><a href="mailto:gabriele.bottai2001@gmail.com"><i data-icon-replace="send"></i> Email</a></li>
        <li><a href="https://github.com/GabrieleBottai01" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> GitHub</a></li>
        <li><a href="https://www.linkedin.com/in/gabriele-bottai-1825a9302/" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> LinkedIn</a></li>
        <li><a href="https://x.com/bottai_gabriele" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> X / Twitter</a></li>
        <li><a href="https://gabrielebottai.netlify.app/" target="_blank" rel="noopener"><i data-icon-replace="external-link"></i> Portfolio</a></li>
      </ul>
    </div>

    <div class="card about-feedback">
      <h3>Got feedback?</h3>
      <p>Errors, suggestions, chapters that aren't clear: <a href="mailto:gabriele.bottai2001@gmail.com">drop me a line</a>. Every piece of feedback is welcome and improves the next edition.</p>
    </div>

    <div class="card about-license">
      <h3>License</h3>
      <p>© 2026 Gabriele Bottai. All rights reserved.</p>
      <p class="muted small">Unauthorized resale or redistribution is forbidden. For commercial or in-company educational use, <a href="mailto:gabriele.bottai2001@gmail.com">contact me</a>.</p>
    </div>
  </aside>
</div>"""

    asset_prefix = "../" if lang == "en" else ""
    toggle_url = "en/about.html" if lang == "it" else "../about.html"
    url_path = "/en/about.html" if lang == "en" else "/about.html"
    page_title = "Gabriele Bottai · Guida agli Agenti AI" if lang == "it" else "Gabriele Bottai · Guide to AI Agents"
    page_desc = (
        "Chi è Gabriele Bottai, autore della Guida agli Agenti AI. Bio, contatti, info sull'opera."
        if lang == "it" else
        "Who is Gabriele Bottai, author of the Guide to AI Agents. Bio, contact, info about the work."
    )
    return base_html(body, lang, title_key="about.title", active="about",
                     asset_prefix=asset_prefix, lang_toggle_url=toggle_url,
                     url_path=url_path, page_title=page_title, page_description=page_desc,
                     og_type="profile", include_jsonld=True)


def render_tutor(lang: str) -> str:
    body = """<div class="page-header">
  <span class="eyebrow">
    <i data-icon-replace="message-circle"></i>
    <span data-i18n="page.tag"></span>
  </span>
  <h1 data-i18n="tutor.title"></h1>
  <p class="lead" data-i18n="tutor.lead"></p>
</div>

<div class="tutor-page card">
  <div id="tutor-page-messages" class="tutor-messages tutor-messages-large">
    <div class="tutor-msg tutor-msg-ai">
      <span data-i18n="tutor.greet"></span>
      <ul>
        <li data-i18n="tutor.greet.1"></li>
        <li data-i18n="tutor.greet.2"></li>
        <li data-i18n="tutor.greet.3"></li>
        <li data-i18n="tutor.greet.4"></li>
      </ul>
      <span data-i18n="tutor.greet.q"></span>
    </div>
  </div>
  <form id="tutor-page-form" class="tutor-form">
    <textarea id="tutor-page-input" rows="3" data-i18n-attr="placeholder:tutor.placeholder"></textarea>
    <button type="submit" class="btn btn-primary" aria-label="Send"><i data-icon-replace="send"></i></button>
  </form>
  <div class="suggestions">
    <span class="muted small" data-i18n="tutor.sugg"></span>
    <button class="chip" data-q-key="tutor.sugg.1.q" data-i18n="tutor.sugg.1"></button>
    <button class="chip" data-q-key="tutor.sugg.2.q" data-i18n="tutor.sugg.2"></button>
    <button class="chip" data-q-key="tutor.sugg.3.q" data-i18n="tutor.sugg.3"></button>
    <button class="chip" data-q-key="tutor.sugg.4.q" data-i18n="tutor.sugg.4"></button>
  </div>
</div>"""
    asset_prefix = "../" if lang == "en" else ""
    tutor_path = "../assets/tutor.js" if lang == "en" else "assets/tutor.js"
    toggle_url = "en/tutor.html" if lang == "it" else "../tutor.html"
    extra = f"""<script src="{tutor_path}"></script>
<script>
  initTutorChat({{
    formId: 'tutor-page-form',
    inputId: 'tutor-page-input',
    messagesId: 'tutor-page-messages',
    chapterContext: null,
  }});
  document.querySelectorAll('.suggestions .chip').forEach(b => {{
    b.addEventListener('click', () => {{
      const ta = document.getElementById('tutor-page-input');
      ta.value = I18N.t(b.dataset.qKey);
      ta.focus();
    }});
  }});
</script>"""
    return base_html(body, lang, title_key="tutor.title", extra_scripts=extra,
                     active="tutor", asset_prefix=asset_prefix, lang_toggle_url=toggle_url)


# ---------------------------------------------------------------------------
# Build orchestration
# ---------------------------------------------------------------------------
def build_lang(lang: str, out_dir: Path):
    """Build a complete site for a single language under out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "capitolo").mkdir(exist_ok=True)

    # Pages
    (out_dir / "index.html").write_text(render_index(lang), encoding="utf-8")
    (out_dir / "playground.html").write_text(render_playground(lang), encoding="utf-8")
    (out_dir / "agente.html").write_text(render_agent(lang), encoding="utf-8")
    (out_dir / "tutor.html").write_text(render_tutor(lang), encoding="utf-8")
    (out_dir / "about.html").write_text(render_about(lang), encoding="utf-8")

    # Chapters + search index docs
    search_docs = []
    for i, ch in enumerate(CHAPTERS):
        md_text = get_chapter_md(ch["slug"], lang)
        if md_text is None:
            print(f"  [{lang}] WARN: missing chapter {ch['slug']}")
            continue
        html_content = md_to_html(md_text)
        prev_ch = CHAPTERS[i - 1] if i > 0 else None
        next_ch = CHAPTERS[i + 1] if i < len(CHAPTERS) - 1 else None
        page = render_chapter(ch, html_content, prev_ch, next_ch, lang)
        (out_dir / "capitolo" / f"{ch['slug']}.html").write_text(page, encoding="utf-8")
        # Add to search index
        title = ch["title_it"] if lang == "it" else ch["title_en"]
        search_docs.extend(extract_search_docs(md_text, ch["slug"], ch["n"], title, lang))

    # Search index file (consumed by search.js)
    return search_docs


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "assets").mkdir()

    # Copy CSS
    shutil.copy(SITE / "static" / "style.css", DIST / "assets" / "style.css")

    # Copy JS
    for js_file in ["app.js", "playground.js", "agent.js", "tutor.js", "exercise.js",
                    "ai-client.js", "icons.js", "i18n.js", "search.js", "enhancements.js"]:
        src = ROOT / "static-js" / js_file
        if src.exists():
            shutil.copy(src, DIST / "assets" / js_file)

    # Copy PDFs
    for pdf in ["Guida-Agenti-AI.pdf", "Guide-AI-Agents-EN.pdf"]:
        p = ROOT / pdf
        if p.exists():
            shutil.copy(p, DIST / pdf)

    # Favicon
    (DIST / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\n'
        '  <rect width="100" height="100" rx="22" fill="#d4533c"/>\n'
        '  <g fill="none" stroke="white" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">\n'
        '    <path d="M50 18 L80 35 L80 65 L50 82 L20 65 L20 35 Z"/>\n'
        '    <circle cx="50" cy="50" r="11"/>\n'
        '  </g>\n'
        '</svg>\n',
        encoding="utf-8",
    )

    # Launcher
    launcher = DIST / "Avvia-sito.command"
    launcher.write_text(
        '#!/usr/bin/env bash\n'
        'cd "$(dirname "$0")"\n\n'
        'PORT=8765\n'
        'URL="http://localhost:$PORT"\n\n'
        'echo ""\n'
        'echo "================================================================"\n'
        'echo "  Guida agli Agenti AI / Guide to AI Agents — local server"\n'
        'echo "================================================================"\n'
        'echo ""\n'
        'echo "  IT: $URL"\n'
        'echo "  EN: $URL/en/"\n'
        'echo ""\n'
        'echo "  Stop: Ctrl+C or close this window"\n'
        'echo ""\n\n'
        '( sleep 1 && open "$URL" ) &\n\n'
        'python3 -m http.server $PORT --bind 127.0.0.1\n',
        encoding="utf-8",
    )
    launcher.chmod(0o755)

    # Build IT (root) + EN (/en/)
    print("Building IT…")
    docs_it = build_lang("it", DIST)
    print(f"  {len(docs_it)} search docs")

    print("Building EN…")
    docs_en = build_lang("en", DIST / "en")
    print(f"  {len(docs_en)} search docs")

    # Search indexes (one per language)
    (DIST / "search-index-it.json").write_text(
        json.dumps(docs_it, ensure_ascii=False), encoding="utf-8"
    )
    (DIST / "search-index-en.json").write_text(
        json.dumps(docs_en, ensure_ascii=False), encoding="utf-8"
    )

    # ----- robots.txt -----
    (DIST / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE_BASE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )

    # ----- sitemap.xml -----
    sitemap_urls = []
    today = "2026-05-07"

    def add_url(path: str, lang: str, priority: float = 0.7, changefreq: str = "monthly"):
        sitemap_urls.append({
            "loc": f"{SITE_BASE_URL}{path}",
            "lastmod": today,
            "changefreq": changefreq,
            "priority": priority,
            "alternates": [],  # filled below
        })

    for lang_code, prefix in [("it", ""), ("en", "/en")]:
        add_url(f"{prefix}/", lang_code, priority=1.0, changefreq="weekly")
        add_url(f"{prefix}/about.html", lang_code, priority=0.5, changefreq="monthly")
        add_url(f"{prefix}/playground.html", lang_code, priority=0.7, changefreq="monthly")
        add_url(f"{prefix}/agente.html", lang_code, priority=0.7, changefreq="monthly")
        add_url(f"{prefix}/tutor.html", lang_code, priority=0.7, changefreq="monthly")
        for ch in CHAPTERS:
            add_url(f"{prefix}/capitolo/{ch['slug']}.html", lang_code, priority=0.8, changefreq="monthly")

    # Build sitemap XML with hreflang alternates for chapter pages and homepage
    sm_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u in sitemap_urls:
        sm_lines.append("  <url>")
        sm_lines.append(f"    <loc>{u['loc']}</loc>")
        sm_lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        sm_lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        sm_lines.append(f"    <priority>{u['priority']:.1f}</priority>")
        # Add hreflang alternates: pair root URLs with /en/ URLs
        if "/en/" in u["loc"]:
            other = u["loc"].replace("/en/", "/")
            sm_lines.append(f'    <xhtml:link rel="alternate" hreflang="it" href="{other}"/>')
            sm_lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{u["loc"]}"/>')
        else:
            other = u["loc"].replace(SITE_BASE_URL, f"{SITE_BASE_URL}/en", 1)
            # Handle root path edge case
            if u["loc"].endswith("/") and not u["loc"].endswith("//"):
                other = u["loc"].rstrip("/") + "/en/"
            sm_lines.append(f'    <xhtml:link rel="alternate" hreflang="it" href="{u["loc"]}"/>')
            sm_lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{other}"/>')
        sm_lines.append("  </url>")
    sm_lines.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm_lines), encoding="utf-8")

    total_files = sum(1 for _ in DIST.rglob("*"))
    print(f"\nOK → {DIST}")
    print(f"   {total_files} files generated")
    print(f"\n  IT: open {DIST}/index.html")
    print(f"  EN: open {DIST}/en/index.html")


if __name__ == "__main__":
    build()

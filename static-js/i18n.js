// =============================================================
// i18n — IT (default) / EN
// Use: t("nav.home") returns translated string
// Use: data-i18n="key" on HTML elements → auto-translated
// Use: data-i18n-attr="placeholder:key,title:key" for attributes
// =============================================================

const TRANSLATIONS = {
  it: {
    "site.title": "Guida agli Agenti AI",
    "site.tagline": "Una guida completa, dai fondamenti alla produzione",

    // Nav
    "nav.home": "Home",
    "nav.chapters": "Capitoli",
    "nav.playground": "Playground",
    "nav.agent": "Demo Agente",
    "nav.tutor": "Tutor AI",

    // Theme & lang
    "theme.toggle": "Cambia tema",
    "lang.toggle": "Cambia lingua",

    // API key button
    "key.unset": "Configura AI",
    "key.set": "{provider} attivo",

    // Hero
    "hero.eyebrow": "Guida completa · in italiano · 16 capitoli",
    "hero.title.before": "Impara gli",
    "hero.title.accent": "Agenti AI",
    "hero.title.after": "da zero — e provali sul posto.",
    "hero.lead": "Una guida didattica con teoria, codice runnable e <b>tre strumenti AI integrati</b>: tutor, playground prompt, demo agente con tool use.",
    "hero.cta.start": "Inizia dal Cap. 1",
    "hero.cta.playground": "Apri il Playground",
    "hero.free.title": "Provala gratis:",
    "hero.free.body": "il sito funziona con una <a href=\"https://aistudio.google.com/app/apikey\" target=\"_blank\" rel=\"noopener\">API key Gemini di Google</a> (nessuna carta richiesta, free tier 1500 req/giorno). Anche Claude di Anthropic è supportato (a pagamento).",
    "hero.meta.author": "scritta da Gabriele Bottai",
    "hero.meta.edition": "edizione 2026",
    "hero.meta.pdf": "scarica PDF",

    // Features
    "features.tutor.title": "Tutor AI",
    "features.tutor.desc": "Chatti con un tutor che conosce la guida. Spiegazioni alternative, esempi su misura, chiarimenti.",
    "features.tutor.cta": "Apri il tutor",
    "features.playground.title": "Playground prompt",
    "features.playground.desc": "System + user prompt → risposta in streaming. Vedi token, costi, latency.",
    "features.playground.cta": "Apri il playground",
    "features.agent.title": "Demo agente",
    "features.agent.desc": "Un agente con 3 tool reali. Vedi il loop ReAct dal vivo.",
    "features.agent.cta": "Apri la demo",

    // TOC
    "toc.title": "Indice della guida",
    "toc.subtitle": "Capitoli brevi, autonomi, pensati per essere letti in ordine la prima volta.",
    "toc.part.1": "Parte 1 — Fondamenti",
    "toc.part.2": "Parte 2 — Tecniche",
    "toc.part.3": "Parte 3 — Usare gli agenti",
    "toc.part.4": "Parte 4 — Costruire",
    "toc.part.5": "Parte 5 — Lavorare bene",
    "toc.part.6": "Parte 6 — Applicazioni",

    // Chapter
    "chapter.sidebar.title": "Capitoli",
    "chapter.nav.prev": "Precedente",
    "chapter.nav.next": "Successivo",
    "chapter.tutor.greet": "Ciao! Sto guardando con te il <b>Cap. {n} — {title}</b>. Chiedimi spiegazioni alternative, esempi diversi o approfondimenti.",
    "chapter.tutor.placeholder": "Fai una domanda…",
    "chapter.lang.notice": "I capitoli sono attualmente disponibili solo in italiano. L'interfaccia è multilingua.",

    // Page headers
    "page.tag": "Strumento interattivo",
    "playground.title": "Playground prompt",
    "playground.lead": "Imposta system prompt e user message, scegli temperature e modello, vedi la risposta in streaming.",
    "agent.title": "Demo agente con tool use",
    "agent.lead": "Dai un obiettivo, l'agente decide autonomamente quali tool chiamare. Vedrai ogni passo del loop ReAct.",
    "agent.tools": "Tool disponibili: <code>calculator</code>, <code>current_time</code>, <code>wikipedia_search</code>.",
    "tutor.title": "Tutor AI",
    "tutor.lead": "Un chatbot che conosce il contenuto della guida. Chiedigli spiegazioni alternative, esempi su misura, chiarimenti.",
    "tutor.greet": "Ciao! Sono il tutor AI di questa guida. Posso:",
    "tutor.greet.1": "Spiegarti un capitolo con parole/esempi diversi",
    "tutor.greet.2": "Aiutarti a fissare i concetti chiave",
    "tutor.greet.3": "Confrontare due idee correlate (es. \"ReAct vs Plan-and-Execute\")",
    "tutor.greet.4": "Suggerirti quale capitolo leggere per un certo problema",
    "tutor.greet.q": "Cosa ti incuriosisce?",
    "tutor.placeholder": "Esempio: 'Spiegami la differenza tra agente e chatbot con un esempio della vita quotidiana'",

    // Provider
    "provider.active": "Provider attivo:",
    "provider.change": "cambia",

    // Form labels
    "form.system": "System prompt",
    "form.user": "User message",
    "form.model": "Modello",
    "form.temperature": "Temperature",
    "form.maxtokens": "Max tokens",
    "form.run": "Esegui",
    "form.cancel": "Annulla",
    "form.send": "Invia",
    "form.clear": "Pulisci",
    "form.goal": "Obiettivo dell'agente",
    "form.maxiter": "Max iterazioni",
    "form.launch": "Lancia agente",

    // Playground
    "pg.placeholder.system": "Es. 'Sei un editor di una rivista scientifica…'",
    "pg.placeholder.user": "La domanda o richiesta dell'utente",
    "pg.output.empty": "La risposta apparirà qui in streaming.",
    "pg.output.title": "Risposta",
    "pg.presets": "Esempi pronti",
    "pg.preset.role": "Role priming",
    "pg.preset.fewshot": "Few-shot",
    "pg.preset.cot": "Chain-of-thought",
    "pg.preset.json": "Output JSON",
    "pg.preset.critic": "Self-critique",

    // Agent
    "agent.placeholder.goal": "Es. 'Quanti minuti sono passati dalla mezzanotte a ora (UTC)?' oppure 'Chi è il fondatore di Anthropic e quando è nata?'",
    "agent.examples": "Prova:",
    "agent.example.1": "durata mezzanotte",
    "agent.example.1.goal": "Quanti minuti sono passati dalla mezzanotte fino ad adesso (UTC)?",
    "agent.example.2": "calcolo composto",
    "agent.example.2.goal": "Calcola il 17% di 2.450 e poi convertilo in dollari (1€ = 1.08$).",
    "agent.example.3": "ricerca wikipedia",
    "agent.example.3.goal": "Chi è il fondatore di Anthropic e in che anno è nata l'azienda? Cita la fonte.",
    "agent.example.4": "analisi demografica",
    "agent.example.4.goal": "Quanto è grande in popolazione la città di Milano? Confrontala con Roma in percentuale.",
    "agent.trace.title": "Loop dell'agente",
    "agent.trace.empty": "Premi \"Lancia agente\" per vedere il loop in azione.",
    "agent.callout.title": "Cosa stai vedendo",
    "agent.callout.1": "<b>thinking</b>: l'LLM riceve lo stato e decide se chiamare un tool o rispondere.",
    "agent.callout.2": "<b>tool call</b>: il modello sceglie un tool e produce gli argomenti.",
    "agent.callout.3": "<b>tool result</b>: il browser esegue il tool e ritorna l'output.",
    "agent.callout.4": "Il ciclo continua finché il modello non produce risposta finale o si raggiunge max iterazioni.",
    "agent.callout.note": "Versione statica: i tool girano nel tuo browser, niente backend. <code>wikipedia_search</code> usa l'API pubblica di Wikipedia.",

    // Suggestions
    "tutor.sugg": "Prova:",
    "tutor.sugg.1": "agente vs chatbot",
    "tutor.sugg.1.q": "Spiegami in 3 punti perché un agente è diverso da un chatbot, con un esempio concreto.",
    "tutor.sugg.2": "prompt caching",
    "tutor.sugg.2.q": "Cosa è il prompt caching e quando devo usarlo? Fammi un esempio numerico di risparmio.",
    "tutor.sugg.3": "primo progetto",
    "tutor.sugg.3.q": "Da dove inizio a costruire il mio primo agente? Suggeriscimi un mini-progetto da 2 ore.",
    "tutor.sugg.4": "RAG vs context",
    "tutor.sugg.4.q": "Quando RAG è meglio del context lungo? E viceversa?",

    // Modal
    "modal.title": "Configura il provider AI",
    "modal.subtitle": "Scegli quale modello AI usare. <b>Le chiavi restano solo nel tuo browser</b> (localStorage) e non passano per nessun server intermedio.",
    "modal.close": "Chiudi",
    "modal.hint": "<b>Sei nuovo?</b> Inizia con <b>Gemini di Google</b> (gratis, niente carta, ti basta un account Google). Quando vuoi, puoi passare a Claude di Anthropic per modelli più capaci.",

    // Provider cards
    "pc.free": "GRATIS",
    "pc.paid": "A PAGAMENTO",
    "pc.active": "ATTIVO",
    "pc.inuse": "In uso",
    "pc.use": "Usa",
    "pc.remove": "Rimuovi key",
    "pc.input.label": "API key (deve iniziare con {prefix})",
    "pc.create": "Crea una API key gratis qui:",

    // Exercise
    "exercise.tag": "Esercizio interattivo",
    "exercise.verify": "Verifica con il tutor AI",

    // Footer
    "footer.copyright": "© 2026 Gabriele Bottai · Guida agli Agenti AI · Tutti i diritti riservati",
    "footer.about": "About",
    "about.title": "About · Guida agli Agenti AI",

    // Search
    "search.placeholder": "Cerca nei capitoli…",
    "search.hint": "Scrivi per cercare. <kbd>↑↓</kbd> per navigare, <kbd>↵</kbd> per aprire",
    "search.no_results": "Nessun risultato",
    "search.result.in": "in",

    // Errors
    "error.no_key": "Nessuna API key impostata. Apri il modal in alto a destra.",
    "error.streaming": "Errore",
  },
  en: {
    "site.title": "Guide to AI Agents",
    "site.tagline": "A complete guide, from fundamentals to production",

    "nav.home": "Home",
    "nav.chapters": "Chapters",
    "nav.playground": "Playground",
    "nav.agent": "Agent Demo",
    "nav.tutor": "AI Tutor",

    "theme.toggle": "Toggle theme",
    "lang.toggle": "Toggle language",

    "key.unset": "Configure AI",
    "key.set": "{provider} active",

    "hero.eyebrow": "Complete guide · in Italian · 16 chapters",
    "hero.title.before": "Learn",
    "hero.title.accent": "AI Agents",
    "hero.title.after": "from scratch — and try them right here.",
    "hero.lead": "An educational guide with theory, runnable code and <b>three integrated AI tools</b>: tutor, prompt playground, agent demo with tool use.",
    "hero.cta.start": "Start from Ch. 1",
    "hero.cta.playground": "Open Playground",
    "hero.free.title": "Try it free:",
    "hero.free.body": "the site works with a free <a href=\"https://aistudio.google.com/app/apikey\" target=\"_blank\" rel=\"noopener\">Google Gemini API key</a> (no card needed, free tier 1500 req/day). Anthropic Claude is also supported (paid).",
    "hero.meta.author": "by Gabriele Bottai",
    "hero.meta.edition": "2026 edition",
    "hero.meta.pdf": "download PDF",

    "features.tutor.title": "AI Tutor",
    "features.tutor.desc": "Chat with a tutor that knows the guide. Alternative explanations, custom examples, clarifications.",
    "features.tutor.cta": "Open tutor",
    "features.playground.title": "Prompt playground",
    "features.playground.desc": "System + user prompt → streaming response. See tokens, cost, latency.",
    "features.playground.cta": "Open playground",
    "features.agent.title": "Agent demo",
    "features.agent.desc": "An agent with 3 real tools. Watch the ReAct loop live.",
    "features.agent.cta": "Open demo",

    "toc.title": "Guide index",
    "toc.subtitle": "Short, self-contained chapters, designed to be read in order the first time.",
    "toc.part.1": "Part 1 — Fundamentals",
    "toc.part.2": "Part 2 — Techniques",
    "toc.part.3": "Part 3 — Using agents",
    "toc.part.4": "Part 4 — Building",
    "toc.part.5": "Part 5 — Working well",
    "toc.part.6": "Part 6 — Applications",

    "chapter.sidebar.title": "Chapters",
    "chapter.nav.prev": "Previous",
    "chapter.nav.next": "Next",
    "chapter.tutor.greet": "Hi! I'm with you on <b>Ch. {n} — {title}</b>. Ask me for alternative explanations, different examples or deeper dives.",
    "chapter.tutor.placeholder": "Ask a question…",
    "chapter.lang.notice": "Chapters are currently available in Italian only. The UI is multilingual.",

    "page.tag": "Interactive tool",
    "playground.title": "Prompt playground",
    "playground.lead": "Set the system prompt and user message, choose temperature and model, watch the response stream in.",
    "agent.title": "Agent demo with tool use",
    "agent.lead": "Give a goal, the agent decides autonomously which tools to call. You'll see every step of the ReAct loop.",
    "agent.tools": "Available tools: <code>calculator</code>, <code>current_time</code>, <code>wikipedia_search</code>.",
    "tutor.title": "AI Tutor",
    "tutor.lead": "A chatbot that knows the guide content. Ask for alternative explanations, custom examples, clarifications.",
    "tutor.greet": "Hi! I'm the AI tutor for this guide. I can:",
    "tutor.greet.1": "Explain a chapter with different words/examples",
    "tutor.greet.2": "Help you fix the key concepts",
    "tutor.greet.3": "Compare two related ideas (e.g. \"ReAct vs Plan-and-Execute\")",
    "tutor.greet.4": "Suggest which chapter to read for a specific problem",
    "tutor.greet.q": "What are you curious about?",
    "tutor.placeholder": "Example: 'Explain the difference between agent and chatbot with an everyday example'",

    "provider.active": "Active provider:",
    "provider.change": "change",

    "form.system": "System prompt",
    "form.user": "User message",
    "form.model": "Model",
    "form.temperature": "Temperature",
    "form.maxtokens": "Max tokens",
    "form.run": "Run",
    "form.cancel": "Cancel",
    "form.send": "Send",
    "form.clear": "Clear",
    "form.goal": "Agent goal",
    "form.maxiter": "Max iterations",
    "form.launch": "Launch agent",

    "pg.placeholder.system": "E.g. 'You are an editor for a science magazine…'",
    "pg.placeholder.user": "The user's question or request",
    "pg.output.empty": "The response will appear here as it streams.",
    "pg.output.title": "Response",
    "pg.presets": "Ready examples",
    "pg.preset.role": "Role priming",
    "pg.preset.fewshot": "Few-shot",
    "pg.preset.cot": "Chain-of-thought",
    "pg.preset.json": "JSON output",
    "pg.preset.critic": "Self-critique",

    "agent.placeholder.goal": "E.g. 'How many minutes have passed since midnight UTC?' or 'Who founded Anthropic and when?'",
    "agent.examples": "Try:",
    "agent.example.1": "midnight duration",
    "agent.example.1.goal": "How many minutes have passed from midnight until now (UTC)?",
    "agent.example.2": "compound calc",
    "agent.example.2.goal": "Calculate 17% of 2,450 and convert to dollars (1€ = 1.08$).",
    "agent.example.3": "wiki search",
    "agent.example.3.goal": "Who founded Anthropic and in what year was the company started? Cite the source.",
    "agent.example.4": "demographic",
    "agent.example.4.goal": "How big is Milan's population? Compare with Rome as a percentage.",
    "agent.trace.title": "Agent loop",
    "agent.trace.empty": "Press \"Launch agent\" to see the loop in action.",
    "agent.callout.title": "What you're seeing",
    "agent.callout.1": "<b>thinking</b>: the LLM receives the state and decides whether to call a tool or respond.",
    "agent.callout.2": "<b>tool call</b>: the model picks a tool and produces the arguments.",
    "agent.callout.3": "<b>tool result</b>: the browser executes the tool and returns the output.",
    "agent.callout.4": "The cycle continues until the model produces a final response or max iterations is reached.",
    "agent.callout.note": "Static version: tools run in your browser, no backend. <code>wikipedia_search</code> uses Wikipedia's public API.",

    "tutor.sugg": "Try:",
    "tutor.sugg.1": "agent vs chatbot",
    "tutor.sugg.1.q": "Explain in 3 points why an agent is different from a chatbot, with a concrete example.",
    "tutor.sugg.2": "prompt caching",
    "tutor.sugg.2.q": "What is prompt caching and when should I use it? Give me a numerical savings example.",
    "tutor.sugg.3": "first project",
    "tutor.sugg.3.q": "Where do I start to build my first agent? Suggest a 2-hour mini-project.",
    "tutor.sugg.4": "RAG vs context",
    "tutor.sugg.4.q": "When is RAG better than long context? And vice versa?",

    "modal.title": "Configure the AI provider",
    "modal.subtitle": "Choose which AI model to use. <b>Keys stay only in your browser</b> (localStorage) and don't pass through any intermediate server.",
    "modal.close": "Close",
    "modal.hint": "<b>New here?</b> Start with <b>Google Gemini</b> (free, no card, just a Google account). Later you can switch to Anthropic Claude for more capable models.",

    "pc.free": "FREE",
    "pc.paid": "PAID",
    "pc.active": "ACTIVE",
    "pc.inuse": "In use",
    "pc.use": "Use",
    "pc.remove": "Remove key",
    "pc.input.label": "API key (must start with {prefix})",
    "pc.create": "Create a free API key here:",

    "exercise.tag": "Interactive exercise",
    "exercise.verify": "Check with AI tutor",

    "footer.copyright": "© 2026 Gabriele Bottai · Guide to AI Agents · All rights reserved",
    "footer.about": "About",
    "about.title": "About · Guide to AI Agents",

    "search.placeholder": "Search in chapters…",
    "search.hint": "Type to search. <kbd>↑↓</kbd> to navigate, <kbd>↵</kbd> to open",
    "search.no_results": "No results",
    "search.result.in": "in",

    "error.no_key": "No API key set. Open the modal in the top right.",
    "error.streaming": "Error",
  },
};

const LANG_STORAGE = "site_language";

function getLang() {
  // Priority: <meta name="page-lang"> (set by build for the page's language) > localStorage > browser
  const pageLang = document.querySelector('meta[name="page-lang"]')?.content;
  if (pageLang && (pageLang === "it" || pageLang === "en")) return pageLang;
  const stored = localStorage.getItem(LANG_STORAGE);
  if (stored === "it" || stored === "en") return stored;
  return (navigator.language || "it").startsWith("en") ? "en" : "it";
}

function setLang(lang) {
  if (!TRANSLATIONS[lang]) return;
  localStorage.setItem(LANG_STORAGE, lang);
  document.documentElement.lang = lang;
  applyTranslations();
  window.dispatchEvent(new CustomEvent("lang-changed", { detail: { lang } }));
}

function t(key, vars) {
  const lang = localStorage.getItem(LANG_STORAGE) || "it";
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.it;
  let s = dict[key] || TRANSLATIONS.it[key] || key;
  if (vars) {
    Object.keys(vars).forEach(k => {
      s = s.replace(new RegExp(`\\{${k}\\}`, "g"), vars[k]);
    });
  }
  return s;
}

function applyTranslations(root = document) {
  // text content
  root.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    el.innerHTML = t(key);
  });
  // attributes — format: "attr1:key1,attr2:key2"
  root.querySelectorAll("[data-i18n-attr]").forEach(el => {
    const map = el.dataset.i18nAttr.split(",");
    map.forEach(pair => {
      const [attr, key] = pair.split(":").map(s => s.trim());
      if (attr && key) el.setAttribute(attr, t(key));
    });
  });
  // <title>
  const titleKey = document.querySelector("meta[name='i18n-title']")?.content;
  if (titleKey) document.title = t(titleKey);
}

document.addEventListener("DOMContentLoaded", () => {
  const lang = localStorage.getItem(LANG_STORAGE) || "it";
  document.documentElement.lang = lang;
  applyTranslations();
});

window.I18N = { t, getLang, setLang, applyTranslations, TRANSLATIONS };

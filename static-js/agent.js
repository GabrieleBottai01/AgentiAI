// Agent demo — usa AI.streamAI con tool use

const AGENT_TOOLS = [
  {
    name: "calculator",
    description: "Esegue espressioni aritmetiche (es. '2+2', '15*23/4', 'Math.sqrt(144)'). Usa SOLO per calcoli numerici.",
    input_schema: {
      type: "object",
      properties: { expression: { type: "string", description: "Espressione JavaScript matematica valida" } },
      required: ["expression"],
    },
  },
  {
    name: "current_time",
    description: "Restituisce data e ora correnti (UTC, formato ISO-8601). Usa per timestamp o per calcolare durate.",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "wikipedia_search",
    description: "Cerca su Wikipedia (italiano). Restituisce titoli e descrizioni dei risultati più rilevanti. Usa per fatti, persone, eventi storici, definizioni. Non per notizie recenti.",
    input_schema: {
      type: "object",
      properties: { query: { type: "string", description: "Termine di ricerca (es. 'Anthropic', 'Roma')" } },
      required: ["query"],
    },
  },
];

function execCalculator(expression) {
  try {
    const fn = new Function("Math", `"use strict"; return (${expression});`);
    return String(fn(Math));
  } catch (e) { return `errore: ${e.message}`; }
}

function execCurrentTime() { return new Date().toISOString(); }

async function execWikipediaSearch(query) {
  try {
    const url = `https://it.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(query)}&limit=5&namespace=0&format=json&origin=*`;
    const resp = await fetch(url);
    if (!resp.ok) return `errore HTTP ${resp.status}`;
    const data = await resp.json();
    const [, titles, descriptions, urls] = data;
    if (!titles || titles.length === 0) return `Nessun risultato Wikipedia per "${query}".`;
    return titles.map((t, i) => `- ${t}: ${descriptions[i] || "(no description)"} [${urls[i] || ""}]`).join("\n");
  } catch (e) { return `errore: ${e.message}`; }
}

const TOOL_FNS = {
  calculator: ({ expression }) => execCalculator(expression || ""),
  current_time: () => execCurrentTime(),
  wikipedia_search: ({ query }) => execWikipediaSearch(query || ""),
};

const AGENT_SYSTEM = `Sei un agente di ricerca e assistenza. Hai 3 tool:
- calculator: per qualsiasi calcolo numerico.
- current_time: per data/ora correnti (UTC).
- wikipedia_search: per cercare su Wikipedia in italiano.

Procedura: capisci l'obiettivo, usa i tool quando servono, sintetizza una risposta finale concisa (3-6 frasi) citando le fonti se hai cercato sull'enciclopedia.
Se dopo qualche tentativo non hai abbastanza info, dillo invece di inventare. Massimo 8 iterazioni.`;

document.addEventListener("DOMContentLoaded", () => {
  const goalEl = document.getElementById("ag-goal");
  const modelEl = document.getElementById("ag-model");
  const maxEl = document.getElementById("ag-max");
  const submitBtn = document.getElementById("ag-submit");
  const clearBtn = document.getElementById("ag-clear");
  const trace = document.getElementById("ag-trace");
  const status = document.getElementById("ag-status");
  const providerLabel = document.getElementById("ag-provider");

  function refreshUI() {
    appHelpers.populateModelSelect(modelEl);
    appHelpers.refreshProviderLine("ag-provider");
  }
  refreshUI();
  window.addEventListener("ai-provider-changed", refreshUI);
  window.addEventListener("lang-changed", refreshUI);

  document.querySelectorAll(".examples .chip").forEach(b => {
    b.addEventListener("click", () => {
      // Prefer i18n key; fallback to legacy data-goal
      const goalText = b.dataset.goalKey ? I18N.t(b.dataset.goalKey) : b.dataset.goal;
      goalEl.value = goalText;
      goalEl.focus();
    });
  });

  function clearTrace() {
    trace.classList.add("empty");
    trace.innerHTML = 'Premi "Lancia agente" per vedere il loop in azione.';
    status.textContent = "";
  }

  function addStep(type, label, content) {
    if (trace.classList.contains("empty")) {
      trace.classList.remove("empty");
      trace.innerHTML = "";
    }
    const div = document.createElement("div");
    div.className = `trace-step ${type}`;
    div.innerHTML = `<div class="step-label">${label}</div>${content}`;
    trace.appendChild(div);
    trace.scrollTop = trace.scrollHeight;
    return div;
  }

  function escHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  clearBtn.addEventListener("click", clearTrace);

  submitBtn.addEventListener("click", async () => {
    const goal = goalEl.value.trim();
    if (!goal) { alert("Scrivi un obiettivo per l'agente"); return; }
    if (!appHelpers.ensureApiKey()) return;

    clearTrace();
    trace.classList.remove("empty");
    trace.innerHTML = "";
    submitBtn.disabled = true;
    status.textContent = "agente in esecuzione…";

    const messages = [{ role: "user", content: goal }];
    const maxIters = parseInt(maxEl.value, 10);
    // Mantieni una mappa id→name per fornire il name quando convertiamo tool_result a Gemini
    const toolNameById = {};

    try {
      for (let step = 1; step <= maxIters; step++) {
        addStep("thinking", `Iterazione ${step} — Thinking`, "<div>Il modello sta valutando il prossimo passo…</div>");

        const stream = AI.streamAI({
          model: modelEl.value,
          max_tokens: 2048,
          system: AGENT_SYSTEM,
          tools: AGENT_TOOLS,
          messages,
        });

        let assistantContent = null;
        let stopReason = null;
        let textBuffer = "";
        const toolCalls = [];

        for await (const ev of stream) {
          if (ev.type === "text_delta") {
            textBuffer += ev.text;
          } else if (ev.type === "tool_use") {
            toolCalls.push(ev);
            toolNameById[ev.id] = ev.name;
          } else if (ev.type === "stop") {
            stopReason = ev.stop_reason;
            assistantContent = ev.content;
          } else if (ev.type === "error") {
            addStep("error", "Errore", `<div>${escHtml(ev.message)}</div>`);
            status.textContent = "errore";
            submitBtn.disabled = false;
            return;
          }
        }

        if (textBuffer.trim()) {
          addStep("text", "Testo intermedio del modello",
                  `<div>${appHelpers.renderMarkdown(textBuffer)}</div>`);
        }

        messages.push({ role: "assistant", content: assistantContent || [] });

        if (stopReason !== "tool_use") {
          addStep("done", "Fine", `<div>Stop reason: <code>${stopReason}</code></div>`);
          status.textContent = "completato";
          submitBtn.disabled = false;
          return;
        }

        // Esegui i tool
        const toolResults = [];
        for (const tc of toolCalls) {
          addStep("tool-call", `Tool call → ${tc.name}`,
                  `<pre>${escHtml(JSON.stringify(tc.input, null, 2))}</pre>`);

          const fn = TOOL_FNS[tc.name];
          let result;
          if (!fn) result = `errore: tool sconosciuto '${tc.name}'`;
          else {
            try { result = await fn(tc.input || {}); }
            catch (e) { result = `errore: ${e.message}`; }
          }

          addStep("tool-result", `Tool result ← ${tc.name}`,
                  `<pre>${escHtml(String(result).slice(0, 1500))}</pre>`);

          toolResults.push({
            type: "tool_result",
            tool_use_id: tc.id,
            _toolName: tc.name,  // hint per l'adapter Gemini
            content: String(result).slice(0, 5000),
          });
        }

        messages.push({ role: "user", content: toolResults });
      }

      addStep("done", "Fine", `<div>Stop reason: <code>max_iterations</code></div>`);
      status.textContent = "max iterazioni raggiunto";
    } catch (e) {
      addStep("error", "Errore", `<div>${escHtml(e.message)}</div>`);
      status.textContent = "errore";
    } finally {
      submitBtn.disabled = false;
    }
  });
});

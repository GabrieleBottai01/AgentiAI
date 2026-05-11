// Agent demo — visualizza il loop ReAct con tool use

document.addEventListener("DOMContentLoaded", () => {
  const goalEl = document.getElementById("ag-goal");
  const modelEl = document.getElementById("ag-model");
  const maxEl = document.getElementById("ag-max");
  const submitBtn = document.getElementById("ag-submit");
  const clearBtn = document.getElementById("ag-clear");
  const trace = document.getElementById("ag-trace");
  const status = document.getElementById("ag-status");

  // chip examples
  document.querySelectorAll(".examples .chip").forEach(b => {
    b.addEventListener("click", () => {
      goalEl.value = b.dataset.goal;
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

    await appHelpers.streamPost(
      "/api/agent",
      {
        goal,
        model: modelEl.value,
        max_iterations: parseInt(maxEl.value, 10),
      },
      (ev) => {
        if (ev.type === "thinking") {
          addStep("thinking", `Iterazione ${ev.step} — Thinking`,
                  '<div>Il modello sta valutando il prossimo passo…</div>');
        } else if (ev.type === "text") {
          addStep("text", "Testo intermedio del modello",
                  `<div>${appHelpers.renderMarkdown(ev.content)}</div>`);
        } else if (ev.type === "tool_call") {
          const args = JSON.stringify(ev.input, null, 2);
          addStep("tool-call", `Tool call → ${ev.name}`,
                  `<pre>${escHtml(args)}</pre>`);
        } else if (ev.type === "tool_result") {
          addStep("tool-result", `Tool result ← ${ev.name}`,
                  `<pre>${escHtml(ev.result)}</pre>`);
        } else if (ev.type === "done") {
          addStep("done", "Fine", `<div>Stop reason: <code>${ev.stop_reason}</code></div>`);
          status.textContent = "completato";
        } else if (ev.type === "error") {
          addStep("error", "Errore", `<div>${escHtml(ev.message)}</div>`);
          status.textContent = "errore";
        }
      },
      () => {
        submitBtn.disabled = false;
      },
      (err) => {
        addStep("error", "Errore di rete", `<div>${escHtml(err)}</div>`);
        status.textContent = "errore";
        submitBtn.disabled = false;
      }
    );
  });
});

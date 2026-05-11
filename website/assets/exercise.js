// Exercise widget — usa AI.streamAI

const EXERCISE_PROMPTS = {
  "ex-cap1": (answers) => `Sei il tutor della guida. Valuta le risposte dello studente all'esercizio sul Capitolo 1 (agente vs chatbot vs automazione).

Le 3 descrizioni e la risposta corretta:
1. Bug-fix autonomo con esplorazione e PR → AGENTE (loop, decisione, tool)
2. Traduzione automatica messaggi → AUTOMAZIONE (singolo passo, no loop)
3. Q&A su cucina → CHATBOT (no tool, no loop)

Risposte dello studente (JSON):
${JSON.stringify(answers, null, 2)}

Per ogni risposta:
- Indica se è giusta o sbagliata.
- Spiega in 1-2 frasi PERCHÉ, citando i criteri "loop" / "decisione autonoma" / "tool".
Conclusione finale: punteggio X/3 e un consiglio.`,

  "ex-cap5": (answers) => `Sei un esperto di prompt engineering. Lo studente ha riscritto il prompt "Riassumi il testo che ti mando." in qualcosa di più strutturato. Valuta secondo i criteri del Capitolo 5: ruolo, obiettivo, contesto, vincoli, formato dell'output, esempi.

Prompt dello studente:
"""
${answers.prompt}
"""

Restituisci:
1. Cosa funziona (2-3 punti specifici).
2. Cosa manca o si potrebbe migliorare (con esempi concreti).
3. Voto da 1 a 10 con giustificazione in una frase.
4. Una versione migliorata di esempio (massimo 8 righe).`,

  "ex-cap6": (answers) => `Sei un esperto di tool design per agenti AI. Lo studente ha progettato la definizione di un tool per cercare voli. Valuta secondo i criteri del Capitolo 6.

Tool dello studente:
"""
${answers.tool_def}
"""

Restituisci:
1. Validità sintattica (è JSON valido? lo schema è corretto?).
2. Qualità della description: il modello capirebbe quando usarlo? Cita criteri specifici.
3. Qualità dei parametri: tipi, descrizioni, required, enum dove utili.
4. Voto 1-10 con motivazione.
5. Una versione rivista di esempio (formattata, max 25 righe).`,
};

document.addEventListener("DOMContentLoaded", () => {
  const ex = document.querySelector(".exercise");
  if (!ex) return;

  const id = ex.dataset.exerciseId;
  const type = ex.dataset.exerciseType;
  const submitBtn = ex.querySelector(".exercise-submit");
  const statusEl = ex.querySelector(".exercise-status");
  const feedbackEl = ex.querySelector(".exercise-feedback");

  submitBtn.addEventListener("click", async () => {
    if (!appHelpers.ensureApiKey()) return;

    let answers = {};
    if (type === "classify") {
      ex.querySelectorAll(".exercise-items > li").forEach((li, idx) => {
        const checked = li.querySelector('input[type="radio"]:checked');
        answers[`item-${idx}`] = checked ? checked.value : null;
      });
      const allAnswered = Object.values(answers).every(v => v !== null);
      if (!allAnswered) {
        statusEl.textContent = "Rispondi a tutte le domande prima di verificare.";
        statusEl.style.color = "#c62828";
        return;
      }
    } else if (type === "improve_prompt") {
      const text = ex.querySelector(".exercise-input").value.trim();
      if (!text) { statusEl.textContent = "Scrivi il prompt prima di valutare."; return; }
      answers = { prompt: text };
    } else if (type === "design_tool") {
      const text = ex.querySelector(".exercise-input").value.trim();
      if (!text) { statusEl.textContent = "Scrivi la definizione del tool."; return; }
      answers = { tool_def: text };
    }

    const promptBuilder = EXERCISE_PROMPTS[id];
    if (!promptBuilder) { statusEl.textContent = "Esercizio non riconosciuto."; return; }
    const prompt = promptBuilder(answers);

    statusEl.textContent = "il tutor sta valutando…";
    statusEl.style.color = "";
    submitBtn.disabled = true;
    feedbackEl.hidden = false;
    feedbackEl.innerHTML = '<span class="streaming"></span>';
    let acc = "";

    try {
      const stream = AI.streamAI({
        max_tokens: 2048,
        system: "Sei un tutor preciso, costruttivo, in italiano. Usa formattazione markdown leggera.",
        messages: [{ role: "user", content: prompt }],
      });
      for await (const ev of stream) {
        if (ev.type === "text_delta") {
          acc += ev.text;
          feedbackEl.innerHTML = appHelpers.renderMarkdown(acc) + '<span class="streaming"></span>';
        } else if (ev.type === "error") {
          feedbackEl.innerHTML = `<span style="color:#c62828">${ev.message}</span>`;
          submitBtn.disabled = false;
          return;
        }
      }
      feedbackEl.innerHTML = appHelpers.renderMarkdown(acc);
      statusEl.textContent = "valutazione completata";
    } catch (e) {
      feedbackEl.innerHTML = `<span style="color:#c62828">Errore: ${e.message}</span>`;
      statusEl.textContent = "errore";
    } finally {
      submitBtn.disabled = false;
    }
  });
});

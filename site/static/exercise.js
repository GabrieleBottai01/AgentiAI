// Exercise widget — submits to /api/exercise and streams the AI feedback

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
      // verify all answered
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

    statusEl.textContent = "il tutor sta valutando…";
    statusEl.style.color = "";
    submitBtn.disabled = true;
    feedbackEl.hidden = false;
    feedbackEl.innerHTML = '<span class="streaming"></span>';
    let acc = "";

    await appHelpers.streamPost(
      "/api/exercise",
      { exercise_id: id, answers },
      (ev) => {
        if (ev.delta) {
          acc += ev.delta;
          feedbackEl.innerHTML = appHelpers.renderMarkdown(acc) + '<span class="streaming"></span>';
        } else if (ev.error) {
          feedbackEl.innerHTML = `<span style="color:#c62828">Errore: ${ev.error}</span>`;
        }
      },
      () => {
        feedbackEl.innerHTML = appHelpers.renderMarkdown(acc);
        statusEl.textContent = "valutazione completata";
        submitBtn.disabled = false;
      },
      (err) => {
        feedbackEl.innerHTML = `<span style="color:#c62828">Errore: ${err}</span>`;
        statusEl.textContent = "errore";
        submitBtn.disabled = false;
      }
    );
  });
});

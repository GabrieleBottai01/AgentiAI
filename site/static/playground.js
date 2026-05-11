// Playground prompt — system + user → streaming response

const PRESETS = {
  role: {
    system: "Sei un Senior Software Engineer con 15 anni di esperienza in sistemi distribuiti. Fai code review di un junior. Stile diretto ma costruttivo, citi best practice. Rispondi in italiano.",
    user: "Ho scritto questa funzione Python per validare email:\n\ndef valid_email(s):\n    return '@' in s and '.' in s\n\nVa bene?",
    temp: 0.4,
  },
  "few-shot": {
    system: "Classifica il sentiment di un tweet in 'positivo', 'negativo' o 'neutro'.",
    user: "Ecco alcuni esempi:\n\nTweet: \"Adoro questo nuovo telefono!\"\nSentiment: positivo\n\nTweet: \"Spedizione lentissima, mai più.\"\nSentiment: negativo\n\nTweet: \"Arrivato come da descrizione.\"\nSentiment: neutro\n\nTweet: \"Il design è ok ma la batteria dura niente.\"\nSentiment:",
    temp: 0.0,
  },
  cot: {
    system: "Sei un solver di problemi matematici. Ragiona passo passo prima di rispondere. Rispondi in italiano.",
    user: "Marco ha 12 mele. Ne dà 3 a sua sorella, ne mangia 2, poi compra il doppio di quelle che gli sono rimaste. Quante mele ha alla fine? Pensa passo passo prima di rispondere.",
    temp: 0.0,
  },
  json: {
    system: "Estrai informazioni strutturate dal CV in input. Restituisci SOLO JSON valido, niente testo extra.\n\nSchema:\n{\n  \"nome\": \"string\",\n  \"anni_esperienza\": \"number\",\n  \"skill\": [\"string\"],\n  \"ultimo_ruolo\": {\n    \"azienda\": \"string\",\n    \"titolo\": \"string\"\n  }\n}",
    user: "Mario Rossi, ingegnere software con 8 anni di esperienza. Esperto di Python, React, AWS. Attualmente Senior Backend Developer presso Acme Inc. Laurea in Informatica al Politecnico di Milano (2017).",
    temp: 0.0,
  },
  critic: {
    system: "Sei un critico letterario rigoroso. Per ogni testo che ricevi:\n1. Identifica 2 punti di forza con esempi specifici.\n2. Identifica 2 debolezze con suggerimenti concreti.\n3. Concludi con voto da 1 a 10.\n\nUsa formattazione markdown.",
    user: "Critica questo paragrafo:\n\n\"Era una mattina come tante. Il sole splendeva, gli uccelli cinguettavano. Mario si svegliò di buon umore e decise che oggi sarebbe stata una bella giornata. Si vestì velocemente e uscì di casa. La strada era affollata di persone che andavano al lavoro.\"",
    temp: 0.7,
  },
};

document.addEventListener("DOMContentLoaded", () => {
  const sysEl = document.getElementById("pg-system");
  const userEl = document.getElementById("pg-user");
  const modelEl = document.getElementById("pg-model");
  const tempEl = document.getElementById("pg-temp");
  const tempVal = document.getElementById("pg-temp-val");
  const maxEl = document.getElementById("pg-max");
  const submitBtn = document.getElementById("pg-submit");
  const cancelBtn = document.getElementById("pg-cancel");
  const result = document.getElementById("pg-result");
  const stats = document.getElementById("pg-stats");

  let currentCancel = null;

  // temperature display
  tempEl.addEventListener("input", () => { tempVal.textContent = tempEl.value; });

  // presets
  document.querySelectorAll(".preset").forEach(btn => {
    btn.addEventListener("click", () => {
      const p = PRESETS[btn.dataset.preset];
      if (!p) return;
      sysEl.value = p.system;
      userEl.value = p.user;
      if (typeof p.temp === "number") {
        tempEl.value = p.temp;
        tempVal.textContent = p.temp;
      }
    });
  });

  submitBtn.addEventListener("click", async () => {
    const user = userEl.value.trim();
    if (!user) { alert("Scrivi un user message"); return; }
    if (!appHelpers.ensureApiKey()) return;

    submitBtn.disabled = true;
    cancelBtn.disabled = false;
    result.classList.remove("empty");
    result.innerHTML = '<span class="streaming"></span>';
    stats.textContent = "in attesa…";

    const t0 = performance.now();
    let acc = "";

    currentCancel = await appHelpers.streamPost(
      "/api/playground",
      {
        system: sysEl.value,
        user,
        model: modelEl.value,
        temperature: parseFloat(tempEl.value),
        max_tokens: parseInt(maxEl.value, 10),
      },
      (ev) => {
        if (ev.delta) {
          acc += ev.delta;
          result.innerHTML = appHelpers.renderMarkdown(acc) + '<span class="streaming"></span>';
        } else if (ev.error) {
          result.innerHTML = `<span style="color:#c62828">Errore: ${ev.error}</span>`;
        } else if (ev.done) {
          const ms = Math.round(performance.now() - t0);
          const inT = ev.input_tokens ?? "?";
          const outT = ev.output_tokens ?? "?";
          stats.textContent = `${ms} ms · in: ${inT} tok · out: ${outT} tok`;
        }
      },
      () => {
        result.innerHTML = appHelpers.renderMarkdown(acc);
        submitBtn.disabled = false;
        cancelBtn.disabled = true;
      },
      (err) => {
        result.innerHTML = `<span style="color:#c62828">Errore: ${err}</span>`;
        submitBtn.disabled = false;
        cancelBtn.disabled = true;
      }
    );
  });

  cancelBtn.addEventListener("click", () => {
    if (currentCancel) currentCancel();
    submitBtn.disabled = false;
    cancelBtn.disabled = true;
  });
});

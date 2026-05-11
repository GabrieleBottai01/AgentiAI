// Tutor chat — usa AI.streamAI (provider attivo: Anthropic o Gemini)

function tutorBaseSystemPrompt() {
  const lang = (I18N && I18N.getLang) ? I18N.getLang() : "it";
  const langDirective = lang === "en"
    ? "- English, direct and friendly tone."
    : "- Italiano, tono diretto e amichevole.";

  return `You are the AI tutor for the "Guida agli Agenti AI" (Guide to AI Agents) by Gabriele Bottai.

Your job: help users understand the guide's content with clear explanations, concrete examples, simple analogies, building on what the guide already says.

Style:
${langDirective}
- Concise responses (4-8 sentences typical). Longer only when needed.
- Practical examples before abstract terms.
- When citing a chapter, use the format "(see Ch. N)" / "(vedi Cap. N)" with the section number when relevant (e.g. "see Ch. 7.5").
- If the question is ambiguous, ask ONE clarifying question first.

CRITICAL RULES:
- The user is reading a specific guide. Below you have the most relevant excerpts retrieved from that guide. Base your answer primarily on these excerpts.
- If the excerpts don't contain the answer, say so explicitly and offer the best general explanation you can — but be transparent about not citing the guide.
- Never invent chapter contents. If you don't see info in the excerpts, you don't know what the guide says about it.`;
}

function formatRetrievedChunks(chunks, lang) {
  if (!chunks || chunks.length === 0) return "";
  const header = lang === "en"
    ? "\n\n=== RELEVANT EXCERPTS FROM THE GUIDE ===\n(Use these as primary source for your answer. Cite them as 'Ch. N' / 'Ch. N.X'.)\n"
    : "\n\n=== ESTRATTI RILEVANTI DALLA GUIDA ===\n(Usa questi come fonte primaria. Citali come 'Cap. N' / 'Cap. N.X'.)\n";
  const body = chunks.map((c, i) => {
    const ref = c.section
      ? `[Cap. ${c.n} — ${c.chapter_title} | ${c.section}]`
      : `[Cap. ${c.n} — ${c.chapter_title}]`;
    return `\n${ref}\n${c.text}`;
  }).join("\n");
  return header + body + "\n=== END EXCERPTS ===\n";
}

function initTutorChat({ formId, inputId, messagesId, chapterContext }) {
  const form = document.getElementById(formId);
  const input = document.getElementById(inputId);
  const messages = document.getElementById(messagesId);
  if (!form) return;

  const history = [];

  function appendMessage(role, html) {
    const div = document.createElement("div");
    div.className = `tutor-msg tutor-msg-${role === "user" ? "user" : "ai"}`;
    div.innerHTML = html;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    if (!appHelpers.ensureApiKey()) return;

    history.push({ role: "user", content: text });
    appendMessage("user", text.replace(/\n/g, "<br>"));
    input.value = "";

    const aiBubble = appendMessage("ai", '<span class="streaming"></span>');
    let acc = "";

    // RAG: retrieve relevant chunks from the guide for this question
    let chunks = [];
    let queryForRetrieval = text;
    // If we're on a chapter page, bias retrieval toward that chapter's content too
    if (chapterContext) {
      queryForRetrieval = `${chapterContext.title} ${text}`;
    }
    if (window.SearchAPI && window.SearchAPI.retrieveChunks) {
      try {
        chunks = await window.SearchAPI.retrieveChunks(queryForRetrieval, 4);
      } catch (e) {
        console.warn("RAG retrieval failed, falling back to no-context:", e);
      }
    }

    const lang = (I18N && I18N.getLang) ? I18N.getLang() : "it";
    let system = tutorBaseSystemPrompt();
    system += formatRetrievedChunks(chunks, lang);
    if (chapterContext) {
      const note = lang === "en"
        ? `\n\nThe user is currently reading Chapter ${chapterContext.n}: ${chapterContext.title}. Prefer that chapter's content when relevant.`
        : `\n\nL'utente sta leggendo il Capitolo ${chapterContext.n}: ${chapterContext.title}. Privilegia quel capitolo quando rilevante.`;
      system += note;
    }

    try {
      const stream = AI.streamAI({
        max_tokens: 2048,
        system,
        messages: history,
      });
      for await (const ev of stream) {
        if (ev.type === "text_delta") {
          acc += ev.text;
          aiBubble.innerHTML = appHelpers.renderMarkdown(acc) + '<span class="streaming"></span>';
          messages.scrollTop = messages.scrollHeight;
        } else if (ev.type === "error") {
          aiBubble.innerHTML = `<span style="color:#c62828">${ev.message}</span>`;
          return;
        }
      }
      aiBubble.innerHTML = appHelpers.renderMarkdown(acc);
      history.push({ role: "assistant", content: acc });
    } catch (e) {
      aiBubble.innerHTML = `<span style="color:#c62828">Errore: ${e.message}</span>`;
    }
  }

  form.addEventListener("submit", (e) => { e.preventDefault(); send(); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); send(); }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const sidebarForm = document.getElementById("tutor-form");
  if (sidebarForm) {
    const ctx = sidebarForm.dataset.chapterN ? {
      n: sidebarForm.dataset.chapterN,
      title: sidebarForm.dataset.chapterTitle,
    } : null;
    initTutorChat({
      formId: "tutor-form",
      inputId: "tutor-input",
      messagesId: "tutor-messages",
      chapterContext: ctx,
    });
  }
});

window.initTutorChat = initTutorChat;

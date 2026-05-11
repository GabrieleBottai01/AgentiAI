// Tutor chat (sidebar in chapter pages, full panel in /tutor)

function initTutorChat({ formId, inputId, messagesId, chapterSlug }) {
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

    await appHelpers.streamPost(
      "/api/tutor",
      { messages: history, chapter_slug: chapterSlug || null },
      (ev) => {
        if (ev.delta) {
          acc += ev.delta;
          aiBubble.innerHTML = appHelpers.renderMarkdown(acc) + '<span class="streaming"></span>';
          messages.scrollTop = messages.scrollHeight;
        } else if (ev.error) {
          aiBubble.innerHTML = `<span style="color:#c62828">Errore: ${ev.error}</span>`;
        }
      },
      () => {
        aiBubble.innerHTML = appHelpers.renderMarkdown(acc);
        history.push({ role: "assistant", content: acc });
      },
      (err) => {
        aiBubble.innerHTML = `<span style="color:#c62828">Errore: ${err}</span>`;
      }
    );
  }

  form.addEventListener("submit", (e) => { e.preventDefault(); send(); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); send(); }
  });
}

// Auto-init for chapter sidebar tutor (form#tutor-form)
document.addEventListener("DOMContentLoaded", () => {
  const sidebarForm = document.getElementById("tutor-form");
  if (sidebarForm) {
    initTutorChat({
      formId: "tutor-form",
      inputId: "tutor-input",
      messagesId: "tutor-messages",
      chapterSlug: sidebarForm.dataset.chapterSlug,
    });
  }
});

window.initTutorChat = initTutorChat;

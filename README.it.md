# Guida agli Agenti AI

> 🇬🇧 **English speaker?** Read the [English README](README.md) — the whole guide is available in English too.

Una guida completa, in italiano, pensata per chi parte da zero e vuole capire **cosa sono gli agenti AI, come funzionano e come usarli** — sia come utente, sia come sviluppatore.

## 🌐 Leggila online

| | |
|---|---|
| **Sito (italiano)** | **https://myfirstaiagent.netlify.app/** |
| **Website (English)** | https://myfirstaiagent.netlify.app/en/ |
| **PDF italiano** | [`Guida-Agenti-AI.pdf`](Guida-Agenti-AI.pdf) |
| **PDF English** | [`Guide-AI-Agents-EN.pdf`](Guide-AI-Agents-EN.pdf) |

Il sito ha ricerca full-text (`Cmd/Ctrl + K`), un tutor legato al capitolo che stai leggendo e un playground interattivo.

---

## A chi è rivolta

A te, se almeno una di queste frasi ti suona familiare:

- "Sento parlare di agenti AI ovunque ma non ho capito cosa li distingue da ChatGPT."
- "Voglio iniziare a usare l'AI per lavorare meglio, ma non so da dove partire."
- "So programmare ma non ho mai costruito un agente. Da dove comincio?"
- "Ho provato un chatbot e mi ha deluso. Si può fare di meglio?"

Non serve nessuna conoscenza pregressa di machine learning. Serve curiosità e voglia di provare.

## Come è organizzata

La guida è divisa in **capitoli brevi**, ognuno in un file `.md` separato. Puoi leggerli in ordine (consigliato la prima volta) oppure saltare a quello che ti serve.

Ogni capitolo è strutturato così:
1. **Concetto** — la teoria, spiegata semplice.
2. **Pratica** — esempi concreti, codice o screenshot di workflow.
3. **Da ricordare** — i 3-5 punti chiave.
4. **Errori tipici** — le trappole in cui cascano quasi tutti.

## Indice

### Parte 1 — Fondamenti (capire)
1. [Cosa sono gli Agenti AI](01-cosa-sono-gli-agenti-ai.md)
2. [Come funzionano gli LLM (il motore)](02-come-funzionano-gli-llm.md)
3. [Anatomia di un agente](03-anatomia-di-un-agente.md)
4. [Tipi di agenti e architetture](04-tipi-di-agenti-e-architetture.md)

### Parte 2 — Tecniche essenziali (saper parlare con loro)
5. [Prompt engineering: l'arte di chiedere](05-prompt-engineering.md)
6. [Tool use e function calling](06-tool-use-e-function-calling.md)
7. [Memoria, contesto e RAG](07-memoria-contesto-e-rag.md)

### Parte 3 — Usare gli agenti (pratica quotidiana)
8. [Usare i chatbot AI: ChatGPT, Claude.ai, Gemini](08-usare-i-chatbot-ai.md)
9. [Claude Code: agente da terminale per sviluppatori](09-claude-code-per-sviluppatori.md)

### Parte 4 — Costruire agenti (mani in pasta)
10. [Costruire agenti custom con API e SDK](10-costruire-agenti-con-api-sdk.md)
11. [Framework: LangChain, AutoGen, CrewAI](11-framework-langchain-autogen-crewai.md)

### Parte 5 — Lavorare bene (qualità e responsabilità)
12. [Best practice di sviluppo con agenti](12-best-practice-sviluppo-con-agenti.md)
13. [Sicurezza, costi, limiti](13-sicurezza-costi-e-limiti.md)
14. [Valutazione e miglioramento](14-valutazione-e-miglioramento.md)

### Parte 6 — Applicazioni
15. [Casi d'uso e workflow reali](15-casi-uso-e-workflow-reali.md)
16. [Glossario e risorse](16-glossario-e-risorse.md)

## Oltre ai capitoli

Il repository contiene anche:

- **Sito statico bilingue** in `website/` — versione navigabile della guida (IT + EN) con ricerca, tutor e playground. Generato da `build_site.py`; per leggerlo in locale apri `website/index.html`.
- **PDF** — `Guida-Agenti-AI.pdf` (IT) e `Guide-AI-Agents-EN.pdf` (EN), generati da `build_pdf.py`.
- **Esempi di codice runnable** in [`examples/`](examples/README.it.md) — 5 progetti Python autonomi: agent loop minimale, tool use, RAG, prompt caching, eval harness.
- **Versione inglese** dei 16 capitoli in [`en/`](en/).
- **Istruzioni di deploy** in [`DEPLOY.md`](DEPLOY.md) — Netlify, Vercel o GitHub Pages.
- **Registro di avanzamento** in [`docs/AVANZAMENTO.md`](docs/AVANZAMENTO.md) — struttura del progetto, come rigenerare sito e PDF, decisioni prese.

### Rigenerare sito e PDF

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install markdown beautifulsoup4 pygments reportlab
python3 build_site.py
python3 build_pdf.py
```

I file `.md` (in root e in `en/`) sono la fonte di verità: `website/` è output di build e non va modificato a mano.

## Come usare la guida al meglio

- **Non leggerla passivamente.** Apri ChatGPT, Claude o un terminale di fianco e prova ogni esempio.
- **Sbaglia presto.** Gli agenti AI si imparano usandoli, non studiandoli. La guida ti dà il vocabolario; la pratica ti dà l'intuito.
- **Torna indietro.** I concetti dei primi capitoli prendono senso vero solo dopo aver fatto un po' di pratica nei capitoli 8 e 10.

## Convenzioni

- **Termini in inglese**: alcuni concetti (prompt, tool, token, embedding) li lascio in inglese perché in italiano non hanno una traduzione consolidata e troverai sempre la versione inglese nella documentazione che leggerai dopo.
- **Codice**: gli esempi sono in Python (linguaggio dominante in AI). Dove utile uso TypeScript per esempi web.
- **Citazioni**: quando cito "un modello" o "l'agente" senza specificare, intendo un comportamento generale comune ai LLM moderni; quando il dettaglio dipende dal modello specifico, lo dico esplicitamente.

---

Pronto? Si parte da [Capitolo 1 — Cosa sono gli Agenti AI](01-cosa-sono-gli-agenti-ai.md).

---

## Autore

**Gabriele Bottai**
[Portfolio](https://gabrielebottai.netlify.app/) · [GitHub](https://github.com/GabrieleBottai01) · [LinkedIn](https://www.linkedin.com/in/gabriele-bottai-1825a9302/) · [X](https://x.com/bottai_gabriele)

Hai trovato un errore o qualcosa spiegato male? [Apri una issue](https://github.com/GabrieleBottai01/AgentiAI/issues).

---

© 2026 Gabriele Bottai

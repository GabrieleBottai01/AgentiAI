# 16. Glossario e risorse

## 16.1 Glossario

### A

**Agente AI** — Sistema software che usa un LLM per decidere azioni, le esegue tramite tool, osserva il risultato e ripete in un loop fino a un obiettivo o stop. (Cap. 1, 3)

**Allucinazione** — Affermazione plausibile ma falsa generata da un LLM. Dovuta al fatto che il modello predice token plausibili, non verificati. (Cap. 13)

**API key** — Credenziale per autenticare le chiamate alle API dei provider (OpenAI, Anthropic, ecc.). Va tenuta segreta.

**Architettura agentica** — Pattern strutturale di un agente: ReAct, Plan-and-Execute, multi-agent, ecc. (Cap. 4)

**Assistant message** — Messaggio prodotto dal modello in una conversazione, sia testuale che con tool call. (Cap. 2)

### B

**Backoff esponenziale** — Strategia di retry che raddoppia l'attesa a ogni tentativo (1s, 2s, 4s, 8s). Standard per rate limit. (Cap. 10)

### C

**Cache (prompt caching)** — Meccanismo che consente di pagare meno per parti del prompt riutilizzate tra chiamate. (Cap. 10)

**Chain-of-Thought (CoT)** — Tecnica di prompting che chiede al modello di ragionare passo passo prima di rispondere. (Cap. 5)

**Chunking** — Spezzare un documento in pezzi (chunk) per indicizzazione in un vector store. Tipicamente 200-500 parole con overlap. (Cap. 7)

**Claude** — Famiglia di modelli LLM di Anthropic. Modelli principali: Opus (potente), Sonnet (bilanciato), Haiku (veloce/economico).

**Claude Code** — CLI di Anthropic, agente da terminale per sviluppatori. (Cap. 9)

**Compaction** — Compressione automatica della history quando si avvicina al limite del context window. (Cap. 7)

**Context window** — Quantità massima di token che il modello può "vedere" in una chiamata. (Cap. 2)

### D

**Dataset di valutazione (eval set)** — Insieme di esempi rappresentativi usati per misurare la qualità di un agente. (Cap. 14)

**Determinismo** — Proprietà di un sistema che, dato lo stesso input, produce sempre lo stesso output. Gli LLM sono *non* deterministici per default. (Cap. 12)

### E

**Embedding** — Rappresentazione numerica (vettore) del significato di un testo. Testi simili hanno embedding vicini. (Cap. 7)

**Eval / evaluation** — Misurazione strutturata di un agente su un dataset di test. (Cap. 14)

**Extended thinking / reasoning mode** — Modalità di alcuni modelli moderni dove fanno chain-of-thought interno prima di rispondere. (Cap. 2, 5)

### F

**Few-shot prompting** — Tecnica di prompting che include esempi input/output per guidare il modello. (Cap. 5)

**Fine-tuning** — Allenamento aggiuntivo di un modello su un dataset specifico per specializzarlo. Costoso, statico (non in real-time).

**Function calling** — Vedi *tool use*. (Cap. 6)

### G

**GPT** — Famiglia di modelli LLM di OpenAI (Generative Pre-trained Transformer).

**Gemini** — Famiglia di modelli LLM di Google.

**GDPR** — Regolamento europeo sulla protezione dei dati personali. Rilevante per agenti che processano dati di utenti EU. (Cap. 13)

**Guardrails** — Vincoli e validazioni per impedire all'agente di fare cose indesiderate (es. PII filtering, toxic check).

### H

**Hallucination** — Vedi *allucinazione*.

**Hook** — In Claude Code (e in altri sistemi), script che si esegue automaticamente in risposta a eventi (es. dopo un edit). (Cap. 9)

**Human-in-the-loop (HITL)** — Pattern in cui l'umano interviene per approvare o decidere a passi critici dell'agente. (Cap. 12)

### I

**Idempotenza** — Proprietà di un'operazione che, ripetuta più volte con gli stessi parametri, produce lo stesso risultato. Importante per tool con effetti collaterali. (Cap. 12)

**Inference** — Esecuzione di un modello pre-addestrato per generare output. La parte "runtime" che paghi all'API.

### J

**JSON mode / structured output** — Modalità API che garantisce output JSON valido conforme a uno schema. (Cap. 5, 10)

### K

**Knowledge cutoff** — Data dell'ultimo training del modello. Oltre, il modello non conosce eventi/fatti senza tool. (Cap. 2)

**Knowledge base** — Insieme di documenti su cui un agente fa RAG.

### L

**LangChain / LangGraph** — Framework Python per costruire applicazioni LLM e agenti. (Cap. 11)

**LLM (Large Language Model)** — Modello di linguaggio di grandi dimensioni (Claude, GPT, Gemini, Llama, ecc.). (Cap. 2)

**Loop (agent loop)** — Il ciclo perceive → reason → act → observe → ripeti che definisce un agente. (Cap. 3)

**Lost-in-the-middle** — Effetto per cui i modelli "dimenticano" informazioni nel mezzo di prompt molto lunghi. (Cap. 2)

### M

**MCP (Model Context Protocol)** — Standard aperto per esporre tool ad agenti compatibili. (Cap. 6, 9)

**Memoria di lungo termine** — Informazioni salvate fuori dal context per persistere tra sessioni. (Cap. 7)

**Memoria episodica** — Log delle azioni passate dell'agente, per debug e learning. (Cap. 7)

**Multi-agent** — Architettura con più agenti che cooperano (orchestratore-worker, debate, swarm). (Cap. 4)

### N

**Non-determinismo** — Vedi *determinismo*.

### O

**Observability** — Capacità di vedere cosa fa il sistema in produzione (log, traces, metriche). (Cap. 11, 12)

**Orchestratore** — Componente che coordina i sottosistemi (modello, tool, memoria) di un agente. (Cap. 3, 4)

### P

**Pairwise comparison** — Tecnica di valutazione: invece di scoring assoluto, "tra A e B quale è meglio". (Cap. 14)

**Plan-and-Execute** — Architettura agentica: prima un piano completo, poi esecuzione. (Cap. 4)

**Prompt** — Tutto il testo che il modello vede prima di generare: system, user, history, tool result. (Cap. 5)

**Prompt caching** — Vedi *cache*.

**Prompt engineering** — Disciplina di scrivere prompt efficaci. (Cap. 5)

**Prompt injection** — Attacco in cui istruzioni malevole nel testo letto dall'agente lo dirottano. (Cap. 13)

**Privilege separation** — Pattern di sicurezza: tool potenti separati da contesti che leggono dati esterni non fidati. (Cap. 13)

### R

**RAG (Retrieval-Augmented Generation)** — Pattern: retrieve i chunk rilevanti da una knowledge base, includili nel prompt, genera risposta. (Cap. 7)

**ReAct** — Pattern Reason + Act: il modello alterna ragionamento e tool call. (Cap. 4)

**Reflexion / self-critique** — Pattern in cui l'agente critica e rivede il proprio output prima di consegnare. (Cap. 4)

**Re-ranker** — Modello che riordina i risultati di un retrieval per migliorare la qualità. (Cap. 7)

**Role / system prompt** — Le istruzioni di base che plasmano il comportamento del modello. (Cap. 2, 5)

### S

**Sampling** — Processo di scelta del token successivo da una distribuzione di probabilità. Controllato da temperature, top-p, top-k. (Cap. 2)

**Sandbox** — Ambiente isolato per eseguire codice generato dall'AI senza accesso al sistema host. (Cap. 13)

**SDK** — Software Development Kit, libreria del provider per accedere all'API. (Cap. 10)

**Self-consistency** — Tecnica: chiamare il modello N volte, prendere la risposta più frequente. (Cap. 5)

**Streaming** — Ricezione dei token man mano che il modello li genera, per UX migliore. (Cap. 10)

**Subagent** — Agente lanciato da un altro agente per task delegati. (Cap. 4, 9)

**System prompt** — Vedi *role*.

### T

**Temperature** — Parametro di sampling che regola creatività vs. determinismo. (Cap. 2)

**Token** — Unità in cui i modelli spezzano il testo. ~4 caratteri o 0.75 parole inglesi. (Cap. 2)

**Tokenizer** — Componente che converte testo in token e viceversa.

**Tool / function** — Funzione che il modello può chiamare. Agente = LLM + tool. (Cap. 6)

**Tool call** — Richiesta del modello di eseguire un tool con specifici parametri. (Cap. 6)

**Tool result** — Output del tool che torna al modello. (Cap. 6)

**Top-p / top-k** — Parametri di sampling alternativi/complementari a temperature. (Cap. 2)

**TTL (Time To Live)** — Quanto tempo un dato resta valido in cache. Per prompt cache: ~5 minuti. (Cap. 10)

### V

**Vector store** — DB ottimizzato per cercare embedding simili. (Cap. 7)

### W

**Web search tool** — Tool che permette all'agente di cercare nel web durante una risposta.

---

## 16.2 Risorse per approfondire

### Documentazione ufficiale

- **Anthropic** — [docs.anthropic.com](https://docs.anthropic.com)
- **OpenAI** — [platform.openai.com/docs](https://platform.openai.com/docs)
- **Google AI Studio** — [ai.google.dev](https://ai.google.dev)
- **MCP Spec** — [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Claude Code** — [docs.claude.com/en/docs/claude-code](https://docs.claude.com/en/docs/claude-code)

### Corsi e tutorial

- **DeepLearning.AI short courses** ([deeplearning.ai/short-courses](https://deeplearning.ai/short-courses)) — Andrew Ng + provider, gratuiti, brevi (1-2 ore), molto pratici. Iniziare da: "ChatGPT Prompt Engineering for Developers", "Building Agentic AI Apps", "AI Agentic Design Patterns with AutoGen".
- **Anthropic Cookbook** ([github.com/anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook)) — Notebook eseguibili con pattern reali.
- **OpenAI Cookbook** ([cookbook.openai.com](https://cookbook.openai.com)) — Idem in casa OpenAI.
- **LangChain Academy** ([academy.langchain.com](https://academy.langchain.com)) — Corsi gratuiti sui propri framework.
- **Promptingguide.ai** — Riferimento community-driven sul prompt engineering.

### Libri

- **"AI Engineering"** — Chip Huyen (2024). La guida più completa al ciclo di vita di applicazioni AI. Highly recommended.
- **"Hands-On Large Language Models"** — Jay Alammar, Maarten Grootendorst (2024). Dalla teoria a uso pratico, illustrato.
- **"Designing Machine Learning Systems"** — Chip Huyen. Pre-LLM ma ancora rilevante per l'infra.

### Paper di riferimento

- **"Attention Is All You Need"** (Vaswani et al., 2017) — il transformer.
- **"Language Models are Few-Shot Learners"** (Brown et al., 2020) — GPT-3, few-shot.
- **"ReAct: Synergizing Reasoning and Acting"** (Yao et al., 2022).
- **"Reflexion"** (Shinn et al., 2023).
- **"Toolformer"** (Schick et al., 2023).
- **"Constitutional AI"** (Bai et al., 2022) — Anthropic, sicurezza.

Tutti su [arxiv.org](https://arxiv.org) con DOI o ID. Cercali per nome.

### Newsletter e blog

- **The Batch** (DeepLearning.AI) — Settimanale, panoramica AI. ([deeplearning.ai/the-batch](https://deeplearning.ai/the-batch))
- **Import AI** (Jack Clark) — Settimanale, lungo ma profondo.
- **Lilian Weng's blog** (lilianweng.github.io) — Articoli tecnici dettagliati su agent, RLHF, ecc. Eccellente.
- **Simon Willison's blog** (simonwillison.net) — Pratico, sperimenta tutto, scrive bene.
- **Anthropic blog** ([anthropic.com/news](https://anthropic.com/news)) — Aggiornamenti sui modelli e ricerca.

### Community

- **r/LocalLLaMA** (Reddit) — Comunità self-hosted, modelli aperti.
- **r/MachineLearning** (Reddit) — Più accademica.
- **Hugging Face** ([huggingface.co](https://huggingface.co)) — Hub modelli aperti, dataset, demo.
- **Discord di LangChain, LlamaIndex, vari provider** — Domande tecniche, supporto.
- **AI Engineer Summit** (conferences.aiengineer.com) — Talks pratici.

### Tool e piattaforme da provare

- **Modelli e API**: Anthropic Console, OpenAI Playground, Google AI Studio, Together AI (open models hosted), Groq (inferenza velocissima).
- **Agenti CLI**: Claude Code, Aider, Cursor.
- **Agenti consumer**: ChatGPT, Claude.ai, Gemini, Perplexity.
- **Vector store gestiti**: Pinecone, Weaviate Cloud, Qdrant Cloud.
- **Vector store self-hosted**: Chroma, Qdrant, pgvector.
- **Observability**: Langfuse (OSS), LangSmith, Helicone, Braintrust.
- **Eval**: Promptfoo, DeepEval, Ragas.
- **Sandbox code execution**: E2B, Modal, Daytona.

### Per restare aggiornato (2026 e oltre)

Il campo si muove veloce. Strategia che funziona:

1. **Una newsletter settimanale** seguita seriamente (non 10 a metà).
2. **Un account Twitter/X** o **Bluesky** con i practitioners di riferimento (Andrej Karpathy, Simon Willison, Hamel Husain, Eugene Yan, ecc.).
3. **Un hands-on al mese**: prova un nuovo modello, framework, pattern. Costruisci qualcosa.
4. **Un paper al mese** (o un thread che lo spiega bene). Non per essere ricercatore, per capire la direzione.

Più importante di "stare aggiornato": **avere una lista di problemi tuoi** che vuoi risolvere con AI. Le novità da quel momento si auto-filtrano.

---

## 16.3 Da ricordare alla fine di tutto

Se di tutta questa guida dovessi tenere solo cinque cose:

1. **Un agente è LLM + tool + loop + obiettivo.** Tutto il resto sono dettagli.
2. **Il prompt è codice.** Versionalo, testalo, iteralo.
3. **Senza eval voli al buio.** Costruisci il dataset prima del codice.
4. **Più piccolo, più semplice, più osservabile.** Il sistema più complesso è quasi sempre il problema, non la soluzione.
5. **Costruisci qualcosa.** Leggere ti dà vocabolario, costruire ti dà intuito.

Buon viaggio.

---

← [Torna all'indice](README.md)

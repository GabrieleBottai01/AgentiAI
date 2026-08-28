# Examples — Codice runnable della guida

> 🇬🇧 [English version](README.md)

Repository di esempi self-contained per i capitoli chiave della *Guida agli Agenti AI*. Ogni cartella contiene un progetto Python autonomo con `requirements.txt` e `README.md`.

## Quick start

```bash
# Crea un virtualenv (consigliato)
python3 -m venv .venv
source .venv/bin/activate

# Installa le dipendenze del progetto specifico
cd 01-agent-loop
pip install -r requirements.txt

# Imposta la API key (Anthropic)
export ANTHROPIC_API_KEY="sk-ant-..."

# Esegui
python main.py
```

## Esempi

| Cartella | Capitolo | Cosa fa |
|---|---|---|
| `01-agent-loop` | Cap. 3 | Il loop minimale di un agente: ~70 righe, 2 tool, leggibile come pseudocodice. |
| `02-tool-use` | Cap. 6 | Tool design completo: schema preciso, error handling strutturato, multiple tools. |
| `03-rag-minimal` | Cap. 7 | RAG end-to-end: chunking, embedding, retrieval, generation con citazioni. |
| `04-prompt-caching` | Cap. 10 | Agente di research con prompt caching, retry, streaming, loop detection. |
| `05-eval-harness` | Cap. 14 | Eval harness con dataset .jsonl, programmatic checks, LLM-as-judge. |

## Convenzioni

- **Ogni esempio è indipendente.** Niente file condivisi tra cartelle.
- **API key via env var.** Mai hardcoded.
- **Output stampato a video.** Niente UI, niente file generati (salvo il vector store del RAG).
- **Modello di default `claude-haiku-4-5`** per tenere bassi i costi durante i test.

Costo medio per eseguire tutti e 5 gli esempi: **< €0.10**.

## Struttura tipica di un esempio

```
01-agent-loop/
├── README.md           # cosa fa, come si esegue, cosa imparare
├── requirements.txt    # dipendenze pin-versioned
├── main.py            # script principale, eseguibile
└── (eventuali file di supporto)
```

## Note

Gli esempi usano **Anthropic Claude** come provider primario. Per usare OpenAI/Gemini, vedi i commenti `# OpenAI:` e `# Gemini:` negli esempi: sono indicate le righe da modificare.

---

© 2026 Gabriele Bottai · Guida agli Agenti AI

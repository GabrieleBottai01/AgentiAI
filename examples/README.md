# Examples — Runnable code from the guide

Self-contained examples for the key chapters of *AI Agents — The Complete Guide*. Every folder is a standalone Python project with its own `requirements.txt` and `README.md`.

> 🇮🇹 [Versione italiana](README.it.md)

## Quick start

```bash
# Create a virtualenv (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies of the specific project
cd 01-agent-loop
pip install -r requirements.txt

# Set the API key (Anthropic)
export ANTHROPIC_API_KEY="sk-ant-..."

# Run
python main.py
```

## The examples

| Folder | Chapter | What it does |
|---|---|---|
| [`01-agent-loop`](01-agent-loop/) | Ch. 3 | The minimal agent loop: ~70 lines, 2 tools, readable as pseudocode. |
| [`02-tool-use`](02-tool-use/) | Ch. 6 | Complete tool design: precise schemas, structured error handling, multiple tools. |
| [`03-rag-minimal`](03-rag-minimal/) | Ch. 7 | End-to-end RAG: chunking, embedding, retrieval, generation with citations. |
| [`04-prompt-caching`](04-prompt-caching/) | Ch. 10 | Research agent with prompt caching, retry, streaming, loop detection. |
| [`05-eval-harness`](05-eval-harness/) | Ch. 14 | Eval harness with a `.jsonl` dataset, programmatic checks, LLM-as-judge. |

## Conventions

- **Every example is independent.** No files shared between folders.
- **API key via environment variable.** Never hardcoded.
- **Output printed to the terminal.** No UI, no generated files (except the RAG vector store).
- **Default model `claude-haiku-4-5`** to keep costs low while testing.

Average cost to run all five examples: **under $0.10**.

## Typical structure of an example

```
01-agent-loop/
├── README.md           # what it does, how to run it, what to learn
├── requirements.txt    # version-pinned dependencies
├── main.py             # main script, executable
└── (any supporting files)
```

## Notes

The examples use **Anthropic Claude** as the primary provider. To use OpenAI/Gemini instead, look for the `# OpenAI:` and `# Gemini:` comments in the code — they mark the lines to change.

---

© 2026 Gabriele Bottai · AI Agents — The Complete Guide

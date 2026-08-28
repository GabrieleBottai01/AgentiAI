# AI Agents — The Complete Guide

**A from-scratch guide to what AI agents are, how they work, and how to actually build them.**
16 chapters, fully available in **English** and **Italian**, plus a static website, PDF editions, and 5 self-contained runnable Python examples.

[![Read online](https://img.shields.io/badge/read%20online-myfirstaiagent.netlify.app-2563eb?style=flat-square)](https://myfirstaiagent.netlify.app/en/)
[![Chapters](https://img.shields.io/badge/chapters-16-16a34a?style=flat-square)](#table-of-contents)
[![Languages](https://img.shields.io/badge/languages-EN%20%7C%20IT-7c3aed?style=flat-square)](#-two-languages)
[![Examples](https://img.shields.io/badge/runnable%20examples-5-ea580c?style=flat-square)](examples/)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab?style=flat-square&logo=python&logoColor=white)](#run-the-examples)

> 🇮🇹 **Parli italiano?** Vai al [README in italiano](README.it.md).

---

## 🌐 Read it online

| | |
|---|---|
| **English website** | **https://myfirstaiagent.netlify.app/en/** |
| **Sito in italiano** | https://myfirstaiagent.netlify.app/ |
| **PDF (English)** | [`Guide-AI-Agents-EN.pdf`](Guide-AI-Agents-EN.pdf) |
| **PDF (Italiano)** | [`Guida-Agenti-AI.pdf`](Guida-Agenti-AI.pdf) |

The website includes full-text search (`Cmd/Ctrl + K`), a chapter-aware tutor, and an interactive playground.

---

## What this is

Most AI-agent material is either a marketing blog post or a framework tutorial that hides the mechanics. This guide sits in between: it explains **the mechanism first**, then shows the code.

No machine-learning background required. If you can read Python, you can follow every example.

**It's for you if:**

- "I hear about AI agents everywhere but I still don't get what makes them different from ChatGPT."
- "I want to use AI to work better, but I don't know where to start."
- "I can code, but I've never built an agent. Where do I begin?"
- "I tried a chatbot and it disappointed me. Can this be done better?"

**Every chapter follows the same structure:**

1. **Concept** — the theory, explained plainly.
2. **Practice** — concrete examples, code, real workflows.
3. **Key takeaways** — the 3–5 things that matter.
4. **Common mistakes** — the traps nearly everyone falls into.

---

## Table of contents

### Part 1 — Foundations (understanding)
1. [What AI Agents Are](en/01-cosa-sono-gli-agenti-ai.md)
2. [How LLMs Work (the engine)](en/02-come-funzionano-gli-llm.md)
3. [Anatomy of an Agent](en/03-anatomia-di-un-agente.md)
4. [Types of Agents and Architectures](en/04-tipi-di-agenti-e-architetture.md)

### Part 2 — Core techniques (talking to them)
5. [Prompt Engineering: the Art of Asking](en/05-prompt-engineering.md)
6. [Tool Use and Function Calling](en/06-tool-use-e-function-calling.md)
7. [Memory, Context and RAG](en/07-memoria-contesto-e-rag.md)

### Part 3 — Using agents (day to day)
8. [Using AI Chatbots: ChatGPT, Claude.ai, Gemini](en/08-usare-i-chatbot-ai.md)
9. [Claude Code: Terminal-Based Agent for Developers](en/09-claude-code-per-sviluppatori.md)

### Part 4 — Building agents (hands on)
10. [Building Custom Agents with API and SDK](en/10-costruire-agenti-con-api-sdk.md)
11. [Frameworks: LangChain, AutoGen, CrewAI](en/11-framework-langchain-autogen-crewai.md)

### Part 5 — Doing it well (quality and responsibility)
12. [Best Practices for Development with Agents](en/12-best-practice-sviluppo-con-agenti.md)
13. [Security, Costs, Limits](en/13-sicurezza-costi-e-limiti.md)
14. [Evaluation and Improvement](en/14-valutazione-e-miglioramento.md)

### Part 6 — Applications
15. [Real Use Cases and Workflows](en/15-casi-uso-e-workflow-reali.md)
16. [Glossary and Resources](en/16-glossario-e-risorse.md)

> The Italian chapters live in the repository root (`01-*.md` … `16-*.md`) and are indexed in [README.it.md](README.it.md).

---

## Runnable examples

Five standalone Python projects in [`examples/`](examples/README.md), each mapped to a chapter. No shared state, no framework, pinned dependencies — read them top to bottom like pseudocode.

| Folder | Chapter | What it demonstrates |
|---|---|---|
| [`01-agent-loop`](examples/01-agent-loop/) | Ch. 3 | The minimal agent loop: ~70 lines, 2 tools, readable as pseudocode. |
| [`02-tool-use`](examples/02-tool-use/) | Ch. 6 | Real tool design: precise schemas, structured error handling, idempotency keys. |
| [`03-rag-minimal`](examples/03-rag-minimal/) | Ch. 7 | End-to-end RAG: chunking, embedding, retrieval, generation with citations. |
| [`04-prompt-caching`](examples/04-prompt-caching/) | Ch. 10 | Production-grade agent: prompt caching, retry with backoff, cost tracking. |
| [`05-eval-harness`](examples/05-eval-harness/) | Ch. 14 | Eval harness: `.jsonl` dataset, programmatic checks, LLM-as-judge, A/B testing. |

### Run the examples

```bash
git clone https://github.com/GabrieleBottai01/AgentiAI.git
cd AgentiAI/examples/01-agent-loop

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

Examples default to `claude-haiku-4-5` to keep costs low. **Running all five costs well under $0.10.** API keys are always read from environment variables, never hardcoded.

---

## 🌍 Two languages

The guide is written and maintained in both languages — not machine-translated stubs. Both versions have all 16 chapters, both are on the website, both have a PDF edition.

| | English | Italiano |
|---|---|---|
| Chapters | [`en/`](en/) | root (`01-*.md` … `16-*.md`) |
| Website | [myfirstaiagent.netlify.app/en/](https://myfirstaiagent.netlify.app/en/) | [myfirstaiagent.netlify.app](https://myfirstaiagent.netlify.app/) |
| PDF | [`Guide-AI-Agents-EN.pdf`](Guide-AI-Agents-EN.pdf) | [`Guida-Agenti-AI.pdf`](Guida-Agenti-AI.pdf) |
| README | this file | [README.it.md](README.it.md) |

Technical terms (*prompt*, *tool*, *token*, *embedding*) are kept in English in the Italian edition too — that's the vocabulary you'll meet in the documentation you read next.

---

## Repository structure

```
AgentiAI/
├── 01-*.md … 16-*.md      # 16 chapters — Italian (source of truth)
├── en/                    # 16 chapters — English (source of truth)
├── examples/              # 5 standalone runnable Python projects
├── build_site.py          # Markdown → static bilingual website
├── build_pdf.py           # Markdown → PDF (EN + IT)
├── website/               # BUILD OUTPUT — deployable static site
├── static-js/             # Site sources: search, tutor, playground, i18n
├── site/                  # Earlier Flask prototype (kept for reference)
├── DEPLOY.md              # Deploy guide: Netlify / Vercel / GitHub Pages
└── docs/AVANZAMENTO.md    # Progress log & project decisions (Italian)
```

The Markdown files are the **source of truth**. `website/` is generated — never edit it by hand.

### Build the site and the PDFs yourself

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install markdown beautifulsoup4 pygments reportlab

python3 build_site.py    # → website/
python3 build_pdf.py     # → PDF, EN + IT
```

Then open `website/index.html`, or serve the folder with `python3 -m http.server -d website`.

The site is plain HTML/CSS/JS — no framework, no bundler, no `node_modules`. Deployment instructions for Netlify, Vercel and GitHub Pages are in [DEPLOY.md](DEPLOY.md).

---

## How to get the most out of it

- **Don't read passively.** Keep ChatGPT, Claude, or a terminal open next to you and try every example.
- **Fail early.** Agents are learned by using them, not by studying them. The guide gives you the vocabulary; practice gives you the intuition.
- **Come back.** The early chapters only fully click after you've built something in chapters 8 and 10.

---

## Author

**Gabriele Bottai**
[Portfolio](https://gabrielebottai.netlify.app/) · [GitHub](https://github.com/GabrieleBottai01) · [LinkedIn](https://www.linkedin.com/in/gabriele-bottai-1825a9302/) · [X](https://x.com/bottai_gabriele)

Found a mistake, or something explained badly? [Open an issue](https://github.com/GabrieleBottai01/AgentiAI/issues) — corrections in either language are welcome.

---

© 2026 Gabriele Bottai

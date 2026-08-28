# Registro di avanzamento — Guida agli Agenti AI

> File di continuità tra sessioni. **Leggilo all'inizio di ogni sessione prima di agire.**
> Va aggiornato a ogni step con: decisioni prese, file creati/modificati, problemi noti e come sono stati risolti.

---

## 1. Cos'è questo progetto

Guida didattica completa **in italiano** sugli Agenti AI, per chi parte da zero.
Path: `/Users/mac/Documents/PersonaleGB/AgentiAI`
Repo: https://github.com/GabrieleBottai01/AgentiAI

Il progetto è cresciuto da "16 capitoli markdown" a un **prodotto completo**: contenuti → sito statico bilingue → PDF → esempi di codice runnable.

## 2. Decisioni di formato consolidate

| Decisione | Stato |
|---|---|
| Capitoli modulari in file `.md` separati (no documento unico) | Consolidata |
| Taglio bilanciato teoria + pratica | Consolidata |
| Codice esempi: **Python primario**, TypeScript dove utile (web) | Consolidata |
| Lingua: italiano; termini tecnici EN consolidati (prompt, tool, token, embedding) non tradotti | Consolidata |
| Struttura fissa per capitolo: Concetto → Pratica → Da ricordare → Errori tipici | Consolidata |
| Versione inglese completa in `en/` | Consolidata |
| Sito **statico** generato da script Python (no framework JS, no build toolchain) | Consolidata |

## 3. Struttura del repository

```
AgentiAI/
├── 01..16-*.md            # 16 capitoli IT (sorgente di verità dei contenuti)
├── en/01..16-*.md         # 16 capitoli EN (traduzione allineata)
├── build_site.py          # Generatore sito statico → website/
├── build_pdf.py           # Generatore PDF IT + EN
├── website/               # OUTPUT build: sito statico pronto al deploy
│   ├── index.html, about.html, playground.html, tutor.html, agente.html
│   ├── capitolo/*.html    # 16 capitoli IT renderizzati
│   ├── en/                # sito EN
│   ├── assets/            # CSS/JS/immagini
│   ├── search-index-it.json / search-index-en.json
│   ├── sitemap.xml, robots.txt, favicon.svg
│   └── Guida-Agenti-AI.pdf / Guide-AI-Agents-EN.pdf
├── static-js/             # Sorgenti JS del sito (agent, tutor, search, i18n, playground…)
├── site/                  # Variante server-side Flask (main.py + templates/) — prototipo storico
├── examples/              # 5 progetti Python runnable e self-contained
│   ├── 01-agent-loop      # Cap.3 — loop minimale (~70 righe, 2 tool)
│   ├── 02-tool-use        # Cap.6 — tool design, schema, error handling
│   ├── 03-rag-minimal     # Cap.7 — RAG end-to-end con citazioni
│   ├── 04-prompt-caching  # Cap.10 — prompt caching, retry, streaming
│   └── 05-eval-harness    # Cap.14 — harness di valutazione
├── DEPLOY.md              # Istruzioni deploy (Netlify / Vercel / GitHub Pages)
├── README.md              # Indice e guida alla lettura
└── docs/AVANZAMENTO.md    # Questo file
```

**Regola d'oro:** i `.md` in root e in `en/` sono la **fonte di verità**. Non modificare mai a mano `website/` — si rigenera.

## 4. Come si rigenera tutto

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install markdown beautifulsoup4 pygments reportlab
python3 build_site.py     # → website/
python3 build_pdf.py      # → PDF IT + EN
```

⚠️ **Problema noto:** il Python di sistema (3.14.6) **non** ha `markdown`, `beautifulsoup4`, `pygments`, `reportlab` installati. Serve il virtualenv sopra prima di ogni rebuild, altrimenti lo script fallisce con `ModuleNotFoundError`.

## 5. Cronologia degli step

### Step 1 — Contenuti (2026-05-07)
- Scritti i 16 capitoli IT, divisi in 6 parti (Fondamenti → Tecniche → Usare → Costruire → Lavorare bene → Applicazioni).
- Tradotti tutti e 16 in `en/`.
- File: `01..16-*.md`, `en/01..16-*.md`, `README.md`.

### Step 2 — Esempi runnable (2026-05-07)
- Creati 5 progetti Python autonomi in `examples/`, ognuno con `requirements.txt` + `README.md`.
- Chiave API letta da `ANTHROPIC_API_KEY` (mai hardcoded).

### Step 3 — Sito statico bilingue (2026-05-07)
- `build_site.py` (~52 KB): markdown → HTML, navigazione, i18n IT/EN, indice di ricerca, sitemap, Open Graph, JSON-LD.
- JS in `static-js/`: ricerca client-side (Cmd+K), tutor RAG, playground, agente demo, i18n, icone.
- Prototipo Flask precedente conservato in `site/` (non più il canale principale).

### Step 4 — PDF (2026-05-07)
- `build_pdf.py` genera `Guida-Agenti-AI.pdf` (IT) e `Guide-AI-Agents-EN.pdf` (EN), copiati anche in `website/`.

### Step 5 — Documentazione deploy (2026-05-07)
- `DEPLOY.md`: tre opzioni (Netlify drag&drop, Vercel, GitHub Pages con workflow pronto), dominio custom, checklist post-deploy, Search Console.
- `SITE_BASE_URL` in `build_site.py` è il punto unico da cambiare per il dominio (impatta OG, canonical, sitemap, JSON-LD).

### Step 6 — Versionamento Git (2026-05-11)
- `git init` + primo commit `40d226f` "Initial commit: corso AgentiAI" (140 file tracciati).
- Remote `origin` → `https://github.com/GabrieleBottai01/AgentiAI.git`, push effettuato.
- `.gitignore`: `.DS_Store`, `node_modules/`, `.env`, `.env.local`, `*.log`.

### Step 7 — Pubblicazione repo (2026-08-28)
- Verificato allineamento: working tree pulito, `main` == `origin/main`, nessuna modifica pendente.
- Scan sicurezza pre-pubblicazione: **nessuna** API key, token o file `.env` nel repo. Nessun `.DS_Store` tracciato.
- Aggiunto questo registro (`docs/AVANZAMENTO.md`).
- README allineato al contenuto reale del repo (sito, PDF, esempi, deploy).
- Repository reso **pubblico**; aggiunti description e topics su GitHub.

### Step 8 — Presentazione internazionale (2026-08-28)
- **Decisione:** la landing page del repo (`README.md`) è ora in **inglese**, perché il repo è pubblico e il pubblico potenziale è internazionale. L'italiano non è stato perso: è in `README.it.md`, linkato in cima.
- Schema bilingue applicato a tutti i README: `README.md` (EN) + `README.it.md` (IT), con link incrociato 🇬🇧/🇮🇹 in testa a ciascuno.
  - root: `README.md` (nuovo, EN) / `README.it.md` (ex README italiano, arricchito)
  - `examples/README.md` (EN) / `examples/README.it.md`
  - i 5 `examples/*/README.md` (EN) / `README.it.md`
- Il nuovo README EN contiene: badge, link al sito live, "what this is", indice dei 16 capitoli EN, tabella esempi runnable, quick start, struttura del repo, istruzioni di build, sezione autore.
- **Scoperta:** il sito è **già live** su https://myfirstaiagent.netlify.app/ (IT) e `/en/` (EN) — HTTP 200 verificato. Ora è linkato in evidenza da README e dai metadati GitHub (homepage).
- Description GitHub riscritta in inglese.
- Verifica: script di controllo su tutti i link relativi dei README → 0 link rotti.

**Non fatto di proposito:** le stringhe `print()` dentro `examples/*/main.py` restano in italiano (`OBIETTIVO`, `Iterazione`, `METRICHE`…). I README EN lo dichiarano esplicitamente e traducono le etichette. Tradurre il codice richiederebbe di riallineare anche gli output di esempio dei README IT: valutare come step separato.

## 6. Problemi noti e come sono stati risolti

| Problema | Soluzione |
|---|---|
| Dipendenze Python di build assenti nel Python di sistema | Usare virtualenv dedicato (vedi §4) prima di ogni rebuild |
| `.DS_Store` sparsi nelle cartelle (macOS) | Già in `.gitignore`; verificato che nessuno sia tracciato |
| Rischio divergenza tra `.md` e `website/` | I `.md` sono la fonte di verità: dopo ogni modifica **rilanciare i due build** e committare anche `website/` |
| Il repo era privato → guida non condivisibile | Reso pubblico il 2026-08-28 |
| Repo pubblico ma vetrina solo in italiano → illeggibile per stranieri | README EN come landing page + schema bilingue EN/IT su tutti i README (Step 8) |
| MCP GitHub non connesso in sessione (`Authorization header is badly formatted`) | Usato il `gh` CLI (account `GabrieleBottai01` autenticato) |

## 7. Prossimi passi possibili (non ancora fatti)

- [ ] Attivare **GitHub Pages** con il workflow già scritto in `DEPLOY.md` §Opzione 3 (`.github/workflows/deploy.yml` non è ancora stato creato).
- [ ] Aggiornare `SITE_BASE_URL` se si passa a dominio custom.
- [ ] Submit sitemap su Google Search Console + Bing Webmaster Tools.
- [ ] Aggiungere `LICENSE` (attualmente assente: senza licenza il codice pubblico resta "all rights reserved").
- [ ] Linkare la guida dal portfolio personale.

---

_Ultimo aggiornamento: 2026-08-28 (Step 8)_

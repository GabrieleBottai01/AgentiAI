# 9. Claude Code: agente da terminale per sviluppatori

Claude Code è il prodotto che stai usando ora (probabilmente). È un **agente AI da terminale** pensato specificamente per chi scrive codice. Per chi sviluppa, è oggi uno degli strumenti più produttivi sul mercato.

## 9.1 Cosa fa Claude Code

In una frase: **un terminal-based agent che può leggere, modificare ed eseguire codice nel tuo progetto, sotto il tuo controllo**.

Diversamente da ChatGPT (chat) o GitHub Copilot (autocomplete), Claude Code:

- Ha **accesso reale al filesystem** (legge ed edita file nel tuo repo).
- Può **eseguire comandi shell** (test, build, git).
- Lavora in **loop autonomi**: gli dai un obiettivo, esegue molti passi, ti riporta.
- Chiede **conferma** prima di azioni potenzialmente distruttive.

Esempi di prompt che funzionano:

> "Trova il bug per cui il login fallisce con email maiuscola e fixalo, aggiungendo un test."

> "Refactora il modulo `payments/` per separare logica di business da quella di persistenza."

> "Aggiorna le dipendenze al major successivo, esegui i test, fixa quello che si rompe."

## 9.2 Installazione e setup base

```bash
# macOS / Linux
curl -fsSL https://claude.com/install.sh | sh

# o con npm
npm install -g @anthropic-ai/claude-code
```

Poi nel tuo progetto:

```bash
cd ~/my-project
claude
```

Si apre una sessione interattiva. Scrivi il tuo prompt, premi Invio, l'agente lavora.

## 9.3 La gerarchia dei file CLAUDE.md

Claude Code legge automaticamente file `CLAUDE.md` (e simili) per istruzioni persistenti del progetto. Ordine di precedenza:

1. **`~/.claude/CLAUDE.md`** — istruzioni globali (per tutti i tuoi progetti).
2. **`<project>/CLAUDE.md`** — istruzioni di progetto (versionato in git).
3. **`<project>/.claude/CLAUDE.local.md`** — istruzioni locali tue (gitignored).

Cosa metterci:

```markdown
# Convenzioni del progetto

- Stack: Python 3.12, FastAPI, PostgreSQL, pytest.
- Stile: Black, isort, type hints obbligatori.
- Test: ogni nuovo endpoint richiede un test di integrazione.

# Comandi utili

- `make test` — esegue test unit + integration.
- `make lint` — lancia black + ruff + mypy.
- `make migrate` — esegue le migrations.

# Cose da NON fare

- Non modificare `legacy/` senza chiedere.
- Non aggiungere dipendenze senza valutare alternative.
```

Il file viene caricato a ogni avvio. Risparmi di ripetere lo stesso contesto a ogni sessione.

## 9.4 Slash commands

Comandi che inizi con `/` per azioni speciali. I principali:

- `/help` — vedi tutti i comandi disponibili.
- `/init` — genera un `CLAUDE.md` analizzando il progetto.
- `/clear` — reset della conversazione (mantiene il working directory).
- `/compact` — comprime la storia (utile quando si avvicina al limite).
- `/review` — review della PR corrente.
- `/security-review` — review specifico per problemi di sicurezza.
- `/model` — cambia modello (es. da Sonnet a Opus per task difficili).

Puoi anche **definire i tuoi slash command** mettendo file `.md` in `.claude/commands/` con istruzioni:

```markdown
# .claude/commands/deploy.md

Esegui il deploy in staging:
1. Verifica che `main` sia pulito.
2. Tagga la versione corrente.
3. Esegui `./scripts/deploy.sh staging`.
4. Smoke test su https://staging.example.com.
5. Riporta esiti.
```

Poi in chat: `/deploy` → l'agente segue la procedura.

## 9.5 Hooks

Gli hook sono **script shell** che il sistema esegue in risposta a eventi (es. "dopo ogni edit di file", "prima di un commit"). Configurati in `~/.claude/settings.json` o `<project>/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse:Edit": [
      {
        "command": "make lint",
        "matcher": {"path_regex": "src/.*\\.py$"}
      }
    ],
    "Stop": [
      {"command": "say 'Claude ha finito'"}
    ]
  }
}
```

Esempi utili:
- Post-edit di file Python: lancia `ruff` automaticamente.
- Post-edit di test: esegue solo i test interessati.
- Stop: notifica desktop o Slack quando l'agente ha finito un task lungo.

Gli hook sono potenti perché **automatizzano controlli che altrimenti dipenderebbero dal modello**.

## 9.6 MCP server: estendere i tool

Visto nel Cap. 6: i server MCP espongono tool che Claude Code può consumare.

Configurazione in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "ghp_..."}
    }
  }
}
```

Una volta abilitati, Claude Code li vede come tool aggiuntivi disponibili. Puoi chiedere "apri la PR #123 e leggi i commenti" e l'agente userà il tool MCP GitHub.

## 9.7 Permessi e sicurezza

Claude Code chiede conferma prima di azioni rischiose. Puoi:

- **Approvare una sola volta** (default).
- **Approvare per la sessione**.
- **Aggiungere una regola permanente** in `settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(git status)",
      "Edit(src/**)",
      "Read(**)"
    ],
    "deny": [
      "Bash(rm -rf*)",
      "Edit(.env*)"
    ]
  }
}
```

Pattern consigliato:
- **Read libero**, **Edit limitato a cartelle di codice**, **Bash con whitelist** di comandi non distruttivi.
- Mai `allow: ["*"]` in settings globali.

Lo skill `fewer-permission-prompts` analizza i tuoi log e suggerisce permessi sensati.

## 9.8 Subagent: parallelizzare e specializzare

Claude Code può lanciare **subagent** per task delegati. Tipi tipici:

- **Explore** — esplora la codebase per trovare pattern, definizioni.
- **Plan** — progetta un piano di implementazione.
- **claude-code-guide** — risponde a domande sull'uso di Claude Code stesso.

Quando lanciare un subagent:
- Per ricerche ampie nel codebase (evita di "consumare" il tuo context con grep e tree).
- Per task indipendenti che possono andare in parallelo.
- Per delegare ricerca esterna mentre tu lavori sul task principale.

Esempio in chat:

> "Esplora il codebase e trovami tutti i posti dove si fa parsing di date, riportami i pattern usati."

L'agente principale lancerà un subagent di tipo `Explore` per il lavoro di ricerca, ricevendo solo il riassunto finale (e risparmiando context).

## 9.9 Workflow tipici di sviluppo con Claude Code

### Sviluppo di una feature
1. Scrivi un breve spec in chat: cosa, perché, vincoli.
2. Chiedi a Claude di **creare un piano** (`/plan` o "fammi un piano prima di scrivere").
3. Rivedi il piano, correggi se serve.
4. "Procedi". L'agente implementa, esegue test, itera.
5. Tu fai code review della diff (`git diff`).
6. Commit (manualmente o chiedendo a Claude).

### Fix di un bug
1. Descrivi il bug + come riprodurlo.
2. "Trova la causa, proponi fix con test."
3. Claude esplora, propone, scrive test, esegue.
4. Tu valuti la diff e committi.

### Refactor
1. "Refactora X per Y. Vincoli: non rompere i test, mantieni la API pubblica."
2. Lascia l'agente fare il lavoro grosso.
3. Verifica che la diff sia minima e mirata. Se gonfia, chiedi di ripartire con vincoli più stretti.

### Onboarding su un repo nuovo
1. `/init` per generare un `CLAUDE.md` di base.
2. "Spiegami l'architettura di questo repo: principali moduli, dataflow, dipendenze."
3. "Dove devo guardare per capire X?"
4. Salva le scoperte in `CLAUDE.md`.

## 9.10 Tips operativi

- **Una sessione = un task.** Non usare la stessa sessione per refactor + nuova feature + bug fix. Crea sessioni separate, o usa `/clear`.
- **Dai contesto narrativo, non ordini secchi.** "Stiamo migrando da X a Y, oggi tocca al modulo Z, attento al test E che è flaky" → molto più efficace di "modifica file W".
- **Verifica le diff prima del commit.** L'agente è bravo, non perfetto. `git diff` è il tuo amico.
- **Usa il piano mode (`/plan`)** per task >30 minuti di lavoro: vedi cosa farà prima che lo faccia.
- **Quando si blocca, dagli più contesto, non più ordini.** Se non capisce, di solito mancano informazioni.
- **Scrivi `CLAUDE.md` man mano**: ogni volta che spieghi una convenzione una volta, scrivila lì. Risparmi tempo per sempre.
- **Limiti di iterazione**: per task lunghi, l'auto-compaction comprime la storia. Funziona bene ma nei task chirurgici può perdere dettagli — preferisci sessioni focalizzate.

## 9.11 Differenze con Cursor, Aider, Copilot

| Strumento | Modello | Pattern |
|---|---|---|
| **Claude Code** | Agente con loop, in terminale | Tu dai obiettivi, lui agisce |
| **Cursor** | IDE-first con AI integrata | Mix di autocomplete + chat in IDE |
| **Aider** | Agent CLI simile a Claude Code | Pre-Claude Code, modello-agnostico |
| **Copilot** | Autocomplete in editor | Suggerisce mentre scrivi |

Non sono mutuamente esclusivi. Molti dev usano Claude Code per task grossi e Copilot/Cursor per il flow quotidiano di typing.

## 9.12 Pratica: il primo task vero

Apri un tuo progetto in Claude Code e prova questo:

> "Analizza il progetto e dimmi: 1) cosa fa in 3 frasi, 2) le 3 aree con più debito tecnico, 3) un quick win che potresti fare oggi."

In 5 minuti avrai un'analisi che richiederebbe ore a un nuovo dev. Da lì, decidi se vuoi farti aiutare a sistemare uno dei punti.

## 9.13 Da ricordare

- **Claude Code = agente da terminale per dev.** Legge, edita, esegue codice nel tuo repo, con conferma.
- **CLAUDE.md** salva le convenzioni del progetto: scrivi una volta, riutilizzi sempre.
- **Slash commands** automatizzano procedure ripetute.
- **Hooks** lanciano script in risposta a eventi (lint dopo edit, notifica a fine task).
- **MCP** estende i tool disponibili.
- **Subagent** per task delegabili senza saturare il context principale.
- **Permessi a whitelist**, mai "permetti tutto".

## 9.14 Errori tipici

- **Usarlo come ChatGPT in chat.** Senza dargli accesso ai file, sprechi il 90% del valore.
- **Saltare il piano** per task >30 minuti. Risultato: lavoro che va fuori scope.
- **Non scrivere `CLAUDE.md`.** Ripeti le stesse istruzioni a ogni sessione.
- **Dare permessi troppo larghi.** "Permetti Bash" = l'agente può fare `rm -rf` senza chiedere.
- **Non rivedere le diff.** Il commit è tua responsabilità, non sua.
- **Sessioni troppo lunghe e mischiate.** Un task = una sessione, riapri quando cambi obiettivo.

---

Hai imparato a usare gli agenti già pronti. Adesso passiamo alla **costruzione**: come si fa un agente da zero, con codice tuo.

→ [Capitolo 10 — Costruire agenti con API e SDK](10-costruire-agenti-con-api-sdk.md)

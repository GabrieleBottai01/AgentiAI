# 4. Tipi di agenti e architetture

Lo schema base del Cap. 3 è solo l'inizio. Negli ultimi anni sono emersi **pattern architetturali** che si adattano a compiti diversi. Conoscerli ti permette di scegliere la forma giusta invece di reinventare la ruota.

## 4.1 ReAct: pensiero + azione

**ReAct** (Reasoning + Acting) è il pattern più semplice ed è quello che hai visto nel Cap. 3. A ogni turno l'agente:

1. **Reason** — pensa a cosa fare, scrivendo (anche solo internamente) un breve ragionamento.
2. **Act** — chiama un tool.
3. **Observe** — riceve il risultato.

Pattern letterale di prompt:

```
Domanda: {goal}

Pensiero: devo cercare X
Azione: web_search("X")
Osservazione: ...

Pensiero: ora confronto Y e Z
Azione: ...
Osservazione: ...

...

Risposta finale: ...
```

**Quando usarlo:** task lineari dove ogni passo dipende dal precedente. Ricerca, debug semplice, q&a su documenti.

**Limite:** se il task richiede coordinamento di più sotto-task, ReAct fa fatica perché ragiona "un passo alla volta" senza visione d'insieme.

## 4.2 Plan-and-Execute

Variante: prima il modello produce un **piano completo**, poi un esecutore (a volte lo stesso modello, a volte un modello più piccolo) lo esegue.

```
Pianificatore:
  1. Cerca articoli su "X"
  2. Estrai i 5 più citati
  3. Riassumi ognuno
  4. Confronta i punti di vista
  5. Produci sintesi finale

Esecutore: esegue 1 → esegue 2 → esegue 3 → ...
```

**Quando usarlo:**
- Task con molti passi indipendenti (puoi parallelizzare).
- Quando l'utente vuole **vedere e approvare il piano** prima dell'esecuzione (es. azioni rischiose).
- Quando l'esecuzione è costosa e vuoi evitare di "scoprire" a metà strada che l'approccio era sbagliato.

**Limite:** se il piano è sbagliato, l'agente lo esegue alla cieca. Spesso si aggiunge un meccanismo di **re-planning**: se uno step fallisce, torna al pianificatore.

## 4.3 Reflexion / Self-critique

L'agente, dopo aver prodotto una risposta o un'azione, **critica sé stesso** prima di consegnarla. Spesso si fa con un secondo prompt:

```
[Primo turno]
Soluzione proposta: ...

[Secondo turno: critique]
Rivedi la soluzione sopra. Trovi errori, casi non considerati, assunzioni discutibili?

[Terzo turno: revisione]
Sulla base della critica, rivedi la soluzione.
```

**Quando usarlo:** scrittura di codice, redazione di testi importanti, analisi quantitative. Migliora la qualità a costo di più token.

**Limite:** non magico. Se il modello è sbagliato sul concetto, anche la critica lo sarà.

## 4.4 Multi-agente: orchestratore + worker

Un agente "regista" coordina diversi agenti specializzati. Esempio: un agente di product management che delega a un agente backend, uno frontend, uno QA.

```
                ┌─────────────────┐
                │   ORCHESTRATORE │
                │ (decide chi fa) │
                └────────┬────────┘
            ┌───────────┼───────────┐
            ▼           ▼           ▼
       ┌────────┐  ┌────────┐  ┌────────┐
       │  Web   │  │ Coder  │  │ Writer │
       │researcher│ │       │  │        │
       └────────┘  └────────┘  └────────┘
```

**Quando usarlo:**
- Task molto eterogenei dove servono "competenze" diverse.
- Quando vuoi un **system prompt specializzato** per ciascun ruolo (un coder è più efficace con un prompt da coder).
- Quando vuoi parallelizzare lavoro indipendente.

**Limite:** complessità di coordinamento. Più agenti = più token = più tempo = più punti di fallimento.

In Claude Code, ad esempio, l'agente principale può lanciare **subagent** per task delegati (Explore, Plan, ecc.). È il pattern orchestratore-worker applicato al coding.

## 4.5 Multi-agente: dibattito / consenso

Più agenti propongono soluzioni indipendenti, poi confrontano. Utile quando l'incertezza è alta e vuoi più "punti di vista":

```
Agente A propone:  "Usiamo PostgreSQL"
Agente B propone:  "Usiamo MongoDB"
Agente C (giudice): "A ha ragione perché i dati sono relazionali..."
```

**Quando usarlo:** decisioni di design, analisi critiche, valutazioni dove più prospettive aiutano.

**Limite:** spesso il "consenso" converge su risposte mediocri (l'AI tende all'accomodamento). Funziona meglio se i ruoli sono *davvero* diversi.

## 4.6 Swarm / market-based

Tanti agenti più piccoli, ognuno con un sub-obiettivo, che competono o collaborano in modo decentralizzato. Pattern affascinante in ricerca, raro in produzione perché difficile da debuggare.

## 4.7 Tool-using agent vs. Code-generating agent

Una distinzione pratica importante.

- **Tool-using agent**: l'agente chiama tool predefiniti. Hai controllo fine sui tool disponibili, audit semplice. Esempio: agente customer support che usa `search_kb()`, `create_ticket()`, `send_email()`.

- **Code-generating agent**: l'agente *scrive codice* (di solito Python) e lo esegue in un sandbox. Estremamente flessibile — qualsiasi cosa Python può fare, l'agente può fare. Estremamente pericoloso se non è sandboxato bene.

Esempi noti del secondo tipo: ChatGPT con Code Interpreter, Claude con il tool `code_execution`, Open Interpreter.

**Tradeoff:**
- Tool-using = sicuro, prevedibile, limitato.
- Code-generating = flessibile, potente, rischioso.

Per molti casi reali, il code-generating risolve in 1 passo quello che un tool-using risolve in 10. Ma vuoi che giri solo in ambienti isolati.

## 4.8 Ambient agent / always-on

Agenti che girano in background, monitorando eventi e agendo solo quando serve. Esempi:

- Un agente che guarda la tua casella email e archivia/etichetta automaticamente.
- Un agente che monitora i log di produzione e apre un ticket quando vede un'anomalia.
- Un agente che osserva un repo Git e propone refactor.

Tecnicamente sono agenti che vengono "svegliati" da un trigger (cron, webhook, evento) e poi seguono il loop normale.

**Quando usarli:** monitoraggio, automazione di workflow ripetitivi.

**Attenzione:** poiché agiscono senza che tu sia presente, le **autorizzazioni** vanno definite con grande cura. Un agente always-on che può scrivere su Slack o cancellare file richiede review umana sui passi critici.

## 4.9 Confronto rapido: che pattern scelgo?

| Caso | Pattern consigliato |
|---|---|
| Q&A con ricerca multi-step | ReAct |
| Task con piano lungo, vuoi visibilità | Plan-and-Execute |
| Codice o testi importanti, vuoi qualità | ReAct + Reflexion |
| Task molto eterogenei | Orchestratore + worker |
| Decisione di design difficile | Multi-agente debate |
| Calcoli/trasformazioni dati arbitrarie | Code-generating agent |
| Monitoraggio in background | Ambient agent (event-driven) |

Non sono mutuamente esclusivi: un sistema reale spesso ne combina due o tre.

## 4.10 Pratica: identifica l'architettura

Apri questi prodotti e prova a riconoscere il pattern (è un esercizio mentale, non c'è una sola risposta giusta):

- **ChatGPT con "Deep Research"**: produce un piano, poi naviga il web per ore, poi sintetizza. → Plan-and-Execute, code-generating sui risultati.
- **Claude Code**: agente principale con subagent per esplorazione/pianificazione. → Orchestratore + worker, ReAct.
- **Cursor / Aider**: autocomplete + edit di codice in tempo reale. → Più strumento che agente "vero" (poco loop).
- **Devin**: agente autonomo per coding. → Plan-and-Execute, code-generating.
- **Zapier AI**: workflow scriptato che chiama LLM in alcuni step. → Automazione con AI, non agente.

## 4.11 Da ricordare

- **ReAct** è il pattern di partenza, semplice e potente.
- **Plan-and-Execute** quando vuoi visibilità sul piano o paralleizzazione.
- **Reflexion** quando la qualità conta più della velocità.
- **Multi-agente** quando i task sono eterogenei o vuoi specializzazione di ruolo.
- **Code-generating** è la massima flessibilità ma chiede sandbox seri.
- **Ambient agent** = agente attivato da eventi anziché da prompt.
- **Combinare pattern è normale e spesso migliore di sceglierne uno solo.**

## 4.12 Errori tipici

- **Iniziare multi-agente prima del singolo.** Quasi sempre un singolo agente ben fatto basta. Multi-agente è una scelta consapevole, non un default.
- **Plan-and-Execute con piani troppo dettagliati.** Se il piano ha 30 step, sei di nuovo nel ReAct. Mantieni piani di 3-7 step.
- **Reflexion infinito.** "Critica e rivedi" può loopare. Imponi *un solo* round di critica.
- **Ignorare il pattern "ambient"** quando in realtà serve solo automazione standard. Non tutto deve avere un loop.

---

Abbiamo coperto i fondamenti architetturali. Adesso passiamo alle **tecniche pratiche** per ottenere il massimo dagli agenti, partendo dalla più importante: il prompt engineering.

→ [Capitolo 5 — Prompt engineering](05-prompt-engineering.md)

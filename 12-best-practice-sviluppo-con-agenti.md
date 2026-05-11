# 12. Best practice di sviluppo con agenti

Questo capitolo è la condensa di **buone abitudini** raccolte nei capitoli precedenti, più alcuni pattern che valgono trasversalmente. Pensalo come un checklist da rivedere prima di mettere un agente in mano agli utenti.

## 12.1 La regola d'oro: piccolo, semplice, osservabile

Il singolo principio che riassume tutto:

> **Inizia piccolo, mantienilo semplice, rendilo osservabile.**

- **Piccolo**: meno tool, meno passi, meno token. Crescere è facile, semplificare è difficile.
- **Semplice**: un agente lineare con 5 tool ben fatti supera quasi sempre un sistema multi-agente complesso.
- **Osservabile**: senza visibilità su cosa fa l'agente, ogni bug è un mistero.

## 12.2 Workflow di sviluppo consigliato

### Fase 1 — Dataset di valutazione (PRIMA del codice)
Sembra nerd, ma è la cosa che separa i pro dai dilettanti.

Crea un file (`evals.jsonl`) con 20-50 esempi rappresentativi:

```json
{"input": "Trova il CEO di Anthropic", "expected_contains": ["Dario Amodei", "Anthropic"]}
{"input": "Calcola 837 * 924", "expected_contains": ["773388"]}
{"input": "Riassumi sezione X del documento Y", "expected_format": "max 3 bullet"}
```

A questo dataset misurerai ogni cambiamento. Vedremo eval più estesi nel Cap. 14.

### Fase 2 — V1 minima
Un singolo agente, 3-5 tool, prompt semplice. Run sul dataset eval, misura la qualità.

### Fase 3 — Iterazione mirata
Guarda i casi falliti del dataset. Cerca pattern. Migliora UN cambiamento alla volta:
- Il prompt? Cambialo, rimisura.
- I tool? Aggiungi/migliora descrizioni, rimisura.
- Il modello? Prova uno più capace o uno più piccolo, rimisura.

### Fase 4 — Hardening per produzione
- Retry, timeout, error handling.
- Limiti di iterazione e budget.
- Logging e tracing.
- Test di carico (latency con N utenti concorrenti).
- Permessi e safety.

### Fase 5 — Rollout graduale
- Beta interna.
- Feature flag per attivare con % di utenti.
- Confronto A/B vs. baseline (es. processo manuale).
- Espansione se le metriche lo confermano.

## 12.3 Prompt sotto controllo versione

I prompt sono codice. Trattali come tali:

- **In repository git**, non in chat o documenti random.
- **Versionati**: `prompts/v1.txt`, `v2.txt` o cambialog dentro.
- **Testati**: ogni cambio prompt → riesegui eval suite.
- **Citati nel codice** come costanti, non hardcoded sparsi.

```python
# bene
from prompts import RESEARCH_AGENT_SYSTEM
client.messages.create(system=RESEARCH_AGENT_SYSTEM, ...)

# male
client.messages.create(system="Sei un agente che...", ...)  # ovunque nel codebase
```

## 12.4 Separare logica e LLM

L'LLM è bravo a **giudicare**, brutto a **calcolare**. Linea guida:

| Cosa fa l'LLM | Cosa fa il codice |
|---|---|
| Capire intento | Validare formati |
| Generare testo | Calcolare numeri |
| Classificare | Fare regex precise |
| Riassumere | Database query |
| Decidere quale tool | Eseguire transazioni |

Se ti accorgi che stai chiedendo all'LLM di fare aritmetica, regex, o lookup esatti — **dagli un tool**, non un prompt.

## 12.5 Idempotenza dei tool

Tool con effetti collaterali (write su DB, invio email) dovrebbero essere **idempotenti** o **deduplicabili**.

L'agente può ritentare. Senza idempotenza, ritenta = duplicare.

Pattern:

```python
def send_email(to: str, subject: str, body: str, idempotency_key: str = None):
    if idempotency_key and already_sent(idempotency_key):
        return {"status": "already_sent", "key": idempotency_key}
    # invia
    record_sent(idempotency_key)
    return {"status": "sent", "key": idempotency_key}
```

Anche per le API esterne, prediligi quelle con idempotency key (Stripe, ecc.).

## 12.6 Human-in-the-loop dove serve

Per azioni costose o irreversibili:

```python
def process_refund(user_id: str, amount: float):
    if amount > 100:
        return ask_human(
            f"Rimborso di €{amount} a user {user_id}. Confermare? (sì/no)"
        )
    return execute_refund(user_id, amount)
```

L'agente capisce che `ask_human` è un tool come gli altri, lo chiama, e riceve la decisione.

Pattern per varie soglie:

- **Read-only**: nessuna conferma.
- **Write reversibile**: log + alert in caso di anomalia.
- **Write costosa o irreversibile**: conferma esplicita.
- **Bulk operation**: dry-run obbligatorio prima dell'esecuzione vera.

## 12.7 Test e tipi di test

Test comuni per un sistema basato su agenti:

### Unit test sui tool
Tool pure, senza LLM. Test classici.

### Eval test sul comportamento dell'agente
Dato un input, verifica che la risposta soddisfi criteri (contiene parole chiave, formato corretto, fa la cosa giusta). Vedremo come scriverli nel Cap. 14.

### Test di regressione su prompt
Quando cambi un prompt, riesegui la suite. Output diverso dalla baseline → review.

### Smoke test in produzione
Un canary che gira ogni 5 minuti con un input noto. Se la risposta è strana, alert.

### Test di costi
Limite massimo di token per richiesta. Se superato, errore. Evita esplosioni in produzione.

## 12.8 Determinismo e riproducibilità

Gli LLM non sono deterministici. Per debug e test:

- **Temperature 0** + seed (dove disponibile) → output (quasi) stabile.
- **Caching delle chiamate** durante test (es. VCR.py per Python): registri una volta, poi rieseguì offline.
- **Snapshot testing**: salvi l'output di una run e segnali differenze rispetto a baseline.

Mai fare test che dipendono da output testuale esatto: piccole variazioni rompono test sani. Usa pattern matching, contains, validazione strutturale.

## 12.9 Sicurezza dei prompt

I prompt possono essere attaccati (Cap. 13). Difese principali:

- **Separa istruzioni da dati**: usa delimitatori chiari (`<doc>...</doc>`).
- **Whitelist dei tool**: l'agente non deve poter chiamare tool non esplicitamente abilitati.
- **Validazione output**: se output JSON, valida con schema. Se output libero, controlla che non contenga comandi (PII, SQL, codice).
- **Privilege separation**: l'agente che parla con l'utente esterno non deve avere gli stessi tool di quello interno.

## 12.10 Costi sotto controllo

- **Budget per richiesta**: cap di token.
- **Budget giornaliero/mensile** sul provider, con alert.
- **Modello adattivo**: per richieste semplici, modello piccolo. Per complesse, grande. Decidi tu o lascia decidere a un router (LLM piccolo che classifica la difficoltà).
- **Caching aggressivo**: prompt caching, cache di tool result deterministici, cache di embedding.

Esempio router semplice:

```python
def route_model(task: str) -> str:
    if "summarize" in task.lower() or "translate" in task.lower():
        return "claude-haiku-4-5"   # economico
    if "design" in task.lower() or "architect" in task.lower():
        return "claude-opus-4-7"    # capace
    return "claude-sonnet-4-6"      # default
```

## 12.11 Pair programming con AI

Per coding personale (con Claude Code, Cursor, ecc.) ci sono pattern che fanno la differenza:

### Spec prima, codice poi
Dedica i primi 5-10 minuti a spiegare *cosa* vuoi e *perché*. L'agente codifica meglio con un buon brief che con dieci correzioni successive.

### Diff piccoli, review veri
Lascia che l'agente faccia 3-4 cambi mirati, poi rivedi `git diff`. Resistere alla tentazione di "lascialo andare per un'ora" — quando torni, hai 800 righe da capire.

### Testare insieme
Chiedi all'agente di scrivere il test prima dell'implementazione. Anche se non sei un purista TDD, in coding con AI funziona benissimo: il test fissa l'intento.

### Rifiuta il codice cattivo
Se la diff è gonfia o aggiunge complessità inutile, dì "no, semplifica, rifai". Non accettare per non offendere — il modello non si offende.

### Investi nei file di contesto
`CLAUDE.md`, hook, slash command: l'investimento nelle "infrastrutture" del tuo workflow paga in produttività esponenziale.

### "Pensa con voce"
Per problemi difficili, chiedigli di **ragionare prima di agire**. "Spiegami il piano in 5 punti, poi procedi." Spesso la pianificazione esplicita rivela errori nel suo ragionamento prima che li esegua.

## 12.12 Evita il "cargo cult"

Il campo è giovane. Tante "best practice" su Twitter sono ipotesi non testate. Mantieni scetticismo:

- **Le frasi magiche** ("you are a 10x engineer", "take a deep breath") di solito non aiutano nei modelli moderni.
- **Catene di pensiero forzate** sui modelli che già fanno CoT internamente → token sprecati.
- **Multi-agent ovunque** è una moda che si sta ridimensionando: nei test, un agente solo con buon reflection vince spesso.
- **RAG di default** non sempre serve: se il dataset entra in 1M token e la query è una sola, il context lungo è più semplice.

**Test prima di credere.** Una linea base senza X, una con X, misura.

## 12.13 Documentare l'agente

L'agente in produzione è un sistema. Va documentato:

- **Cosa fa** (scope chiaro, cosa NON fa).
- **Tool che può chiamare** e cosa fanno.
- **Permessi e limiti** (chi può usarlo, su quali dati, con che SLA).
- **Failure mode noti** (cosa succede se X fallisce, dove guardare).
- **Come si valuta** (link al dataset eval, metriche di riferimento).
- **Come si modifica** (dove sono i prompt, come si testa una modifica).

Un README a fianco del codice, semplice. Quando arriva una persona nuova nel team, ti ringrazia.

## 12.14 Da ricordare

- **Piccolo, semplice, osservabile.** Una sola frase per riassumere tutto.
- **Eval dataset prima del codice.** Senza, voli alla cieca.
- **Prompt come codice**: versionati, testati.
- **Logica/calcoli al codice, giudizio all'LLM.**
- **Idempotenza dei tool**, **human-in-the-loop** dove costa caro.
- **Test multipli**: unit, eval, regressione, smoke, costi.
- **Pair programming AI**: spec prima, diff piccoli, test insieme.
- **Scetticismo sulle mode**. Misura, non credere.

## 12.15 Errori tipici

- **Lanciare in produzione senza eval suite.** Cambierai cose senza saper se peggiorano.
- **Lasciare prompt sparsi nel codebase.** Diventano impossibili da auditare.
- **Tool non idempotenti** + retry attivo = doppio invio, doppio addebito.
- **Niente `ask_user` per casi ambigui.** L'agente inventa.
- **Multi-agent come default** = 3x i costi senza guadagno qualità.
- **Fidarsi del modello senza test.** "Va bene quando provo", e poi in produzione fa una cosa strana.

---

Buone pratiche di sviluppo coprono il "come". Adesso parliamo del "cosa può andare storto": sicurezza, costi, limiti.

→ [Capitolo 13 — Sicurezza, costi, limiti](13-sicurezza-costi-e-limiti.md)

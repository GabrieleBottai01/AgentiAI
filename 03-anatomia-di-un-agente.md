# 3. Anatomia di un agente

Sappiamo cos'è un agente (Cap. 1) e come funziona il suo motore (Cap. 2). Ora apriamo il cofano: di quali pezzi è fatto un agente, e come si combinano.

## 3.1 Lo schema mentale

Tieni in mente questo schema. È letteralmente l'intero capitolo in un disegno.

```
                ┌──────────────────────────────────────┐
                │            AGENT LOOP                │
                │                                      │
   obiettivo ──▶│   1. PERCEPIRE   (cosa è successo)   │
                │           │                          │
                │           ▼                          │
                │   2. RAGIONARE  (cosa fare adesso)   │  ◀── LLM
                │           │                          │
                │           ▼                          │
                │   3. AGIRE       (chiamo un tool)    │  ◀── Tool
                │           │                          │
                │           ▼                          │
                │   4. OSSERVARE   (cosa è cambiato)   │
                │           │                          │
                │           └──── back to 1 ───────────┤
                │                                      │
                │   5. STOP    (obiettivo raggiunto?)  │
                └──────────────────────────────────────┘
                              │
                              ▼
                       risposta finale
```

**Il loop è il cuore di tutto.** Tutto il resto sono dettagli su come implementare ogni passo.

## 3.2 Le quattro componenti fondamentali

### a. Il modello (cervello)
È l'LLM. Riceve in input lo stato corrente (tutto quello che è successo finora) e produce un output: una risposta finale, oppure la richiesta di chiamare un tool.

### b. I tool (mani e occhi)
Sono le funzioni che l'agente può chiamare per **agire** (scrivere file, fare richieste HTTP) o **percepire** (leggere file, cercare nel web). Senza tool, l'agente è cieco e immobile — può solo parlare.

Esempi tipici di tool:
- `read_file(path)` — leggere un file
- `web_search(query)` — cercare nel web
- `run_python(code)` — eseguire codice Python
- `send_email(to, subject, body)` — inviare email
- `query_database(sql)` — interrogare un DB

I tool sono dichiarati con uno **schema** (di solito JSON Schema) che descrive nome, parametri e descrizione. Il modello legge lo schema e decide quando e come chiamarli (Cap. 6).

### c. La memoria (taccuino)
L'agente ha bisogno di ricordare cosa ha fatto. Ci sono diversi livelli:

- **Memoria di breve termine** = il context window. Tutta la conversazione in corso viene rimandata al modello a ogni passo. È la memoria "di lavoro".
- **Memoria di lungo termine** = informazioni salvate fuori dal contesto (file, database, vector store) e richiamate quando servono. Permette all'agente di "ricordare" cose tra sessioni diverse (es. preferenze utente, fatti del progetto).
- **Memoria episodica** = log delle azioni passate. Utile per il debug e per evitare di rifare le stesse cose.

Vedremo memoria e RAG in dettaglio nel Cap. 7.

### d. L'orchestratore (regista)
Il pezzo di codice che tiene insieme tutto: prende l'output del modello, esegue i tool richiesti, raccoglie i risultati, li rimanda al modello, controlla la condizione di stop. È quello che scrivi tu (o usa un framework — Cap. 11).

## 3.3 Esempio passo-passo: un agente che cerca informazioni

Vediamo il loop in azione. Obiettivo: **"Trova chi è il CEO di Anthropic e quando è nata l'azienda"**.

**Turno 1**

```
Stato: messaggio utente "Trova chi è il CEO di Anthropic e quando è nata l'azienda"

LLM pensa: "Mi serve fare una ricerca."
LLM produce: tool_call("web_search", query="CEO Anthropic founding year")

Orchestratore: esegue web_search → riceve risultati (snippet di pagine)
```

**Turno 2**

```
Stato: tutto il turno 1 + risultato della ricerca

LLM pensa: "Ho info parziali, mi serve aprire un link affidabile."
LLM produce: tool_call("fetch_url", url="https://www.anthropic.com/company")

Orchestratore: esegue fetch_url → riceve HTML
```

**Turno 3**

```
Stato: tutti i turni precedenti + contenuto della pagina

LLM pensa: "Ho l'info che serve."
LLM produce: risposta finale "Il CEO di Anthropic è Dario Amodei. L'azienda è stata fondata nel 2021."

Orchestratore: nessun tool da eseguire → STOP, ritorna la risposta.
```

Tre turni di LLM, due chiamate tool, una risposta. **Questo è un agente.**

## 3.4 Lo "stato" dell'agente: cosa contiene

A ogni turno, il modello riceve in input uno stato che cresce. Tipicamente:

```python
state = [
    {"role": "system", "content": "Sei un agente di ricerca..."},
    {"role": "user", "content": "Trova il CEO di Anthropic"},
    {"role": "assistant", "tool_calls": [{"name": "web_search", ...}]},
    {"role": "tool", "content": "Risultati: ..."},
    {"role": "assistant", "tool_calls": [{"name": "fetch_url", ...}]},
    {"role": "tool", "content": "<html>..."},
    {"role": "assistant", "content": "Il CEO è Dario Amodei..."},
]
```

Notare due cose:

1. **Lo stato è la storia completa.** Ogni turno il modello rivede tutto.
2. **Cresce velocemente.** 10 turni con tool che ritornano HTML possono saturare il context window. La gestione del contesto è una skill cruciale (Cap. 7).

## 3.5 La condizione di stop

Quando l'agente smette? Quattro casi tipici:

1. **Stop naturale**: il modello non chiama più tool e produce una risposta finale.
2. **Limite di iterazioni**: l'orchestratore ferma l'agente dopo N turni (es. 25). Salvavita contro loop infiniti.
3. **Limite di budget**: l'agente ha consumato troppi token / soldi → stop.
4. **Stop esplicito dell'utente**: in CLI come Claude Code, un `Esc` interrompe.

**Importante**: senza un limite di iterazioni, un agente può loopare per sempre (es. continua a chiamare lo stesso tool perché interpreta male un errore). Mettilo *sempre*.

## 3.6 Planning: pensare prima di agire

Gli agenti più sofisticati separano due fasi:

- **Planning**: il modello produce un piano in linguaggio naturale ("Per rispondere farò questi passi: 1. cerco X, 2. analizzo Y, 3. confronto").
- **Execution**: l'agente esegue il piano un passo alla volta, con i tool.

Vantaggi del planning esplicito:
- L'utente può **rivedere il piano** prima di lasciar agire l'agente (utile per azioni rischiose).
- L'agente è meno propenso a divagare.
- Si può parallelizzare l'esecuzione di passi indipendenti.

Svantaggi:
- Più lento (un passo in più di LLM).
- Se il piano è sbagliato, l'agente esegue cose inutili.

Vedremo l'architettura "Plan-and-Execute" nel Cap. 4.

## 3.7 Pratica: un loop minimale in Python (pseudo-codice)

Per fissare l'idea, ecco lo scheletro di un agente in pseudo-Python. Non è ancora codice runnable (lo vedremo nel Cap. 10), ma legge come prosa.

```python
def agent_loop(goal: str, tools: dict, max_iterations: int = 25):
    history = [
        {"role": "system", "content": "Sei un agente. Usa i tool quando servono."},
        {"role": "user", "content": goal},
    ]

    for step in range(max_iterations):
        # 1. Chiama il modello con tutto lo stato
        response = llm.chat(messages=history, tools=list(tools.values()))

        # 2. Aggiorna la storia con la risposta del modello
        history.append(response.message)

        # 3. Se non ci sono tool da chiamare, abbiamo finito
        if not response.tool_calls:
            return response.content

        # 4. Esegui i tool richiesti
        for call in response.tool_calls:
            result = tools[call.name](**call.arguments)
            history.append({"role": "tool", "content": result, "tool_call_id": call.id})

    return "Limite di iterazioni raggiunto."
```

Questo è davvero il 90% di quello che serve sapere per costruire un agente da zero. Il resto è migliorare i tool, gestire errori, aggiungere memoria.

## 3.8 Da ricordare

- **Loop = anima dell'agente.** Percepire → ragionare → agire → osservare → ripetere.
- **Quattro componenti**: modello, tool, memoria, orchestratore.
- **Lo stato è la storia.** Tutto il dialogo viene rimandato al modello a ogni turno.
- **Definisci sempre un limite di iterazioni.** Evita loop infiniti.
- **Planning esplicito** è utile per task complessi e per la trasparenza con l'utente.

## 3.9 Errori tipici

- **Loop senza limite.** L'agente entra in spirale, brucia 10€ di token in 5 minuti.
- **Tool senza descrizione.** Se non spieghi al modello *quando* usare un tool, sceglierà a caso.
- **Tool che restituiscono troppo.** Un tool che torna 10MB di HTML satura il contesto. Tronca, riassumi, paginazione.
- **Mischiare logica e LLM.** Tutto ciò che è deterministico (validazioni, calcoli precisi) tienilo nel codice; lascia all'LLM solo ciò che richiede giudizio.
- **Cambiare comportamento solo nel system prompt.** A volte un tool ben progettato è più efficace di tre paragrafi di istruzioni.

---

Adesso che sai com'è fatto un agente, vediamo le **diverse forme** che può prendere: ReAct, Plan-and-Execute, multi-agente. Ognuna risolve problemi diversi.

→ [Capitolo 4 — Tipi di agenti e architetture](04-tipi-di-agenti-e-architetture.md)

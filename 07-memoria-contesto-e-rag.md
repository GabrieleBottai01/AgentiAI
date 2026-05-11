# 7. Memoria, contesto e RAG

Un agente senza memoria è come un consulente con amnesia: ti aiuta benissimo per 5 minuti, poi dimentica chi sei. Vediamo come dargli memoria, e quando serve **portare informazione esterna nel contesto** invece di sperare che il modello la sappia.

## 7.1 I tre tipi di memoria

```
┌──────────────────────────────────────┐
│        Memoria di lavoro             │  ← context window
│  (la conversazione in corso)         │
├──────────────────────────────────────┤
│        Memoria di lungo termine      │  ← file / DB / vector store
│  (preferenze utente, fatti stabili)  │
├──────────────────────────────────────┤
│        Memoria episodica             │  ← log delle azioni
│  (cosa ho fatto, in che ordine)      │
└──────────────────────────────────────┘
```

**Memoria di lavoro** = il context window. Esiste finché dura la sessione. Massima precisione (è tutta lì), ma costosa e limitata.

**Memoria di lungo termine** = informazioni durevoli salvate fuori, da richiamare quando servono. Il modello non le "ricorda", le **rilegge** ogni volta.

**Memoria episodica** = log delle azioni passate. Utile per debug, per non rifare le stesse cose, per imparare nel tempo.

## 7.2 Gestire il context window

Tutta la conversazione (history + tool result + documenti) sta nel context. Quando si avvicina al limite, succedono cose brutte:

- Il modello "perde" pezzi (effetto **lost-in-the-middle**: dimentica info nel mezzo del prompt).
- Costa caro: ogni token in input si paga, e il prezzo cresce linearmente.
- Latency cresce: più contesto, più tempo per rispondere.

Strategie per gestirlo:

### Compaction / summarization
Quando la storia diventa troppo lunga, si fa un riassunto dei turni più vecchi e si sostituiscono nel contesto.

```
Turno 1-15: [riassunto: l'utente chiedeva X, abbiamo fatto Y, scoperto Z]
Turno 16-20: [contenuto integrale]
```

Claude Code lo fa automaticamente quando si avvicina al limite (vedrai messaggi tipo "auto-compact").

### Sliding window
Tieni solo gli ultimi N turni, scartando i più vecchi. Semplice ma rischia di perdere contesto.

### Pruning intelligente
Il pezzo "tieni il system prompt + il messaggio user + risultati tool ESSENZIALI". Si scartano risultati intermedi voluminosi che non servono più.

### Out-of-context summary
Salva un riassunto in un file e citalo nel system prompt come "stato della conversazione". È quello che fa il sistema "auto memory" usato da molti agenti.

## 7.3 Memoria di lungo termine: il pattern base

Il modello non impara *durante* le conversazioni (no fine-tuning runtime). Per dargli memoria persistente:

1. **Dopo ogni interazione**, salva i fatti rilevanti (preferenze utente, decisioni prese, profili) in un file/DB.
2. **All'inizio della prossima conversazione**, carica quei fatti nel system prompt.

Esempio (semplificato, file-based):

```python
# salva
def save_memory(user_id: str, fact: str):
    with open(f"memory/{user_id}.md", "a") as f:
        f.write(f"- {fact}\n")

# carica
def load_memory(user_id: str) -> str:
    try:
        with open(f"memory/{user_id}.md") as f:
            return f.read()
    except FileNotFoundError:
        return ""

system_prompt = f"""
Sei un assistente personale.
Cosa so dell'utente:
{load_memory(user_id)}
"""
```

Pattern semplice, funziona benissimo per molti casi. ChatGPT e Claude.ai usano varianti di questa idea ("Memory" su ChatGPT, "Project knowledge" su Claude).

## 7.4 Quando il file non basta: i vector store

Se la "memoria" è grande (interi documenti, knowledge base aziendale, repo di codice), non puoi metterla tutta nel system prompt. Serve un meccanismo per **trovare solo le parti rilevanti**.

Qui entrano gli **embedding** e i **vector store**.

### Embedding: numeri che catturano significato
Un **embedding** è un vettore (lista di numeri, di solito 1024-3072 elementi) che rappresenta il significato di un testo. Testi con significato simile hanno embedding vicini nello spazio vettoriale.

```
"Il cane è un mammifero"      → [0.12, -0.45, 0.88, ...]
"I cani sono animali pelosi"  → [0.14, -0.42, 0.85, ...]   ← vicino
"La pizza è italiana"         → [-0.32, 0.71, -0.10, ...]  ← lontano
```

Si producono con un **embedding model**: `text-embedding-3-small` (OpenAI), `voyage-3` (Voyage AI), `cohere-embed-v3` (Cohere), modelli open come `bge-large`.

### Vector store: il database degli embedding
È un DB ottimizzato per cercare i vettori "più simili" a un vettore dato.

Implementazioni popolari: Pinecone, Weaviate, Qdrant, Chroma, pgvector (Postgres extension). Anche file locali con FAISS funzionano per piccoli dataset.

## 7.5 RAG: Retrieval-Augmented Generation

**RAG** è il pattern più comune per dare memoria estesa a un agente.

```
Pipeline RAG:

1. INDICIZZAZIONE (offline, una tantum)
   documenti → chunks (pezzi di 200-500 parole) → embedding → vector store

2. RUNTIME (a ogni domanda)
   domanda utente → embedding → cerca i K chunk più simili nel vector store
   → metti i chunk nel prompt → genera risposta basata sui chunk
```

Esempio concreto: la tua azienda ha 500 documenti di policy interne. Senza RAG dovresti metterli tutti nel prompt (esauribile e costoso). Con RAG:

1. Indicizzi tutti i 500 documenti una volta.
2. Quando un dipendente chiede "qual è la policy per il rimborso viaggi?", il sistema:
   - Trasforma la domanda in embedding.
   - Cerca i 5 chunk più rilevanti nei tuoi documenti.
   - Costruisce un prompt: "Rispondi alla domanda usando solo questi documenti: [chunks]".
   - Il modello risponde citando i documenti.

### Codice RAG minimale (Python, Chroma)

```python
from openai import OpenAI
import chromadb

client = OpenAI()
chroma = chromadb.PersistentClient("./vstore")
coll = chroma.get_or_create_collection("policies")

def embed(text: str) -> list[float]:
    return client.embeddings.create(
        model="text-embedding-3-small", input=text
    ).data[0].embedding

# 1. Indicizzazione (una volta)
docs = [open(f).read() for f in ["policy1.txt", "policy2.txt", ...]]
for i, doc in enumerate(docs):
    coll.add(ids=[f"doc-{i}"], embeddings=[embed(doc)], documents=[doc])

# 2. Query
def answer(question: str) -> str:
    q_emb = embed(question)
    results = coll.query(query_embeddings=[q_emb], n_results=3)
    context = "\n\n".join(results["documents"][0])

    completion = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": f"Rispondi usando solo questi documenti:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return completion.choices[0].message.content

print(answer("Posso farmi rimborsare un Uber?"))
```

Una decina di righe di logica. La complessità sta nel **fare il chunking giusto** e **rifinire la qualità del retrieval**.

## 7.6 RAG fatto bene: chunking, re-ranking, citazioni

### Chunking: come spezzare i documenti
Un documento intero come singolo chunk è troppo (rumore). Un singolo paragrafo come chunk è troppo poco (manca contesto).

Linee guida:
- 200-500 parole per chunk.
- Overlap di 10-20% tra chunk consecutivi (così non spezzi info a metà).
- Rispetta i confini semantici (paragrafo, sezione) quando possibile.
- Aggiungi metadata (titolo doc, sezione, data) per filtraggio successivo.

### Re-ranking
Il primo retrieval (per similarità di embedding) è veloce ma grezzo. Per migliorare, prendi i top-50 e fai un secondo passaggio con un **re-ranker** (modello specializzato come Cohere Rerank o un cross-encoder) che ordina meglio.

### Hybrid search
Combina ricerca per embedding (semantica) con ricerca per parole chiave (BM25/lessicale). I due pescano cose diverse: la semantica vede sinonimi, la lessicale vede nomi propri esatti.

### Citazioni
Il modello deve **citare le fonti**. Pattern:

```
System: Rispondi citando i chunk usati con [doc-N, sezione X].
        Se le info non bastano, dillo invece di inventare.
```

Riduce drasticamente le allucinazioni e dà all'utente un modo per verificare.

## 7.7 RAG vs. context lungo: quando uno, quando l'altro

Con context da 1M token, è davvero ancora utile RAG?

**Sì, in molti casi:**
- Costo: 1M token in input = caro. Caricare solo i chunk rilevanti costa meno.
- Latency: lo stesso.
- Lost-in-the-middle: il modello dimentica pezzi nel mezzo di prompt enormi.
- Aggiornamenti: indicizzazione incrementale è più semplice che mandare tutto a ogni query.

**Solo context (no RAG) va bene quando:**
- Il dataset è piccolo (qualche libro, una settimana di chat).
- Hai bisogno di **vista globale** (es. analisi "a stile" che richiede di leggere tutto).
- Vuoi **massima accuratezza** e i costi non contano (es. consulenza one-shot).

In pratica, molti sistemi reali combinano: RAG per il bulk, context lungo per eccezioni complesse.

## 7.8 Memoria episodica: log strutturato

Per agenti che girano a lungo, salva uno **log delle azioni** che possa essere usato per:

- Debug ("perché ha fatto X?").
- Eviti di rifare le stesse cose ("hai già controllato questa fonte").
- Apprendimento iterativo ("nei task simili a questo, in passato ha funzionato Y").

Schema tipico:

```json
{
  "session_id": "...",
  "step": 7,
  "timestamp": "2026-05-07T10:30:00Z",
  "action": "tool_call",
  "tool": "web_search",
  "input": {"query": "..."},
  "output_summary": "trovati 5 risultati su X",
  "tokens_used": 1234
}
```

Salvali in JSONL o in un DB. Costano poco e risolvono problemi enormi quando un agente "fa una cosa strana".

## 7.9 La memoria come tool

Pattern moderno: invece di gestire la memoria a mano, dai all'agente un **tool `remember(fact)`** e un tool **`recall(query)`**. Decide lui cosa salvare e cosa richiamare.

```python
tools = [
    {
        "name": "remember",
        "description": "Salva un fatto importante per ricordarlo in conversazioni future. Usa per: preferenze utente, decisioni, fatti stabili. Non per dettagli effimeri.",
        ...
    },
    {
        "name": "recall",
        "description": "Cerca fatti precedentemente salvati. Usa quando l'utente fa riferimento a 'come la volta scorsa', 'di solito', o quando ti serve contesto storico.",
        ...
    }
]
```

È esattamente il pattern usato dal sistema "auto memory" di Claude Code.

## 7.10 Pratica: indicizza la guida che stai leggendo

Esercizio: prendi i 16 capitoli di questa guida, fai chunking (paragrafo per paragrafo), embedding, e costruisci un piccolo bot che risponde a domande citando il capitolo.

Te ne accorgerai: il primo prototipo funziona in 100 righe, il fine-tuning della qualità (chunking, re-ranking, prompt di sintesi) è dove sta il vero lavoro.

## 7.11 Da ricordare

- **Tre memorie**: lavoro (context), lungo termine (file/DB/vector), episodica (log).
- **Context window** è prezioso: tienilo pulito, riassumi quando lungo.
- **RAG** = retrieval + generation: trovi i pezzi giusti, li metti nel prompt, generi.
- **Embedding** trasformano significato in vettori; **vector store** li indicizza.
- **Chunking, re-ranking, hybrid search** sono dove si gioca la qualità del RAG.
- **Citazioni** riducono allucinazioni.
- **Memory-as-tool** lascia decidere all'agente cosa salvare.

## 7.12 Errori tipici

- **Mettere tutto in context "tanto c'è 1M".** Costoso, lento, perde attenzione.
- **Chunking ingenuo** (es. ogni frase un chunk): rompe il contesto, retrieval scadente.
- **Solo embedding, niente keyword search.** Perdi nomi propri esatti, codici, sigle.
- **Niente citazioni.** L'utente non può verificare, il modello inventa.
- **RAG senza valutazione.** Misura "quante delle top-K contengono la risposta giusta?" su un dataset di test. Senza, lo migliori al buio.
- **Fine-tuning quando bastava RAG.** Il fine-tuning è caro e fragile; RAG aggiorna in tempo reale.

---

Abbiamo finito la Parte 1 (fondamenti) e la Parte 2 (tecniche). Adesso si scende in pratica: come usare gli agenti già pronti.

→ [Capitolo 8 — Usare i chatbot AI](08-usare-i-chatbot-ai.md)

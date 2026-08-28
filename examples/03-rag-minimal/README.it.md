# 03 — RAG minimale end-to-end

> 🇬🇧 [English version](README.md)

Riferimento: **Capitolo 7** della guida.

## Cosa imparerai

- La pipeline RAG completa in ~150 righe.
- Chunking, indicizzazione, retrieval con cosine similarity, generation con citazioni.
- Come strutturare il prompt per **forzare le citazioni** e **ridurre allucinazioni**.

## ⚠️ Importante: l'embedding qui è fake

Per evitare di forzarti a registrarti su un provider di embedding, l'esempio usa una funzione `fake_embed()` basata su hashing. **Funziona per dimostrare la pipeline, ma NON cattura significato semantico.**

Per usarlo per davvero, sostituisci `fake_embed()` con uno di:

```python
# Voyage AI (consigliato per qualità):
from voyageai import Client
v = Client()
def embed(text):
    return v.embed([text], model="voyage-3", input_type="document").embeddings[0]

# OpenAI (più diffuso):
from openai import OpenAI
o = OpenAI()
def embed(text):
    return o.embeddings.create(model="text-embedding-3-small", input=text).data[0].embedding
```

## Cosa fa

1. **Indicizza** 4 documenti di policy aziendale fittizi (rimborsi, ferie, smartworking, formazione).
2. Per 4 domande, fa retrieval dei 3 chunk più simili e genera risposta con citazioni.

## Esegui

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## Output atteso (con embedding reale)

```
Q: Posso farmi rimborsare un Uber per andare in ufficio?

[retrieved chunks: ['policy-rimborsi', 'policy-rimborsi', 'policy-smartworking']]

Sì, taxi e Uber per spostamenti aziendali sono rimborsabili
[policy-rimborsi#0]. Servono le ricevute originali entro 30 giorni dal viaggio.
```

## Da notare nel codice

- **Chunking** con overlap (40 caratteri) per non spezzare info a metà.
- **Citazioni nel system prompt**: "cita sempre con [doc-id#chunk], se non sai dillo".
- **Top-K = 3** chunks. Più alzi K, più contesto ma più rumore + costo.
- Niente persistenza: ogni run ricostruisce l'indice. In produzione: salva in DB.

## Esercizio per te

1. Sostituisci `fake_embed()` con un vero embedding model.
2. Aggiungi un re-ranker: prendi top-10, poi chiedi a un LLM piccolo di riordinare in base a rilevanza alla domanda.
3. Aggiungi una soglia di confidenza: se il top score è < 0.5, rispondi "non ho info sufficienti" senza chiamare il modello.

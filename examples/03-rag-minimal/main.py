"""
Esempio 03 — RAG minimale end-to-end
Capitolo 7 della guida.

Pipeline completa in ~150 righe:
1. Indicizzazione: documenti → chunk → embedding → DB
2. Runtime: domanda → embedding → top-K chunk → prompt → risposta con citazioni

Usa:
- Voyage AI per embeddings (free tier disponibile, modello specializzato)
- Anthropic Claude per generazione
- DB in-memory (lista) — banale ma sufficiente per dimostrare il concetto.
  In produzione: Chroma / pgvector / Qdrant / Pinecone.

Esegui: python main.py
"""

import math
import os
import re
from anthropic import Anthropic

# In produzione: from voyageai import Client; v = Client(); v.embed(texts, model="voyage-3")
# Qui usiamo un embedding "fake ma onesto": hashing per dimostrare il flusso.
# Sostituisci `embed()` con la chiamata reale al tuo provider di embedding.

EMBED_DIM = 256


def fake_embed(text: str) -> list[float]:
    """Embedding hash-based DETERMINISTICO (non semantico).
    Solo per demo: testi simili NON saranno vicini in questo spazio.
    Sostituisci con un embedding model vero (Voyage, OpenAI, Cohere, BGE).
    """
    text = text.lower()
    vec = [0.0] * EMBED_DIM
    # Bag-of-words hash
    for word in re.findall(r"\w+", text):
        h = hash(word) % EMBED_DIM
        vec[h] += 1.0
    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine_sim(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


# ----- 1. Documenti di partenza -----
DOCS = {
    "policy-rimborsi": (
        "Politica di rimborso viaggi. Sono rimborsabili: voli, treni, hotel "
        "fino a 200€/notte, taxi e Uber per spostamenti aziendali. "
        "Non sono rimborsabili: cene oltre 50€/persona, alcolici, multe, mini-bar. "
        "Soglia di approvazione manageriale: 1500€. Documentazione richiesta: "
        "ricevute originali entro 30 giorni dal viaggio."
    ),
    "policy-ferie": (
        "Politica ferie. 25 giorni l'anno per dipendenti full-time. "
        "Massimo 10 giorni consecutivi salvo approvazione speciale. "
        "Le ferie non godute si possono accumulare fino a 50 giorni. "
        "Richiesta tramite portale HR almeno 2 settimane prima."
    ),
    "policy-smartworking": (
        "Smartworking. Fino a 3 giorni a settimana da remoto. "
        "Lunedì e venerdì spesso da remoto, martedì-giovedì preferibilmente in ufficio "
        "per allineamento di team. Eccezioni con approvazione manager."
    ),
    "policy-formazione": (
        "Budget formazione: 1500€/anno per dipendente. "
        "Conferenze, libri, corsi online. Richiesta preventiva al manager. "
        "Conferenze internazionali: necessaria approvazione direzione."
    ),
}


# ----- 2. Chunking + indicizzazione -----
def chunk_text(text: str, max_chars: int = 200, overlap: int = 40) -> list[str]:
    """Chunking semplice. Per testi reali: splitter Markdown-aware."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def build_index(docs: dict[str, str]) -> list[dict]:
    index = []
    for doc_id, text in docs.items():
        for i, chunk in enumerate(chunk_text(text)):
            index.append({
                "doc_id": doc_id,
                "chunk_id": i,
                "text": chunk,
                "embedding": fake_embed(chunk),
            })
    return index


# ----- 3. Retrieval -----
def retrieve(query: str, index: list[dict], k: int = 3) -> list[dict]:
    q_emb = fake_embed(query)
    scored = [(cosine_sim(q_emb, c["embedding"]), c) for c in index]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]


# ----- 4. Generation con citazioni -----
def answer(client: Anthropic, query: str, index: list[dict]) -> str:
    chunks = retrieve(query, index, k=3)

    context = "\n\n".join(
        f"[{c['doc_id']}#{c['chunk_id']}]\n{c['text']}"
        for c in chunks
    )

    system = (
        "Sei un assistente HR. Rispondi alla domanda usando SOLO i passaggi forniti. "
        "Cita sempre le fonti con il formato [doc-id#chunk]. "
        "Se le info non bastano, dillo chiaramente invece di inventare."
    )

    user_msg = f"DOCUMENTI:\n{context}\n\nDOMANDA: {query}"

    print(f"\n[retrieved chunks: {[c['doc_id'] for c in chunks]}]")

    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return resp.content[0].text


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Errore: imposta ANTHROPIC_API_KEY"); return

    client = Anthropic(api_key=api_key)

    print("Indicizzo i documenti...")
    index = build_index(DOCS)
    print(f"  {len(index)} chunk indicizzati da {len(DOCS)} documenti")

    questions = [
        "Posso farmi rimborsare un Uber per andare in ufficio?",
        "Quanti giorni di ferie ho l'anno?",
        "Posso lavorare da casa il martedì?",
        "Quanto budget ho per i libri tecnici?",
    ]

    for q in questions:
        print(f"\n{'='*60}\nQ: {q}")
        print(f"\n{answer(client, q, index)}")


if __name__ == "__main__":
    main()

# 03 — Minimal end-to-end RAG

Reference: **Chapter 7** of the guide.

> 🇮🇹 [Versione italiana](README.it.md)

## What you'll learn

- The complete RAG pipeline in ~150 lines.
- Chunking, indexing, retrieval with cosine similarity, generation with citations.
- How to structure the prompt to **force citations** and **reduce hallucinations**.

## ⚠️ Important: the embedding here is fake

So you don't have to sign up with an embedding provider just to run this, the example uses a hash-based `fake_embed()` function. **It works for demonstrating the pipeline, but it does NOT capture semantic meaning.**

To use it for real, replace `fake_embed()` with one of these:

```python
# Voyage AI (recommended for quality):
from voyageai import Client
v = Client()
def embed(text):
    return v.embed([text], model="voyage-3", input_type="document").embeddings[0]

# OpenAI (most widespread):
from openai import OpenAI
o = OpenAI()
def embed(text):
    return o.embeddings.create(model="text-embedding-3-small", input=text).data[0].embedding
```

## What it does

1. **Indexes** 4 fictional company policy documents (expenses, holidays, remote work, training).
2. For 4 questions, retrieves the 3 most similar chunks and generates an answer with citations.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## Expected output (with a real embedding model)

The sample corpus and answers are in Italian:

```
Q: Posso farmi rimborsare un Uber per andare in ufficio?
   ("Can I expense an Uber ride to the office?")

[retrieved chunks: ['policy-rimborsi', 'policy-rimborsi', 'policy-smartworking']]

Sì, taxi e Uber per spostamenti aziendali sono rimborsabili
[policy-rimborsi#0]. Servono le ricevute originali entro 30 giorni dal viaggio.
```

## What to notice in the code

- **Chunking** with overlap (40 characters) so information isn't cut in half.
- **Citations in the system prompt**: "always cite with [doc-id#chunk]; if you don't know, say so".
- **Top-K = 3** chunks. The higher K, the more context — but also more noise and more cost.
- No persistence: every run rebuilds the index. In production, store it in a database.

## Exercise for you

1. Replace `fake_embed()` with a real embedding model.
2. Add a re-ranker: take the top 10, then ask a small LLM to reorder them by relevance to the question.
3. Add a confidence threshold: if the top score is < 0.5, answer "I don't have enough information" without calling the model at all.

# 7. Memory, Context and RAG

An agent without memory is like a consultant with amnesia: helps you perfectly for 5 minutes, then forgets who you are. Let's see how to give it memory, and when it makes sense to **bring external information into the context** instead of hoping the model knows it.

## 7.1 The three types of memory

```
┌──────────────────────────────────────┐
│        Working memory                │  ← context window
│  (the ongoing conversation)          │
├──────────────────────────────────────┤
│        Long-term memory              │  ← file / DB / vector store
│  (user preferences, stable facts)    │
├──────────────────────────────────────┤
│        Episodic memory               │  ← action log
│  (what I've done, in what order)     │
└──────────────────────────────────────┘
```

**Working memory** = the context window. Exists only while the session lasts. Maximum precision (it's all there), but expensive and limited.

**Long-term memory** = lasting information saved outside, recalled when needed. The model doesn't "remember" it, it **re-reads** it every time.

**Episodic memory** = log of past actions. Useful for debugging, to avoid repeating the same things, for iterative learning.

## 7.2 Managing the context window

The whole conversation (history + tool results + documents) lives in the context. As it approaches the limit, bad things happen:

- The model "loses" pieces (the **lost-in-the-middle** effect: forgets info in the middle of the prompt).
- It costs a lot: every input token is paid, and price grows linearly.
- Latency grows: more context, more time to respond.

Strategies for handling it:

### Compaction / summarization
When history becomes too long, a summary of older turns is made and replaced in the context.

```
Turns 1-15: [summary: user asked X, we did Y, discovered Z]
Turns 16-20: [full content]
```

Claude Code does it automatically when approaching the limit (you'll see messages like "auto-compact").

### Sliding window
Keep only the last N turns, discarding older ones. Simple but risks losing context.

### Smart pruning
The piece "keep system prompt + user message + ESSENTIAL tool results". Voluminous intermediate results that are no longer needed are discarded.

### Out-of-context summary
Save a summary in a file and cite it in the system prompt as "conversation state." It's what the "auto memory" system used by many agents does.

## 7.3 Long-term memory: the basic pattern

The model doesn't learn *during* conversations (no runtime fine-tuning). To give it persistent memory:

1. **After each interaction**, save relevant facts (user preferences, decisions made, profiles) to a file/DB.
2. **At the start of the next conversation**, load those facts into the system prompt.

Example (simplified, file-based):

```python
# save
def save_memory(user_id: str, fact: str):
    with open(f"memory/{user_id}.md", "a") as f:
        f.write(f"- {fact}\n")

# load
def load_memory(user_id: str) -> str:
    try:
        with open(f"memory/{user_id}.md") as f:
            return f.read()
    except FileNotFoundError:
        return ""

system_prompt = f"""
You are a personal assistant.
What I know about the user:
{load_memory(user_id)}
"""
```

Simple pattern, works great for many cases. ChatGPT and Claude.ai use variants of this idea ("Memory" on ChatGPT, "Project knowledge" on Claude).

## 7.4 When the file isn't enough: vector stores

If the "memory" is large (entire documents, corporate knowledge base, code repo), you can't put it all in the system prompt. You need a mechanism to **find only the relevant parts**.

Here's where **embeddings** and **vector stores** come in.

### Embedding: numbers that capture meaning
An **embedding** is a vector (list of numbers, usually 1024-3072 elements) representing the meaning of a text. Texts with similar meaning have close embeddings in vector space.

```
"The dog is a mammal"             → [0.12, -0.45, 0.88, ...]
"Dogs are furry animals"           → [0.14, -0.42, 0.85, ...]   ← close
"Pizza is Italian"                 → [-0.32, 0.71, -0.10, ...]  ← far
```

Produced by an **embedding model**: `text-embedding-3-small` (OpenAI), `voyage-3` (Voyage AI), `cohere-embed-v3` (Cohere), open models like `bge-large`.

### Vector store: the embedding database
A DB optimized to find vectors "most similar" to a given vector.

Popular implementations: Pinecone, Weaviate, Qdrant, Chroma, pgvector (Postgres extension). Local files with FAISS also work for small datasets.

## 7.5 RAG: Retrieval-Augmented Generation

**RAG** is the most common pattern to give an agent extended memory.

```
RAG pipeline:

1. INDEXING (offline, one-time)
   documents → chunks (200-500 word pieces) → embedding → vector store

2. RUNTIME (per question)
   user question → embedding → search the K most similar chunks in vector store
   → put chunks in prompt → generate response based on chunks
```

Concrete example: your company has 500 internal policy documents. Without RAG you'd have to put them all in the prompt (impossible and expensive). With RAG:

1. Index all 500 documents once.
2. When an employee asks "what's the travel reimbursement policy?", the system:
   - Transforms the question into an embedding.
   - Searches the 5 most relevant chunks in your documents.
   - Builds a prompt: "Reply to the question using only these documents: [chunks]".
   - The model responds citing the documents.

### Minimal RAG code (Python, Chroma)

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

# 1. Indexing (one time)
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
            {"role": "system", "content": f"Reply using only these documents:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return completion.choices[0].message.content

print(answer("Can I expense an Uber?"))
```

A dozen lines of logic. The complexity lies in **doing the right chunking** and **refining retrieval quality**.

## 7.6 RAG done well: chunking, re-ranking, citations

### Chunking: how to split documents
A whole document as a single chunk is too much (noise). A single paragraph as chunk is too little (missing context).

Guidelines:
- 200-500 words per chunk.
- 10-20% overlap between consecutive chunks (so you don't break info in half).
- Respect semantic boundaries (paragraph, section) when possible.
- Add metadata (doc title, section, date) for later filtering.

### Re-ranking
The first retrieval (by embedding similarity) is fast but rough. To improve, take the top-50 and do a second pass with a **re-ranker** (specialized model like Cohere Rerank or a cross-encoder) that orders better.

### Hybrid search
Combine embedding search (semantic) with keyword search (BM25/lexical). The two catch different things: semantic sees synonyms, lexical sees exact proper names.

### Citations
The model must **cite the sources**. Pattern:

```
System: Reply citing the chunks used with [doc-N, section X].
        If info isn't enough, say so instead of inventing.
```

Drastically reduces hallucinations and gives the user a way to verify.

## 7.7 RAG vs. long context: when one, when the other

With a 1M token context, is RAG still useful?

**Yes, in many cases:**
- Cost: 1M token in input = expensive. Loading only relevant chunks costs less.
- Latency: same.
- Lost-in-the-middle: the model forgets pieces in the middle of huge prompts.
- Updates: incremental indexing is simpler than sending everything per query.

**Long context only (no RAG) works when:**
- The dataset is small (some books, a week of chat).
- You need a **global view** (e.g. "stylistic" analysis that requires reading everything).
- You want **maximum accuracy** and costs don't matter (e.g. one-shot consulting).

In practice, many real systems combine: RAG for the bulk, long context for complex exceptions.

## 7.8 Episodic memory: structured log

For long-running agents, save an **action log** that can be used to:

- Debug ("why did it do X?").
- Avoid redoing the same things ("you've already checked this source").
- Iterative learning ("in tasks similar to this, Y worked in the past").

Typical schema:

```json
{
  "session_id": "...",
  "step": 7,
  "timestamp": "2026-05-07T10:30:00Z",
  "action": "tool_call",
  "tool": "web_search",
  "input": {"query": "..."},
  "output_summary": "found 5 results on X",
  "tokens_used": 1234
}
```

Save them as JSONL or in a DB. They cost little and solve big problems when an agent "does something strange."

## 7.9 Memory as a tool

Modern pattern: instead of managing memory by hand, give the agent a **tool `remember(fact)`** and a tool **`recall(query)`**. It decides what to save and what to recall.

```python
tools = [
    {
        "name": "remember",
        "description": "Saves an important fact to remember in future conversations. Use for: user preferences, decisions, stable facts. Not for ephemeral details.",
        ...
    },
    {
        "name": "recall",
        "description": "Searches previously saved facts. Use when the user references 'like last time', 'usually', or when you need historical context.",
        ...
    }
]
```

It's exactly the pattern used by Claude Code's "auto memory" system.

## 7.10 Practice: index this guide you're reading

Exercise: take the 16 chapters of this guide, do chunking (paragraph by paragraph), embedding, and build a small bot that answers questions citing the chapter.

You'll notice: the first prototype works in 100 lines, the fine-tuning of quality (chunking, re-ranking, synthesis prompt) is where the real work lies.

## 7.11 Key takeaways

- **Three memories**: working (context), long-term (file/DB/vector), episodic (log).
- **Context window** is precious: keep it clean, summarize when long.
- **RAG** = retrieval + generation: find the right pieces, put them in the prompt, generate.
- **Embeddings** transform meaning into vectors; **vector stores** index them.
- **Chunking, re-ranking, hybrid search** are where RAG quality is decided.
- **Citations** reduce hallucinations.
- **Memory-as-tool** lets the agent decide what to save.

## 7.12 Common mistakes

- **Putting everything in context "since there's 1M".** Expensive, slow, loses attention.
- **Naive chunking** (e.g. each sentence a chunk): breaks context, poor retrieval.
- **Only embeddings, no keyword search.** You miss exact proper names, codes, acronyms.
- **No citations.** The user can't verify, the model invents.
- **RAG without evaluation.** Measure "how many of the top-K contain the right answer?" on a test dataset. Without it, you improve blindly.
- **Fine-tuning when RAG would have sufficed.** Fine-tuning is expensive and brittle; RAG updates in real time.

---

We've finished Part 1 (fundamentals) and Part 2 (techniques). Now we get practical: how to use ready-made agents.

→ [Chapter 8 — Using AI chatbots](08-usare-i-chatbot-ai.md)

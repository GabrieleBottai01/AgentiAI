# 04 — Production-grade agent with prompt caching

Reference: **Chapter 10** of the guide.

> 🇮🇹 [Versione italiana](README.it.md)

## What you'll learn

- **Prompt caching**: how to mark the system prompt as cacheable and track cache hits.
- **Retry with exponential backoff** on rate limits and 5xx errors.
- **Loop detection** — a minimal guard against a spiral of tool calls.
- Detailed **token / cost / latency tracking** for every run.

## What it does

The research agent:
1. Reads the query (CLI argument, or a default).
2. On every iteration, calls Anthropic with a cacheable `LARGE_SYSTEM` prompt (~6 KB).
3. Uses `web_search` (mock) and `fetch_url` (mock) to simulate research.
4. Produces a brief with citations.
5. Prints metrics: tokens used, cache hits, estimated cost, savings.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# Default query
python main.py

# Your own query
python main.py "What are the 3 main changes in Python 3.13?"
```

## Expected output (excerpt)

The metric labels are in Italian (`Costo stimato` = estimated cost, `Risparmio cache` = cache savings):

```
→ Iter 1
  in: 6342 tok, out: 184 tok
  • web_search({"query": "..."})

→ Iter 2
  in: 198 tok, out: 156 tok, cache_read: 6342     ← cache hit, -90% input cost

=== BRIEF ===
...

--- METRICHE ---
Iterazioni:        3
Cache read (hit):  12684
Costo stimato:     $0.0028
Risparmio cache:   $0.0091   (vs no-cache)
```

## What to notice in the code

- `system=[{"type":"text", "text":..., "cache_control":{"type":"ephemeral"}}]` — that block gets cached.
- Cache reads are billed at ~10% of the input price. On agents with a large system prompt and many iterations, the saving is enormous.
- Cache TTL: 5 minutes, refreshed on every hit.
- `call_with_retry` handles 429 (rate limit), 5xx, and connection errors.

## Exercise for you

1. Change `* 4` to `* 10` on `LARGE_SYSTEM` and compare the cost of the first iteration (cache write) with the following ones (cache read).
2. Replace the mock tools with real ones (e.g. the Tavily API for web search).
3. Add a second level of `cache_control` on the tool definitions so those get cached too.
4. Implement real loop detection with a counter (3 identical consecutive calls → stop).

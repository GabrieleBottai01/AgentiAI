# 04 — Agente production-grade con prompt caching

Riferimento: **Capitolo 10** della guida.

## Cosa imparerai

- **Prompt caching**: come marcare il system prompt come cacheable e tracciare il cache hit.
- **Retry con backoff esponenziale** su rate limit / errori 5xx.
- **Loop detection** — protezione minima contro spirale di tool calls.
- **Token / cost / latency tracking** dettagliato per ogni run.

## Cosa fa

L'agente di research:
1. Legge la query (CLI arg o default).
2. Per ogni iterazione, chiama Anthropic con `LARGE_SYSTEM` cacheable (~6KB).
3. Usa `web_search` (mock) e `fetch_url` (mock) per simulare ricerca.
4. Produce un brief con citazioni.
5. Stampa metriche: token usati, cache hit, costo stimato, risparmio.

## Esegui

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# Default query
python main.py

# Tua query
python main.py "Quali sono i 3 cambiamenti principali in Python 3.13?"
```

## Output atteso (estratto)

```
→ Iter 1
  in: 6342 tok, out: 184 tok
  • web_search({"query": "..."})

→ Iter 2
  in: 198 tok, out: 156 tok, cache_read: 6342     ← cache hit, -90% costo input
  • fetch_url({"url": "..."})

=== BRIEF ===
Anthropic è stata fondata nel 2021 da Dario Amodei e Daniela Amodei [1][2]...

--- METRICHE ---
Iterazioni:        3
Cache read (hit):  12684
Costo stimato:     $0.0028
Risparmio cache:   $0.0091   (vs no-cache)
```

## Da notare nel codice

- `system=[{"type":"text", "text":..., "cache_control":{"type":"ephemeral"}}]` — il blocco viene cachato.
- Cache read viene fatturato a ~10% del prezzo di input. Su agenti con system grandi e molte iterazioni, il risparmio è enorme.
- TTL della cache: 5 minuti. Si rinnova ad ogni hit.
- `call_with_retry` gestisce 429 (rate limit), 5xx, errori di connessione.

## Esercizio per te

1. Aumenta `* 4` a `* 10` su `LARGE_SYSTEM` e osserva il costo della prima iterazione (cache write) e delle successive (cache read).
2. Sostituisci i tool mock con tool reali (Tavily API per web search).
3. Aggiungi un secondo livello di cache_control sui tool definitions per cachare anche quelli.
4. Implementa il loop detection vero con un counter (3 chiamate identiche consecutive → stop).

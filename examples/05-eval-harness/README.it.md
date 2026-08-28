# 05 — Eval harness

> 🇬🇧 [English version](README.md)

Riferimento: **Capitolo 14** della guida.

## Cosa imparerai

- Come strutturare un dataset di eval (`evals.jsonl`).
- Programmatic checks (contains, length, language detection).
- LLM-as-judge per valutazioni qualitative.
- A/B test tra due prompt diversi (`v1` vs `v2`).
- Salvataggio dei run per analisi successiva e regressioni.

## Cosa fa

1. Carica `evals.jsonl` (10 casi di test).
2. Per ogni caso, genera la risposta con il prompt selezionato (`v1` o `v2`).
3. Esegue programmatic checks (contains, max_words, ecc.).
4. (Opzionale) Chiama un LLM-as-judge per qualità su 3 dimensioni (factual / clarity / conciseness).
5. Stampa pass rate, casi falliti, salva tutto in `results-v1.json`.

## Esegui

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# Run baseline
python main.py --prompt v1

# Run alternative + judge
python main.py --prompt v2 --judge

# Confronta i due files results-*.json per A/B
```

## Output atteso

```
Eval con prompt=v1, judge=False, dataset=10 casi
------------------------------------------------------------
 1/10 [✓] easy-math       checks: {'contains': True, 'max_words': True}
 2/10 [✓] easy-fact       checks: {'contains': True, 'max_words': True}
 3/10 [✓] lang-it         checks: {'language_it': True, 'max_words': True}
 4/10 [✗] format          checks: {'contains': False, 'max_words': True}
   ...
------------------------------------------------------------
Pass rate:    80.0%  (8/10)
Latency:      18.4s, 1.8s/case
Salvato: results-v1.json

2 casi falliti:
  - format: Elenca i 3 ingredienti principali della pizza...
    output: La pizza margherita ha pomodoro san marzano…
    checks: {'contains': False, 'max_words': True}
```

## Struttura del dataset

Ogni riga è un JSON con almeno `id` e `input`. Criteri di success opzionali:

| Campo | Significato |
|---|---|
| `expected_contains` | tutte queste keywords devono apparire |
| `expected_not_contains` | nessuna deve apparire |
| `max_words` / `min_words` | vincoli sulla lunghezza |
| `expected_language` | "it" o "en" |

## Esercizio per te

1. Aggiungi 10 casi al dataset, inclusi edge case (input vuoti, lingue diverse, contraddittori).
2. Aggiungi un terzo prompt `v3` e confrontalo con v1/v2 sulle stesse metriche.
3. Implementa una **regression check**: confronta `results-v2.json` con un baseline `baseline.json` e flagga differenze.
4. Aggiungi una metrica di costo (token usati, costo in $) per valutare il tradeoff qualità/prezzo.

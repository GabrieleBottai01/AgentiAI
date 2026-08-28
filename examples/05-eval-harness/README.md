# 05 — Eval harness

Reference: **Chapter 14** of the guide.

> 🇮🇹 [Versione italiana](README.it.md)

## What you'll learn

- How to structure an eval dataset (`evals.jsonl`).
- Programmatic checks (contains, length, language detection).
- LLM-as-judge for qualitative scoring.
- A/B testing between two different prompts (`v1` vs `v2`).
- Saving runs so you can analyse them later and catch regressions.

## What it does

1. Loads `evals.jsonl` (10 test cases).
2. For each case, generates the answer with the selected prompt (`v1` or `v2`).
3. Runs programmatic checks (contains, max_words, …).
4. (Optional) Calls an LLM-as-judge scoring 3 dimensions (factual / clarity / conciseness).
5. Prints the pass rate and failed cases, and saves everything to `results-v1.json`.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# Baseline run
python main.py --prompt v1

# Alternative prompt + judge
python main.py --prompt v2 --judge

# Compare the two results-*.json files for the A/B
```

## Expected output

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
```

(The test cases and console labels are in Italian; the harness itself is language-agnostic.)

## Dataset structure

Each line is a JSON object with at least `id` and `input`. Success criteria are optional:

| Field | Meaning |
|---|---|
| `expected_contains` | all of these keywords must appear |
| `expected_not_contains` | none of these may appear |
| `max_words` / `min_words` | length constraints |
| `expected_language` | `"it"` or `"en"` |

## Exercise for you

1. Add 10 cases to the dataset, including edge cases (empty inputs, other languages, contradictory prompts).
2. Add a third prompt `v3` and compare it against v1/v2 on the same metrics.
3. Implement a **regression check**: compare `results-v2.json` against a `baseline.json` and flag differences.
4. Add a cost metric (tokens used, cost in $) so you can judge the quality/price tradeoff.

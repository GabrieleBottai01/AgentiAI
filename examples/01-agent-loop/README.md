# 01 — The minimal agent loop

Reference: **Chapter 3** of the guide.

> 🇮🇹 [Versione italiana](README.it.md)

## What you'll learn

- The structure of an agent loop (perceive → reason → act → observe → repeat).
- How tools are declared and called.
- How to handle both natural stopping and the iteration limit.

## What it does

The agent is given a goal that requires 2 steps:
1. Find the current time (tool `current_time`).
2. Compute the minutes elapsed since midnight (tool `calculator`).

Every iteration, every tool call and every result is printed to the terminal.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## Expected output

The console labels are in Italian (`Iterazione` = iteration, `RISPOSTA FINALE` = final answer):

```
OBIETTIVO: Quanti minuti sono passati dalla mezzanotte UTC fino ad adesso?…

→ Iterazione 1
  • tool: current_time({})
    → 2026-05-07T14:32:18+00:00

→ Iterazione 2
  • tool: calculator({"expression": "14*60 + 32"})
    → 872

=== RISPOSTA FINALE ===
Sono passati 872 minuti dalla mezzanotte UTC. Il calcolo:
14 ore × 60 minuti = 840, più 32 minuti = 872.
```

## Cost

~$0.001 per run (Haiku model, 2 turns).

## What to notice in the code

- **`stop_reason`** — we distinguish `tool_use` (keep looping) from everything else (exit).
- **Tool schema** — clear description, typed parameters, `required`.
- **Structured tool result** — `{"type": "tool_result", "tool_use_id": ..., "content": ...}`.
- **`max_iterations`** — guards against infinite loops.

## Exercise for you

1. Add a third tool: `convert_currency(amount, from, to)` (a fake one is fine).
2. Change the goal to: "How much is €100 in dollars, and how many hours of your working day does that represent if you earn €50/hour?"
3. Check that the agent calls the tools in the right order.

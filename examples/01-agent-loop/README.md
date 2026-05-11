# 01 — Loop minimale di un agente

Riferimento: **Capitolo 3** della guida.

## Cosa imparerai

- La struttura del loop di un agente (perceive → reason → act → observe → repeat).
- Come si dichiarano e si chiamano i tool.
- Come gestire lo stop naturale e il limite di iterazioni.

## Cosa fa

L'agente riceve un obiettivo che richiede 2 passi:
1. Sapere l'ora corrente (tool `current_time`).
2. Calcolare i minuti dalla mezzanotte (tool `calculator`).

Vedrai stampato a video ogni iterazione, ogni chiamata a tool, ogni risultato.

## Esegui

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## Output atteso

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

## Costo

~€0.001 per esecuzione (modello Haiku, 2 turni).

## Da notare nel codice

- **`stop_reason`** — distinguiamo `tool_use` (continua il loop) da tutto il resto (esci).
- **Schema dei tool** — descrizione chiara, parametri tipizzati, `required`.
- **Tool result strutturato** — `{"type": "tool_result", "tool_use_id": ..., "content": ...}`.
- **`max_iterations`** — protegge da loop infiniti.

## Esercizio per te

1. Aggiungi un terzo tool: `convert_currency(amount, from, to)` (anche fake).
2. Cambia l'obiettivo in: "Quanto costano 100€ in dollari, e quante ore della tua giornata lavorativa rappresentano se guadagni 50€/ora?"
3. Verifica che l'agente chiami i tool nell'ordine giusto.
